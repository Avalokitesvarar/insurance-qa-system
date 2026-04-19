"""
保险智能体核心模块（重构版）
使用混合检索和工具化对比
"""
import sys
sys.path.append('.')

from typing import List, Dict, Any
from langchain_anthropic import ChatAnthropic
from langchain.chains import RetrievalQA

from config.settings import settings
from src.agent.prompt import (
    get_qa_prompt,
    get_comparison_prompt,
    get_needs_analysis_prompt
)
from src.tools.product_comparator import ProductComparator


class InsuranceAgent:
    """保险智能体"""

    def __init__(self, retriever, use_tools: bool = True):
        """
        初始化智能体

        Args:
            retriever: 检索器（可以是混合检索器）
            use_tools: 是否使用工具化对比
        """
        self.retriever = retriever
        self.use_tools = use_tools

        # 初始化LLM
        self.llm = ChatAnthropic(
            model=settings.claude_model,
            api_key=settings.anthropic_api_key,
            temperature=settings.temperature
        )

        # 初始化工具
        if use_tools:
            self.comparator = ProductComparator(retriever)

        # 问答链
        self.qa_chain = self._create_qa_chain()

    def _create_qa_chain(self):
        """创建问答链"""
        return RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": get_qa_prompt()}
        )

    def ask(self, question: str) -> Dict[str, Any]:
        """
        智能问答

        Args:
            question: 用户问题

        Returns:
            包含答案和来源的字典
        """
        result = self.qa_chain.invoke({"query": question})
        return {
            "answer": result["result"],
            "sources": [
                {
                    "product_name": doc.metadata.get("product_name", ""),
                    "company": doc.metadata.get("company", ""),
                    "score": doc.metadata.get("rrf_score") or doc.metadata.get("bm25_score", 0)
                }
                for doc in result["source_documents"]
            ]
        }

    def compare_products(
        self,
        product_names: List[str],
        dimensions: List[str] = None
    ) -> str:
        """
        产品对比分析

        Args:
            product_names: 产品名称列表
            dimensions: 对比维度

        Returns:
            对比分析结果
        """
        if self.use_tools:
            # 使用工具化对比（结构化）
            comparison_result = self.comparator.compare(product_names, dimensions)

            if "error" in comparison_result:
                return comparison_result["error"]

            # 格式化为LLM输入
            comparison_data = self.comparator.format_for_llm(comparison_result)

            # LLM生成分析
            prompt = get_comparison_prompt().format(comparison_data=comparison_data)
            response = self.llm.invoke(prompt)

            # 返回表格 + 分析
            return f"{comparison_result['comparison_table']}\n\n## 专业分析\n\n{response.content}"

        else:
            # 传统方式：直接让LLM生成
            query = f"对比以下产品：{', '.join(product_names)}"
            docs = self.retriever.get_relevant_documents(query)

            prompt = get_comparison_prompt().format(
                comparison_data=self._format_docs(docs)
            )
            response = self.llm.invoke(prompt)
            return response.content

    def analyze_needs(self, user_profile: Dict[str, Any]) -> str:
        """
        需求分析与产品推荐

        Args:
            user_profile: 用户画像

        Returns:
            分析结果
        """
        # 检索相关产品
        search_query = (
            f"{user_profile.get('age')}岁 "
            f"{user_profile.get('gender')} "
            f"预算{user_profile.get('budget')}"
        )
        docs = self.retriever.get_relevant_documents(search_query)

        # 构建prompt
        prompt = get_needs_analysis_prompt().format(
            age=user_profile.get('age'),
            gender=user_profile.get('gender'),
            occupation=user_profile.get('occupation'),
            family_status=user_profile.get('family_status'),
            budget=user_profile.get('budget'),
            existing_coverage=user_profile.get('existing_coverage', '无'),
            available_products=self._format_docs(docs)
        )

        response = self.llm.invoke(prompt)
        return response.content

    def _format_docs(self, docs) -> str:
        """格式化文档"""
        return "\n\n---\n\n".join([doc.page_content for doc in docs])
