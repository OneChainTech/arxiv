# 论文工具API

这是一个基于FastAPI的论文工具API，提供了论文搜索、下载、列表和阅读功能。

## 功能特点

- 论文搜索：支持关键词搜索，可按日期范围和类别筛选
- 论文下载：支持下载指定ID的论文
- 论文列表：查看已下载的论文列表
- 论文阅读：阅读已下载论文的内容

## 安装依赖

使用 uv 安装依赖：

```bash
# 安装 uv（如果尚未安装）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 创建虚拟环境
uv venv

# 激活虚拟环境
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows

# 安装项目依赖
uv pip install -e .
```

## 运行服务

```bash
# 确保虚拟环境已激活
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows

# 运行服务
python -m arxiv_tool.main
```

服务将在 http://localhost:8001 运行

## API接口

### 1. 搜索论文
- 路径：`POST /search`
- 请求体：
```json
{
    "query": "搜索关键词",
    "max_results": 10,
    "date_from": "2023-01-01",
    "date_to": "2023-12-31",
    "categories": ["cs.AI", "cs.CL"]
}
```

### 2. 下载论文
- 路径：`POST /download`
- 请求体：
```json
{
    "paper_id": "论文ID"
}
```

### 3. 获取论文列表
- 路径：`GET /papers`

### 4. 阅读论文
- 路径：`GET /papers/{paper_id}`

## 配置说明

在 `config.py` 文件中可以配置：
- DeepSeek API密钥
- MCP服务器URL

## 注意事项

1. 确保MCP服务器（arxiv-mcp-server）已经启动并运行
2. 默认MCP服务器运行在8000端口
3. 本服务运行在8001端口 

例如，如果你的 FastAPI 应用运行在本地的默认端口（8000），你可以通过以下 URL 访问这些文档：​
博客园

Swagger UI：​http://127.0.0.1:8000/docs

ReDoc：​http://127.0.0.1:8000/redoc

OpenAPI Schema：​http://127.0.0.1:8000/openapi.json​
菜鸟教程