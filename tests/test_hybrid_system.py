"""
测试混合检索和工具化对比
"""
import sys
sys.path.append('.')

from src.retriever.vector_store import VectorStoreManager
from src.retriever.bm25_retriever import BM25Retriever
from src.retriever.hybrid_search import HybridSearchRetriever
from src.agent.insurance_agent_v2 import InsuranceAgent
from config.settings import settings


def test_hybrid_search():
    """测试混合检索"""
    print("=" * 60)
    print("测试 1: 混合检索 vs 纯向量检索")
    print("=" * 60)

    vm = VectorStoreManager()
    vm.init_vectorstore()

    # 获取所有文档
    all_docs = vm.get_all_documents()
    print(f"\n数据库中共有 {len(all_docs)} 个文档块")

    # 初始化检索器
    vector_retriever = vm.get_retriever()
    bm25_retriever = BM25Retriever(all_docs)
    hybrid_retriever = HybridSearchRetriever(
        vector_retriever=vector_retriever,
        bm25_retriever=bm25_retriever,
        vector_weight=settings.vector_weight,
        bm25_weight=settings.bm25_weight
    )

    # 测试查询
    test_queries = [
        "超级玛丽9号",  # 精确产品名
        "30岁男性重疾险",  # 语义查询
        "少儿保险"  # 类别查询
    ]

    for query in test_queries:
        print(f"\n查询: '{query}'")
        print("-" * 60)

        # 纯向量检索
        vector_results = vector_retriever.get_relevant_documents(query)
        print("\n纯向量检索结果:")
        for i, doc in enumerate(vector_results[:3], 1):
            print(f"  {i}. {doc.metadata.get('product_name', 'Unknown')}")

        # 混合检索
        hybrid_results = hybrid_retriever.search(query, top_k=3)
        print("\n混合检索结果:")
        for i, doc in enumerate(hybrid_results, 1):
            print(f"  {i}. {doc.metadata.get('product_name', 'Unknown')} "
                  f"(RRF: {doc.metadata.get('rrf_score', 0):.4f})")


def test_tool_comparison():
    """测试工具化对比"""
    print("\n" + "=" * 60)
    print("测试 2: 工具化产品对比")
    print("=" * 60)

    vm = VectorStoreManager()
    all_docs = vm.get_all_documents()
    bm25_retriever = BM25Retriever(all_docs)
    hybrid_retriever = HybridSearchRetriever(
        vector_retriever=vm.get_retriever(),
        bm25_retriever=bm25_retriever
    )

    agent = InsuranceAgent(hybrid_retriever, use_tools=True)

    products = ["超级玛丽9号重疾险", "达尔文8号重疾险"]
    dimensions = ["保障内容", "产品特色", "保险公司"]

    print(f"\n对比产品: {', '.join(products)}")
    print(f"对比维度: {', '.join(dimensions)}\n")

    result = agent.compare_products(products, dimensions)
    print(result)


def test_qa_with_hybrid():
    """测试混合检索问答"""
    print("\n" + "=" * 60)
    print("测试 3: 基于混合检索的智能问答")
    print("=" * 60)

    vm = VectorStoreManager()
    all_docs = vm.get_all_documents()
    bm25_retriever = BM25Retriever(all_docs)
    hybrid_retriever = HybridSearchRetriever(
        vector_retriever=vm.get_retriever(),
        bm25_retriever=bm25_retriever
    )

    agent = InsuranceAgent(hybrid_retriever, use_tools=True)

    question = "超级玛丽9号适合什么人群？保费大概多少？"
    print(f"\n问题: {question}\n")

    result = agent.ask(question)
    print(f"回答:\n{result['answer']}\n")
    print(f"参考来源:")
    for i, source in enumerate(result['sources'], 1):
        print(f"  {i}. {source['product_name']} ({source['company']}) - 相关度: {source['score']:.4f}")


if __name__ == "__main__":
    print("🧪 开始测试重构后的系统...\n")

    try:
        test_hybrid_search()
        test_tool_comparison()
        test_qa_with_hybrid()
        print("\n" + "=" * 60)
        print("✅ 所有测试完成！")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        print("\n请确保：")
        print("1. 已运行 python src/retriever/init_db.py 初始化数据库")
        print("2. 已在 config/.env 中配置 ANTHROPIC_API_KEY")
