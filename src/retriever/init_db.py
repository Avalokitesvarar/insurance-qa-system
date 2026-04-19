"""
初始化向量数据库（重构版）
支持混合检索
"""
import sys
sys.path.append('.')

from src.retriever.vector_store import VectorStoreManager
from src.retriever.bm25_retriever import BM25Retriever
from src.retriever.hybrid_search import HybridSearchRetriever
from data.products.sample_products import SAMPLE_PRODUCTS
from config.settings import settings


def init_database():
    """初始化数据库并导入示例数据"""
    print("🚀 开始初始化向量数据库...")

    # 1. 创建向量库管理器
    vm = VectorStoreManager()
    vm.init_vectorstore()

    # 2. 导入产品数据
    print(f"\n📦 导入 {len(SAMPLE_PRODUCTS)} 个产品...")
    split_docs = vm.add_products(SAMPLE_PRODUCTS)

    # 3. 初始化BM25检索器
    print("\n🔍 初始化BM25检索器...")
    bm25_retriever = BM25Retriever(split_docs)
    print(f"✓ BM25索引已建立，共 {len(split_docs)} 个文档块")

    # 4. 测试混合检索
    if settings.use_hybrid_search:
        print("\n🔄 测试混合检索...")
        vector_retriever = vm.get_retriever()
        hybrid_retriever = HybridSearchRetriever(
            vector_retriever=vector_retriever,
            bm25_retriever=bm25_retriever,
            vector_weight=settings.vector_weight,
            bm25_weight=settings.bm25_weight
        )

        # 测试查询
        test_query = "超级玛丽9号"
        results = hybrid_retriever.search(test_query, top_k=3)
        print(f"\n测试查询：'{test_query}'")
        print(f"检索到 {len(results)} 个结果：")
        for i, doc in enumerate(results, 1):
            print(f"  {i}. {doc.metadata.get('product_name', 'Unknown')} "
                  f"(RRF分数: {doc.metadata.get('rrf_score', 0):.4f})")

    print("\n✅ 数据库初始化完成！")
    print(f"   - 持久化目录: {vm.persist_dir}")
    print(f"   - 集合名称: {vm.collection_name}")
    print(f"   - 混合检索: {'启用' if settings.use_hybrid_search else '禁用'}")


if __name__ == "__main__":
    init_database()
