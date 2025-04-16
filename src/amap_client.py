from typing import Optional, List, Dict, Any
import json
import os
from contextlib import AsyncExitStack
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from openai import OpenAI
from mcp import ClientSession
from mcp.client.sse import sse_client
from contextlib import asynccontextmanager

# 配置
AMAP_MCP_URL = "https://mcp-e7501f2d-826a-4be5.api-inference.modelscope.cn/sse"
DEEPSEEK_API_KEY = "sk-5b382aebfee0438699d977ee4f38ccdb"

class MCPClient:
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.session: Optional[ClientSession] = None
        self._streams_context = None
        self._session_context = None
        
    async def connect(self) -> None:
        """连接到MCP服务器"""
        self._streams_context = sse_client(url=self.server_url)
        streams = await self._streams_context.__aenter__()
        self._session_context = ClientSession(*streams)
        self.session = await self._session_context.__aenter__()
        await self.session.initialize()
        
    async def cleanup(self) -> None:
        """清理连接"""
        if self._session_context:
            await self._session_context.__aexit__(None, None, None)
        if self._streams_context:
            await self._streams_context.__aexit__(None, None, None)
            
    async def list_tools(self) -> List[Dict[str, Any]]:
        """获取可用工具列表"""
        if not self.session:
            raise RuntimeError("未连接到MCP服务器")
            
        response = await self.session.list_tools()
        tools = response.tools
        
        formatted_tools = []
        for tool in tools:
            # 构建参数属性
            properties = {}
            for param_name, param_info in tool.inputSchema["properties"].items():
                param_data = {
                    "type": param_info["type"],
                    "description": param_info.get("description", param_name)
                }
                if param_info["type"] == "array" and "items" in param_info:
                    param_data["items"] = {
                        "type": param_info["items"]["type"]
                    }
                properties[param_name] = param_data
                
            tool_dict = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": {
                        "type": "object",
                        "properties": properties,
                        "required": tool.inputSchema.get("required", [])
                    }
                }
            }
            formatted_tools.append(tool_dict)
            
        return formatted_tools
        
    async def call_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
        """调用指定的工具"""
        if not self.session:
            raise RuntimeError("未连接到MCP服务器")
            
        try:
            response = await self.session.call_tool(tool_name, tool_args)
            
            if response.isError:
                error_message = response.content[0].text if response.content else "未知错误"
                return {
                    "status": "error",
                    "message": "工具执行出错",
                    "details": error_message
                }
            
            result = response.content[0].text if response.content else ""
            return {
                "status": "success",
                "result": result
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": "工具调用异常",
                "details": str(e)
            }

class AIAssistant:
    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com/v1"):
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key,
        )
        self.model = "deepseek-chat"
        
    async def chat(self, 
                  messages: List[Dict[str, str]], 
                  tools: List[Dict[str, Any]], 
                  mcp_client: MCPClient) -> Dict[str, Any]:
        """处理用户消息并返回响应"""
        try:
            # 第一次调用获取意图
            response_1 = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools
            )
            
            # 如果需要调用工具
            if response_1.choices[0].message.tool_calls:
                # 处理工具调用
                tool_results = []
                for tool_call in response_1.choices[0].message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)  # 使用json.loads替代eval
                    
                    print(f"调用工具: {tool_name}, 参数: {tool_args}")  # 调试日志
                    
                    # 调用MCP工具
                    result = await mcp_client.call_tool(
                        tool_name=tool_name,
                        tool_args=tool_args
                    )
                    
                    print(f"工具返回结果: {result}")  # 调试日志
                    
                    tool_results.append({
                        "tool_call_id": tool_call.id,
                        "name": tool_name,
                        "result": result["result"] if result["status"] == "success" else result["message"]
                    })
                
                # 添加工具调用结果到消息历史
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": result["tool_call_id"],
                            "type": "function",
                            "function": {
                                "name": result["name"],
                                "arguments": json.dumps(result["result"], ensure_ascii=False)
                            }
                        } for result in tool_results
                    ]
                })
                
                # 添加工具响应到消息历史
                for result in tool_results:
                    messages.append({
                        "role": "tool",
                        "tool_call_id": result["tool_call_id"],
                        "name": result["name"],
                        "content": str(result["result"])
                    })
                
                # 第二次调用获取最终响应
                response_2 = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=tools
                )
                
                final_response = response_2.choices[0].message.content
            else:
                # 如果不需要工具调用，直接使用第一次响应
                final_response = response_1.choices[0].message.content
                messages.append({
                    "role": "assistant",
                    "content": final_response
                })
            
            return {
                "status": "success",
                "response": final_response,
                "messages": messages
            }
            
        except Exception as e:
            import traceback
            print(f"Chat error: {str(e)}")
            print(traceback.format_exc())  # 打印完整错误堆栈
            return {
                "status": "error",
                "message": str(e),
                "messages": messages
            }

# FastAPI应用
app = FastAPI(title="高德地图AI助手API")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建MCP客户端和AI助手实例
mcp_client = MCPClient(AMAP_MCP_URL)
ai_assistant = AIAssistant(DEEPSEEK_API_KEY)

class ChatRequest(BaseModel):
    messages: List[Dict[str, str]]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时连接到MCP服务器
    await mcp_client.connect()
    yield
    # 关闭时清理连接
    await mcp_client.cleanup()

app = FastAPI(title="高德地图AI助手API", lifespan=lifespan)

@app.get("/amap")
async def read_root():
    """返回前端页面"""
    return FileResponse("static/amap/chat.html")

@app.post("/amap/chat")
async def chat(request: ChatRequest):
    """处理用户消息"""
    try:
        # 获取可用工具
        tools = await mcp_client.list_tools()
        
        # 调用AI助手处理消息
        result = await ai_assistant.chat(
            messages=request.messages,
            tools=tools,
            mcp_client=mcp_client
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 