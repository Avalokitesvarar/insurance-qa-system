"""
混合检索模块
结合向量检索和BM25关键词检索，使用RRF算法融合结果
"""
from typing import List, Dict, Any
from langchain_core.documents import Document
from collections import defaultdict


class HybridSearchRetriever:
    """混合检索器 - 融合向量检索和BM25"""

    def __init__(
        self,
        vector_retriever,
        bm25_retriever,
        vector_weight: float = 0.7,
        bm25_weight: float = 0.3,
        k: int = 60  # RRF参数
    ):
        """
        初始化混合检索器

        Args:
            vector_retriever: 向量检索器
            bm25_retriever: BM25检索器
            vector_weight: 向量检索权重
            bm25_weight: BM25权重
            k: RRF算法的k参数（通常设为60）
        """
        self.vector_retriever = vector_retriever
        self.bm25_retriever = bm25_retriever
        self.vector_weight = vector_weight
        self.bm25_weight = bm25_weight
        self.k = k

    def search(self, query: str, top_k: int = 5) -> List[Document]:
        """
        混合检索

        Args:
            query: 查询文本
            top_k: 返回top-k结果

        Returns:
            融合后的文档列表
        """
        # 1. 向量检索
        vector_docs = self.vector_retriever.get_relevant_documents(query)

        # 2. BM25检索
        bm25_docs = self.bm25_retriever.search(query, top_k=top_k * 2)

        # 3. RRF融合
        fused_docs = self._reciprocal_rank_fusion(
            vector_docs,
            bm25_docs,
            top_k
        )

        return fused_docs

    def _reciprocal_rank_fusion(
        self,
        vector_docs: List[Document],
        bm25_docs: List[Document],
        top_k: int
    ) -> List[Document]:
        """
        倒数排名融合（Reciprocal Rank Fusion）

        RRF公式: score(d) = Σ 1/(k + rank(d))
        其中k通常设为60，rank是文档在各检索结果中的排名

        Args:
            vector_docs: 向量检索结果
            bm25_docs: BM25检索结果
            top_k: 返回数量

        Returns:
            融合后的文档列表
        """
        # 文档ID到文档对象的映射
        doc_map = {}
        # 文档ID到RRF分数的映射
        rrf_scores = defaultdict(float)

        # 处理向量检索结果
        for rank, doc in enumerate(vector_docs, start=1):
            doc_id = self._get_doc_id(doc)
            doc_map[doc_id] = doc
            # 向量检索的RRF分数
            rrf_scores[doc_id] += self.vector_weight * (1.0 / (self.k + rank))

        # 处理BM25检索结果
        for rank, doc in enumerate(bm25_docs, start=1):
            doc_id = self._get_doc_id(doc)
            if doc_id not in doc_map:
                doc_map[doc_id] = doc
            # BM25的RRF分数
            rrf_scores[doc_id] += self.bm25_weight * (1.0 / (self.k + rank))

        # 按RRF分数排序
        sorted_doc_ids = sorted(
            rrf_scores.keys(),
            key=lambda x: rrf_scores[x],
            reverse=True
        )[:top_k]

        # 构建结果
        results = []
        for doc_id in sorted_doc_ids:
            doc = doc_map[doc_id]
            doc.metadata["rrf_score"] = rrf_scores[doc_id]
            results.append(doc)

        return results

    def _get_doc_id(self, doc: Document) -> str:
        """
        生成文档唯一ID

        优先使用metadata中的product_id，否则使用内容hash
        """
        if "product_id" in doc.metadata:
            return doc.metadata["product_id"]
        elif "article_id" in doc.metadata:
            return doc.metadata["article_id"]
        else:
            # 使用内容的hash作为ID
            return str(hash(doc.page_content))

    def get_relevant_documents(self, query: str) -> List[Document]:
        """兼容LangChain的接口"""
        return self.search(query)
