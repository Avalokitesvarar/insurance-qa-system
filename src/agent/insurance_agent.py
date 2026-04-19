"""
保险智能体核心模块
"""
import os
from typing import List, Dict, Any
from langchain_anthropic import ChatAnthropic
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv("config/.env")


class InsuranceAgent:
    """保险智能体"""

    def __init__(self, retriever):
        self.retriever = retriever
        self.llm = ChatAnthropic(
            model=os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6"),
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=0.3
        )

        # 问答链
        self.qa_chain = self._create_qa_chain()

    def _create_qa_chain(self):
        """创建问答链"""
        prompt_template = """你是一位专业的保险经纪人，请基于以下保险产品信息回答用户问题。

相关产品信息：
{context}

用户问题：{question}

请提供专业、客观的建议，包括：
1. 直接回答用户问题
2. 如果涉及产品推荐，说明推荐理由
3. 提醒用户注意事项（如等待期、免责条款等）

回答："""

        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )

        return RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": PROMPT}
        )

    def ask(self, question: str) -> Dict[str, Any]:
        """智能问答"""
        result = self.qa_chain.invoke({"query": question})
        return {
            "answer": result["result"],
            "sources": [doc.metadata for doc in result["source_documents"]]
        }

    def compare_products(self, product_names: List[str], dimensions: List[str] = None) -> str:
        """产品对比分析"""
        # 检索相关产品
        query = f"对比以下产品：{', '.join(product_names)}"
        docs = self.retriever.get_relevant_documents(query)

        # 构建对比prompt
        dimensions = dimensions or ["保障内容", "保费", "产品特色", "责任免除"]

        compare_prompt = f"""请对比分析以下保险产品，从这些维度进行对比：{', '.join(dimensions)}

产品信息：
{self._format_docs(docs)}

请生成一个清晰的对比表格，并给出选择建议。"""

        response = self.llm.invoke(compare_prompt)
        return response.content

    def _format_docs(self, docs) -> str:
        """格式化文档"""
        return "\n\n---\n\n".join([doc.page_content for doc in docs])

    def analyze_needs(self, user_profile: Dict[str, Any]) -> str:
        """需求分析与产品推荐"""
        prompt = f"""基于以下客户信息，分析保险需求并推荐合适的产品：

客户信息：
- 年龄：{user_profile.get('age')}岁
- 性别：{user_profile.get('gender')}
- 职业：{user_profile.get('occupation')}
- 家庭状况：{user_profile.get('family_status')}
- 预算：{user_profile.get('budget')}元/年
- 已有保障：{user_profile.get('existing_coverage', '无')}

请提供：
1. 保障缺口分析
2. 推荐产品类型及优先级
3. 具体产品推荐（从知识库中检索）
4. 配置方案和预算分配
"""

        # 先检索相关产品
        search_query = f"{user_profile.get('age')}岁 {user_profile.get('gender')} 预算{user_profile.get('budget')}"
        docs = self.retriever.get_relevant_documents(search_query)

        full_prompt = prompt + f"\n\n可选产品：\n{self._format_docs(docs)}"
        response = self.llm.invoke(full_prompt)
        return response.content
