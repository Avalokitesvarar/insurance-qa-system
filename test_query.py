"""
知识库查询测试脚本
"""
import sys
sys.path.append('.')

from src.retriever.vector_store import VectorStoreManager
import chromadb

def test_query(db_name, db_path, collection_name, query, top_k=3):
    """测试查询"""
    print(f"\n{'='*60}")
    print(f"测试数据库: {db_name}")
    print(f"查询问题: {query}")
    print(f"{'='*60}\n")

    # 初始化向量库
    vm = VectorStoreManager()
    vm.persist_dir = db_path
    vm.collection_name = collection_name
    vm.client = chromadb.PersistentClient(path=vm.persist_dir)
    vm.init_vectorstore()

    # 执行查询
    results = vm.similarity_search(query, k=top_k)

    # 显示结果
    for i, doc in enumerate(results, 1):
        print(f"[结果 {i}]")
        print(f"标题: {doc.metadata.get('title', '未知')}")
        print(f"来源: {doc.metadata.get('file_name', '未知')}")
        if 'tags' in doc.metadata:
            print(f"标签: {doc.metadata['tags']}")
        print(f"内容预览: {doc.page_content[:200]}...")
        print(f"{'-'*60}\n")

def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("保险知识库查询测试")
    print("="*60)

    # 测试1: 查询公众号文章库
    test_query(
        db_name="公众号文章库",
        db_path="D:/保险数据库/公众号文章库",
        collection_name="insurance_articles",
        query="4月医疗险榜单有哪些产品推荐？",
        top_k=3
    )

    # 测试2: 查询产品资料库
    test_query(
        db_name="产品资料库",
        db_path="D:/保险数据库/产品资料库",
        collection_name="insurance_materials",
        query="乳腺癌保险理赔相关信息",
        top_k=3
    )

    # 测试3: 查询重疾险相关
    test_query(
        db_name="公众号文章库",
        db_path="D:/保险数据库/公众号文章库",
        collection_name="insurance_articles",
        query="重疾险哪个产品性价比高？",
        top_k=3
    )

    print("\n" + "="*60)
    print("测试完成！")
    print("="*60)

if __name__ == "__main__":
    main()
