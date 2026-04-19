"""
保险智能问答系统
支持多数据库查询和智能回答
"""
import sys
sys.path.append('.')

from src.retriever.vector_store import VectorStoreManager
from src.retriever.hybrid_search import HybridSearchRetriever
from src.retriever.bm25_retriever import BM25Retriever
import chromadb
from anthropic import Anthropic
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv("config/.env")

class InsuranceQASystem:
    """保险智能问答系统"""

    def __init__(self, api_key: str = None):
        """初始化问答系统"""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.base_url = os.getenv("ANTHROPIC_BASE_URL")

        if not self.api_key or self.api_key == "sk-placeholder":
            print("[警告] 未配置有效的ANTHROPIC_API_KEY，将只返回检索结果")
            self.client = None
        else:
            # 使用自定义base_url
            if self.base_url:
                self.client = Anthropic(api_key=self.api_key, base_url=self.base_url)
            else:
                self.client = Anthropic(api_key=self.api_key)

        # 初始化数据库
        self.databases = {
            "articles": {
                "name": "公众号文章库",
                "path": "D:/保险数据库/公众号文章库",
                "collection": "insurance_articles",
                "vm": None
            },
            "materials": {
                "name": "产品资料库",
                "path": "D:/保险数据库/产品资料库",
                "collection": "insurance_materials",
                "vm": None
            }
        }

        print("正在初始化知识库...")
        self._init_databases()
        print("知识库初始化完成！\n")

    def _init_databases(self):
        """初始化所有数据库"""
        for db_key, config in self.databases.items():
            vm = VectorStoreManager()
            vm.persist_dir = config["path"]
            vm.collection_name = config["collection"]
            vm.client = chromadb.PersistentClient(path=vm.persist_dir)
            vm.init_vectorstore()
            config["vm"] = vm

    def search(self, query: str, db_keys: list = None, top_k: int = 5):
        """
        搜索知识库

        Args:
            query: 查询问题
            db_keys: 要搜索的数据库列表，默认搜索所有
            top_k: 返回结果数量

        Returns:
            检索结果列表
        """
        if db_keys is None:
            db_keys = list(self.databases.keys())

        all_results = []

        for db_key in db_keys:
            if db_key not in self.databases:
                continue

            config = self.databases[db_key]
            vm = config["vm"]

            # 执行检索
            results = vm.similarity_search(query, k=top_k)

            # 添加数据库来源信息
            for doc in results:
                doc.metadata["db_source"] = config["name"]
                all_results.append(doc)

        return all_results

    def ask(self, question: str, db_keys: list = None, top_k: int = 5):
        """
        智能问答

        Args:
            question: 用户问题
            db_keys: 搜索的数据库
            top_k: 检索文档数量

        Returns:
            回答文本
        """
        print(f"\n[问题] {question}\n")
        print("[检索中...]")

        # 1. 检索相关文档
        results = self.search(question, db_keys, top_k)

        if not results:
            return "抱歉，没有找到相关信息。"

        print(f"[找到 {len(results)} 条相关信息]\n")

        # 2. 如果没有API密钥，只返回检索结果
        if not self.client:
            return self._format_search_results(results)

        # 3. 构建上下文
        context = self._build_context(results)

        # 4. 调用Claude生成回答
        print("[生成回答中...]\n")
        answer = self._generate_answer(question, context)

        return answer

    def _build_context(self, results):
        """构建上下文"""
        context_parts = []

        for i, doc in enumerate(results, 1):
            source = doc.metadata.get("db_source", "未知")
            title = doc.metadata.get("title", "未知")
            content = doc.page_content[:500]  # 限制长度

            context_parts.append(
                f"[文档{i}] 来源:{source} | 标题:{title}\n{content}\n"
            )

        return "\n".join(context_parts)

    def _generate_answer(self, question: str, context: str):
        """使用Claude生成回答"""
        prompt = f"""你是一个专业的保险经纪人助手。请根据以下知识库内容回答用户的问题。

知识库内容：
{context}

用户问题：{question}

请提供专业、准确的回答。如果知识库中没有足够信息，请如实说明。回答要点：
1. 直接回答问题
2. 引用具体产品名称和数据
3. 给出实用建议
4. 保持专业和友好的语气

回答："""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            return response.content[0].text

        except Exception as e:
            print(f"[错误] Claude API调用失败: {e}")
            return self._format_search_results(results)

    def _format_search_results(self, results):
        """格式化检索结果（无API时使用）"""
        output = ["[检索结果]\n"]

        for i, doc in enumerate(results, 1):
            source = doc.metadata.get("db_source", "未知")
            title = doc.metadata.get("title", "未知")
            # 移除emoji和特殊字符
            content = doc.page_content[:300].encode('gbk', errors='ignore').decode('gbk', errors='ignore')

            output.append(f"{i}. [{source}] {title}")
            output.append(f"   {content}...\n")

        return "\n".join(output)


def main():
    """交互式问答"""
    print("="*60)
    print("保险智能问答系统")
    print("="*60)

    # 初始化系统
    qa = InsuranceQASystem()

    # 测试问题
    test_questions = [
        "4月医疗险榜单有哪些产品推荐？",
        "重疾险哪个产品性价比高？",
        "乳腺癌保险理赔需要注意什么？"
    ]

    for question in test_questions:
        answer = qa.ask(question, top_k=3)
        print(f"[回答]\n{answer}\n")
        print("="*60)

    # 交互模式
    print("\n进入交互模式（输入 'quit' 退出）\n")

    while True:
        try:
            question = input("\n请输入问题: ").strip()

            if question.lower() in ['quit', 'exit', 'q']:
                print("再见！")
                break

            if not question:
                continue

            answer = qa.ask(question, top_k=3)
            print(f"\n[回答]\n{answer}\n")
            print("-"*60)

        except KeyboardInterrupt:
            print("\n\n再见！")
            break
        except Exception as e:
            print(f"\n[错误] {e}\n")


if __name__ == "__main__":
    main()
