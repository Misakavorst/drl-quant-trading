"""Application configuration"""
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""
    
    # SSH Tunnel Config
    ssh_host: str = Field(default="kv.run", env="SSH_HOST")
    ssh_port: int = Field(default=10022, env="SSH_PORT")
    ssh_user: str = Field(default="finai", env="SSH_USER")
    ssh_password: str = Field(default="fin2025ai", env="SSH_PASSWORD")
    
    # Database Config
    db_user: str = Field(default="postgres", env="DB_USER")
    db_password: str = Field(default="MLsys2024", env="DB_PASSWORD")
    db_name: str = Field(default="fin_ai_world_model_v2", env="DB_NAME")
    db_host: str = Field(default="localhost", env="DB_HOST")
    db_port: int = Field(default=5432, env="DB_PORT")
    
    # App Config
    api_prefix: str = Field(default="/api", env="API_PREFIX")
    output_dir: str = Field(default="./outputs", env="OUTPUT_DIR")
    
    # Training defaults
    train_test_split: float = 0.8
    initial_amount: float = 1e6
    max_stock: int = 100
    transaction_cost_pct: float = 0.001
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

