"""
向量检索模块（重构版）
"""
import os
from typing import List, Dict, Any
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import chromadb

import sys
sys.path.append('.')
from config.settings import settings


class VectorStoreManager:
    """向量库管理器"""

    def __init__(self):
        self.persist_dir = settings.chroma_persist_dir
        self.collection_name = settings.collection_name

        # 使用ModelScope下载的本地模型
        model_path = "C:/Users/jren3/.cache/modelscope/AI-ModelScope/bge-small-zh-v1___5"
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_path,
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

    def add_documents(self, documents: List[Document]):
        """添加文档到向量库"""
        if not self.vectorstore:
            self.init_vectorstore()

        # 文档分块
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""]
        )

        split_docs = text_splitter.split_documents(documents)

        # 添加到向量库
        self.vectorstore.add_documents(split_docs)
        print(f"[+] 已添加 {len(split_docs)} 个文档块")

        return split_docs  # 返回分块后的文档，供BM25使用

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

        return self.add_documents(documents)

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

    def similarity_search(self, query: str, k: int = None, filter_dict: Dict = None):
        """相似度搜索"""
        if not self.vectorstore:
            self.init_vectorstore()

        k = k or settings.top_k

        return self.vectorstore.similarity_search(
            query,
            k=k,
            filter=filter_dict
        )

    def get_retriever(self, search_kwargs: Dict = None):
        """获取检索器"""
        if not self.vectorstore:
            self.init_vectorstore()

        search_kwargs = search_kwargs or {"k": settings.top_k}
        return self.vectorstore.as_retriever(search_kwargs=search_kwargs)

    def get_all_documents(self) -> List[Document]:
        """获取所有文档（用于初始化BM25）"""
        if not self.vectorstore:
            self.init_vectorstore()

        # 从Chroma获取所有文档
        collection = self.client.get_collection(self.collection_name)
        results = collection.get()

        documents = []
        for i in range(len(results['ids'])):
            doc = Document(
                page_content=results['documents'][i],
                metadata=results['metadatas'][i] if results['metadatas'] else {}
            )
            documents.append(doc)

        return documents
