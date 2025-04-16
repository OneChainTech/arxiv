from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DEEPSEEK_API_KEY: str = "sk-5b382aebfee0438699d977ee4f38ccdb"
    MCP_SERVER_URL: str = "http://localhost:8000"  # 假设MCP服务器运行在本地8000端口
    
    class Config:
        env_file = ".env"

settings = Settings() 