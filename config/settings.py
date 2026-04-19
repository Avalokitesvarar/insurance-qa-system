"""
配置管理模块
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""

    # API配置
    anthropic_api_key: str
    anthropic_base_url: Optional[str] = None
    claude_model: str = "claude-sonnet-4-6"
    temperature: float = 0.3

    # 向量库配置
    chroma_persist_dir: str = "./chroma_db"
    collection_name: str = "insurance_knowledge"
    embedding_model: str = "BAAI/bge-small-zh-v1.5"

    # 检索配置
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k: int = 5

    # 混合检索配置
    use_hybrid_search: bool = True
    bm25_weight: float = 0.3  # BM25权重
    vector_weight: float = 0.7  # 向量检索权重

    # 应用配置
    app_title: str = "保险智能助手"
    app_port: int = 8501

    # 数据路径
    raw_data_dir: str = "./data/raw"
    products_data_dir: str = "./data/products"

    class Config:
        env_file = "config/.env"
        env_file_encoding = "utf-8"


# 全局配置实例
settings = Settings()
