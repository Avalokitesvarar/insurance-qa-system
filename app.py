"""
保险智能问答系统 - Web界面
基于Streamlit构建
"""
import streamlit as st
import sys
sys.path.append('.')

from qa_system import InsuranceQASystem
import time

# 页面配置
st.set_page_config(
    page_title="保险智能助手",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stTextInput > div > div > input {
        font-size: 1.1rem;
    }
    .answer-box {
        background-color: #f0f8ff;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
    }
    .source-box {
        background-color: #f9f9f9;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# 初始化session state
if 'qa_system' not in st.session_state:
    with st.spinner('正在初始化知识库...'):
        st.session_state.qa_system = InsuranceQASystem()
    st.success('知识库初始化完成！')

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# 主标题
st.markdown('<div class="main-header">🛡️ 保险智能助手</div>', unsafe_allow_html=True)

# 侧边栏
with st.sidebar:
    st.header("⚙️ 设置")

    # 数据库选择
    st.subheader("知识库选择")
    use_articles = st.checkbox("公众号文章库", value=True)
    use_materials = st.checkbox("产品资料库", value=True)

    # 检索参数
    st.subheader("检索参数")
    top_k = st.slider("返回结果数量", min_value=1, max_value=10, value=3)

    st.divider()

    # 统计信息
    st.subheader("📊 知识库统计")
    st.info("""
    **公众号文章库**
    - 文档块数：712

    **产品资料库**
    - 文档块数：270

    **总计**
    - 982个文档块
    """)

    st.divider()

    # 清空历史
    if st.button("🗑️ 清空对话历史"):
        st.session_state.chat_history = []
        st.rerun()

# 主界面
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("💬 智能问答")

    # 问题输入
    question = st.text_input(
        "请输入您的问题：",
        placeholder="例如：4月医疗险榜单有哪些产品推荐？",
        key="question_input"
    )

    # 快捷问题
    st.caption("💡 快捷问题：")
    quick_questions = [
        "4月医疗险榜单有哪些产品推荐？",
        "重疾险哪个产品性价比高？",
        "乳腺癌保险理赔需要注意什么？",
        "儿童保险应该怎么配置？"
    ]

    cols = st.columns(2)
    for i, q in enumerate(quick_questions):
        with cols[i % 2]:
            if st.button(q, key=f"quick_{i}"):
                question = q
                st.session_state.question_input = q

    # 提交按钮
    if st.button("🔍 提问", type="primary", use_container_width=True):
        if question:
            # 确定使用的数据库
            db_keys = []
            if use_articles:
                db_keys.append("articles")
            if use_materials:
                db_keys.append("materials")

            if not db_keys:
                st.error("请至少选择一个知识库！")
            else:
                # 显示加载动画
                with st.spinner('正在思考中...'):
                    # 调用问答系统
                    answer = st.session_state.qa_system.ask(
                        question=question,
                        db_keys=db_keys,
                        top_k=top_k
                    )

                # 保存到历史
                st.session_state.chat_history.append({
                    "question": question,
                    "answer": answer,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                })

    # 显示对话历史
    if st.session_state.chat_history:
        st.divider()
        st.subheader("📝 对话历史")

        # 倒序显示（最新的在上面）
        for i, chat in enumerate(reversed(st.session_state.chat_history)):
            with st.expander(f"❓ {chat['question'][:50]}... ({chat['timestamp']})", expanded=(i==0)):
                st.markdown(f"**问题：** {chat['question']}")
                st.markdown('<div class="answer-box">', unsafe_allow_html=True)
                st.markdown(f"**回答：**\n\n{chat['answer']}")
                st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.subheader("📚 使用指南")

    st.info("""
    **如何使用：**
    1. 在左侧选择要查询的知识库
    2. 输入您的问题或点击快捷问题
    3. 点击"提问"按钮获取答案

    **支持的问题类型：**
    - 产品推荐
    - 产品对比
    - 理赔咨询
    - 保险知识
    - 投保建议
    """)

    st.success("""
    **系统特点：**
    - 基于896篇公众号文章
    - 包含270个产品资料
    - AI智能分析回答
    - 实时检索最新信息
    """)

    st.warning("""
    **注意事项：**
    - 回答仅供参考
    - 具体投保请咨询专业顾问
    - 以保险合同为准
    """)

# 页脚
st.divider()
st.caption("© 2026 保险智能助手 | 基于Claude AI构建")
