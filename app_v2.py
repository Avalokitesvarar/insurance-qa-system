"""
Streamlit 应用入口（重构版）
支持混合检索和工具化对比
"""
import sys
sys.path.append('.')

import streamlit as st
from src.retriever.vector_store import VectorStoreManager
from src.retriever.bm25_retriever import BM25Retriever
from src.retriever.hybrid_search import HybridSearchRetriever
from src.agent.insurance_agent_v2 import InsuranceAgent
from config.settings import settings

# 页面配置
st.set_page_config(
    page_title=settings.app_title,
    page_icon="🛡️",
    layout="wide"
)

# 初始化
@st.cache_resource
def init_agent():
    """初始化智能体（支持混合检索）"""
    vm = VectorStoreManager()
    vm.init_vectorstore()

    if settings.use_hybrid_search:
        # 使用混合检索
        vector_retriever = vm.get_retriever()
        all_docs = vm.get_all_documents()
        bm25_retriever = BM25Retriever(all_docs)

        retriever = HybridSearchRetriever(
            vector_retriever=vector_retriever,
            bm25_retriever=bm25_retriever,
            vector_weight=settings.vector_weight,
            bm25_weight=settings.bm25_weight
        )
    else:
        # 仅使用向量检索
        retriever = vm.get_retriever()

    agent = InsuranceAgent(retriever, use_tools=True)
    return agent, settings.use_hybrid_search

# 主界面
def main():
    st.title("🛡️ 保险智能助手 v2.0")

    # 侧边栏
    with st.sidebar:
        st.header("功能选择")
        mode = st.radio(
            "选择功能模式",
            ["💬 智能问答", "📊 产品对比", "🎯 需求分析"]
        )

        st.markdown("---")
        st.markdown("### 系统配置")

        try:
            agent, use_hybrid = init_agent()
            st.success("✅ 系统已就绪")
            st.info(f"检索模式: {'混合检索 (BM25+向量)' if use_hybrid else '向量检索'}")
            st.info(f"模型: {settings.claude_model}")
        except Exception as e:
            st.error(f"❌ 初始化失败: {str(e)}")
            st.info("请先运行: python src/retriever/init_db.py")
            return

        st.markdown("---")
        st.markdown("### 关于")
        st.caption("基于 Claude Sonnet 4.6 + 混合检索 + 工具化对比")

    # 功能模块
    if mode == "💬 智能问答":
        qa_interface(agent)
    elif mode == "📊 产品对比":
        compare_interface(agent)
    elif mode == "🎯 需求分析":
        analysis_interface(agent)


def qa_interface(agent):
    """问答界面"""
    st.header("💬 智能问答")

    # 示例问题
    st.markdown("**示例问题：**")
    examples = [
        "30岁男性，预算5000元，推荐什么重疾险？",
        "超级玛丽9号的等待期是多久？",
        "超级玛丽9号和达尔文8号有什么区别？",
        "医疗险和重疾险有什么不同？"
    ]

    cols = st.columns(2)
    for i, example in enumerate(examples):
        if cols[i % 2].button(example, key=f"ex_{i}"):
            st.session_state.question = example

    # 问题输入
    question = st.text_area(
        "请输入您的问题：",
        value=st.session_state.get("question", ""),
        height=100,
        key="qa_input"
    )

    if st.button("🔍 提问", type="primary"):
        if question:
            with st.spinner("正在思考..."):
                result = agent.ask(question)

            st.markdown("### 回答")
            st.write(result["answer"])

            with st.expander("📚 参考来源"):
                for i, source in enumerate(result["sources"], 1):
                    st.markdown(f"**来源 {i}**: {source['product_name']} ({source['company']}) - 相关度: {source['score']:.4f}")
        else:
            st.warning("请输入问题")


def compare_interface(agent):
    """产品对比界面"""
    st.header("📊 产品对比分析")

    col1, col2 = st.columns(2)

    with col1:
        products = st.multiselect(
            "选择要对比的产品（2-4个）",
            ["超级玛丽9号重疾险", "达尔文8号重疾险", "蓝医保长期医疗险", "大黄蜂9号少儿重疾险"],
            default=["超级玛丽9号重疾险", "达尔文8号重疾险"]
        )

    with col2:
        dimensions = st.multiselect(
            "对比维度",
            ["保障内容", "保费", "产品特色", "责任免除", "保险公司"],
            default=["保障内容", "产品特色", "责任免除"]
        )

    if st.button("🔄 开始对比", type="primary"):
        if len(products) < 2:
            st.warning("请至少选择2个产品")
        else:
            with st.spinner("正在分析..."):
                result = agent.compare_products(products, dimensions)

            st.markdown("### 对比结果")
            st.markdown(result)


def analysis_interface(agent):
    """需求分析界面"""
    st.header("🎯 保险需求分析")

    col1, col2 = st.columns(2)

    with col1:
        age = st.number_input("年龄", min_value=0, max_value=100, value=30)
        gender = st.selectbox("性别", ["男", "女"])
        occupation = st.text_input("职业", "互联网从业者")

    with col2:
        family_status = st.selectbox("家庭状况", ["单身", "已婚无子女", "已婚有子女"])
        budget = st.number_input("年度预算（元）", min_value=0, value=5000, step=500)
        existing = st.text_input("已有保障", "无")

    if st.button("🎯 分析需求", type="primary"):
        user_profile = {
            "age": age,
            "gender": gender,
            "occupation": occupation,
            "family_status": family_status,
            "budget": budget,
            "existing_coverage": existing
        }

        with st.spinner("正在分析..."):
            result = agent.analyze_needs(user_profile)

        st.markdown("### 分析结果")
        st.markdown(result)


if __name__ == "__main__":
    main()
