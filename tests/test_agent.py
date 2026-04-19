"""
测试智能体功能
"""
import sys
sys.path.append('.')

from src.vectorstore.vector_manager import VectorStoreManager
from src.agent.insurance_agent import InsuranceAgent


def test_qa():
    """测试问答功能"""
    print("=" * 50)
    print("测试 1: 智能问答")
    print("=" * 50)

    vm = VectorStoreManager()
    retriever = vm.get_retriever()
    agent = InsuranceAgent(retriever)

    question = "30岁男性，预算5000元，推荐什么重疾险？"
    print(f"\n问题: {question}\n")

    result = agent.ask(question)
    print(f"回答:\n{result['answer']}\n")
    print(f"参考来源: {len(result['sources'])} 个文档")


def test_compare():
    """测试产品对比"""
    print("\n" + "=" * 50)
    print("测试 2: 产品对比")
    print("=" * 50)

    vm = VectorStoreManager()
    retriever = vm.get_retriever()
    agent = InsuranceAgent(retriever)

    products = ["超级玛丽9号重疾险", "达尔文8号重疾险"]
    print(f"\n对比产品: {', '.join(products)}\n")

    result = agent.compare_products(products)
    print(f"对比结果:\n{result}")


def test_analysis():
    """测试需求分析"""
    print("\n" + "=" * 50)
    print("测试 3: 需求分析")
    print("=" * 50)

    vm = VectorStoreManager()
    retriever = vm.get_retriever()
    agent = InsuranceAgent(retriever)

    user_profile = {
        "age": 30,
        "gender": "男",
        "occupation": "程序员",
        "family_status": "已婚有子女",
        "budget": 8000,
        "existing_coverage": "公司团体医疗险"
    }

    print(f"\n客户信息: {user_profile}\n")

    result = agent.analyze_needs(user_profile)
    print(f"分析结果:\n{result}")


if __name__ == "__main__":
    print("🧪 开始测试保险智能体...\n")

    try:
        test_qa()
        test_compare()
        test_analysis()
        print("\n✅ 所有测试完成！")
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        print("\n请确保：")
        print("1. 已运行 python src/vectorstore/init_db.py 初始化数据库")
        print("2. 已在 config/.env 中配置 ANTHROPIC_API_KEY")
