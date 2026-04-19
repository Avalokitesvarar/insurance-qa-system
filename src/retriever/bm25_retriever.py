"""
BM25关键词检索器
用于精确匹配产品名称和关键术语
"""
from typing import List, Dict, Any
from rank_bm25 import BM25Okapi
import jieba
from langchain_core.documents import Document


class BM25Retriever:
    """BM25关键词检索器"""

    def __init__(self, documents: List[Document]):
        """
        初始化BM25检索器

        Args:
            documents: 文档列表
        """
        self.documents = documents
        self.corpus = [doc.page_content for doc in documents]

        # 使用jieba分词
        self.tokenized_corpus = [list(jieba.cut(doc)) for doc in self.corpus]

        # 初始化BM25
        self.bm25 = BM25Okapi(self.tokenized_corpus)

    def search(self, query: str, top_k: int = 5) -> List[Document]:
        """
        BM25检索

        Args:
            query: 查询文本
            top_k: 返回top-k结果

        Returns:
            检索到的文档列表
        """
        # 分词
        tokenized_query = list(jieba.cut(query))

        # 计算BM25分数
        scores = self.bm25.get_scores(tokenized_query)

        # 获取top-k索引
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]

        # 返回文档和分数
        results = []
        for idx in top_indices:
            doc = self.documents[idx]
            doc.metadata["bm25_score"] = float(scores[idx])
            results.append(doc)

        return results

    def add_documents(self, documents: List[Document]):
        """动态添加文档"""
        self.documents.extend(documents)
        new_corpus = [doc.page_content for doc in documents]
        self.corpus.extend(new_corpus)

        # 重新分词
        new_tokenized = [list(jieba.cut(doc)) for doc in new_corpus]
        self.tokenized_corpus.extend(new_tokenized)

        # 重建BM25索引
        self.bm25 = BM25Okapi(self.tokenized_corpus)
