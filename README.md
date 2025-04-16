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
