"""
向量数据库管理模块
"""
import os
from typing import List, Dict, Any
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import chromadb
from dotenv import load_dotenv

load_dotenv("config/.env")


class VectorStoreManager:
    """向量库管理器"""

    def __init__(
        self,
        persist_dir: str = None,
        collection_name: str = None,
        embedding_model: str = "BAAI/bge-small-zh-v1.5"
    ):
        self.persist_dir = persist_dir or os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
        self.collection_name = collection_name or os.getenv("COLLECTION_NAME", "insurance_knowledge")

        # 使用中文优化的嵌入模型
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )

        # 初始化Chroma客户端
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        self.vectorstore = None

    def init_vectorstore(self):
        """初始化向量库"""
        self.vectorstore = Chroma(
            client=self.client,
            collection_name=self.collection_name,
            embedding_function=self.embeddings
        )
        return self.vectorstore

    def add_documents(self, documents: List[Document], metadata_list: List[Dict] = None):
        """添加文档到向量库"""
        if not self.vectorstore:
            self.init_vectorstore()

        # 文档分块
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=int(os.getenv("CHUNK_SIZE", 500)),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", 50)),
            separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""]
        )

        split_docs = text_splitter.split_documents(documents)

        # 添加到向量库
        self.vectorstore.add_documents(split_docs)
        print(f"✓ 已添加 {len(split_docs)} 个文档块")

    def add_products(self, products: List[Dict[str, Any]]):
        """添加产品数据"""
        documents = []
        for product in products:
            # 构建产品文档内容
            content = self._format_product_content(product)
            doc = Document(
                page_content=content,
                metadata={
                    "type": "product",
                    "product_id": product.get("product_id"),
                    "product_name": product.get("name"),
                    "company": product.get("company"),
                    "product_type": product.get("product_type")
                }
            )
            documents.append(doc)

        self.add_documents(documents)

    def _format_product_content(self, product: Dict) -> str:
        """格式化产品内容为文本"""
        content_parts = [
            f"产品名称：{product.get('name')}",
            f"保险公司：{product.get('company')}",
            f"产品类型：{product.get('product_type')}",
        ]

        # 保障项
        if coverages := product.get('coverages'):
            content_parts.append("\n保障内容：")
            for cov in coverages:
                content_parts.append(f"- {cov.get('name')}：{cov.get('amount')} {cov.get('description', '')}")

        # 产品特色
        if features := product.get('features'):
            content_parts.append("\n产品特色：" + "、".join(features))

        # 责任免除
        if exclusions := product.get('exclusions'):
            content_parts.append("\n责任免除：" + "、".join(exclusions))

        return "\n".join(content_parts)

    def similarity_search(self, query: str, k: int = 5, filter_dict: Dict = None):
        """相似度搜索"""
        if not self.vectorstore:
            self.init_vectorstore()

        return self.vectorstore.similarity_search(
            query,
            k=k,
            filter=filter_dict
        )

    def get_retriever(self, search_kwargs: Dict = None):
        """获取检索器"""
        if not self.vectorstore:
            self.init_vectorstore()

        search_kwargs = search_kwargs or {"k": int(os.getenv("TOP_K", 5))}
        return self.vectorstore.as_retriever(search_kwargs=search_kwargs)
