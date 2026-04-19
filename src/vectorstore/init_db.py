"""
初始化向量数据库
"""
import sys
sys.path.append('.')

from src.vectorstore.vector_manager import VectorStoreManager
from data.products.sample_products import SAMPLE_PRODUCTS


def init_database():
    """初始化数据库并导入示例数据"""
    print("🚀 开始初始化向量数据库...")

    # 创建向量库管理器
    vm = VectorStoreManager()
    vm.init_vectorstore()

    # 导入产品数据
    print(f"\n📦 导入 {len(SAMPLE_PRODUCTS)} 个产品...")
    vm.add_products(SAMPLE_PRODUCTS)

    print("\n✅ 数据库初始化完成！")
    print(f"   - 持久化目录: {vm.persist_dir}")
    print(f"   - 集合名称: {vm.collection_name}")


if __name__ == "__main__":
    init_database()
