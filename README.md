# arXiv 论文工具

一个基于FastAPI的arXiv论文搜索、下载和阅读工具。

## 功能特点

- 论文搜索：支持关键词搜索，可按日期范围和类别筛选
- 论文下载：支持下载指定ID的论文
- 论文列表：查看已下载的论文列表
- 论文阅读：阅读已下载论文的内容

## 安装

### 从源码安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/arxiv-tool.git
cd arxiv-tool

# 安装依赖
uv pip install -e .
```

### 从PyPI安装

```bash
uv pip install arxiv-tool
```

## 使用方法

1. 启动服务：

```bash
python -m arxiv_tool.main
```

2. 打开浏览器访问：http://localhost:8001

## 开发

### 构建项目

```bash
# 构建源码分发包和wheel包
uv pip install build
python -m build
```

生成的包文件将在 `dist` 目录下。

### 运行测试

```bash
uv pip install pytest
pytest
```

## 配置说明

在 `config.py` 文件中可以配置：
- MCP服务器参数
- 存储路径等

## 许可证

MIT License

## 注意事项

1. 确保MCP服务器（arxiv-mcp-server）已经启动并运行
2. 默认MCP服务器运行在8000端口
3. 本服务运行在8001端口 

## 服务文档

Swagger UI：​http://127.0.0.1:8000/docs

ReDoc：​http://127.0.0.1:8000/redoc

OpenAPI Schema：​http://127.0.0.1:8000/openapi.json​


# 从amap_client.py中的实现
- 使用URL连接：`AMAP_MCP_URL = "https://mcp-e7501f2d-826a-4be5.api-inference.modelscope.cn/sse"`
- 通过`sse_client`建立连接：
  ```python
  self._streams_context = sse_client(url=self.server_url)
  streams = await self._streams_context.__aenter__()
  ```
- 适用于远程服务调用
- 基于HTTP长连接，支持服务器推送事件到客户端

2. STDIO方式：
```python
# 从arxiv_tool/main.py中的实现
- 使用本地进程通信：
  ```python
  server_params = StdioServerParameters(
      command="uv",
      args=["tool", "run", "arxiv-mcp-server", "--storage-path", "/Users/zhenghong/Documents/work/mcp/arxiv"],
      env=None,
  )
  ```
- 通过`stdio_client`建立连接：
  ```python
  async with stdio_client(server_params) as (read, write):
  ```
- 适用于本地服务调用
- 基于标准输入输出流通信

主要区别：

1. 连接方式：
   - SSE：通过HTTP连接远程服务
   - STDIO：通过进程间通信连接本地服务

2. 使用场景：
   - SSE：适合调用云端API服务，如高德地图API
   - STDIO：适合本地工具集成，如论文下载工具

3. 通信机制：
   - SSE：支持服务器实时推送，适合流式数据传输
   - STDIO：基于进程标准输入输出，适合本地命令行工具集成

4. 配置差异：
   - SSE：需要远程服务URL
   - STDIO：需要本地命令和参数配置

总的来说，这两种方式各有特点，选择哪种方式主要取决于你的使用场景：
- 如果是调用远程服务，选择SSE方式
- 如果是集成本地工具，选择STDIO方式
