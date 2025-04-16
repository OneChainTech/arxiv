from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, validator
from typing import List, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import os
from datetime import datetime

app = FastAPI(title="论文工具API")

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建MCP服务器参数
server_params = StdioServerParameters(
    command="uv",
    args=["tool", "run", "arxiv-mcp-server", "--storage-path", "/Users/zhenghong/Documents/work/mcp/arxiv"],
    env=None,
)

@app.get("/")
async def read_root():
    return FileResponse("static/index.html")

class SearchQuery(BaseModel):
    query: str
    max_results: Optional[int] = 10
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    categories: Optional[List[str]] = None

    @validator('date_from', 'date_to')
    def validate_date(cls, v):
        if v is not None:
            try:
                datetime.strptime(v, '%Y-%m-%d')
            except ValueError:
                raise ValueError('日期格式必须是 YYYY-MM-DD')
        return v

class PaperDownload(BaseModel):
    paper_id: str

@app.post("/search")
async def search_papers(query: SearchQuery):
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool("search_papers", {
                    "query": query.query,
                    "max_results": query.max_results,
                    "date_from": query.date_from,
                    "date_to": query.date_to,
                    "categories": query.categories
                })
                return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/download")
async def download_paper(paper: PaperDownload):
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool("download_paper", {
                    "paper_id": paper.paper_id
                })
                return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/papers")
async def list_papers():
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool("list_papers", {})
                return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/papers/{paper_id}")
async def read_paper(paper_id: str):
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool("read_paper", {
                    "paper_id": paper_id
                })
                return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 