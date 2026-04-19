"""
保险智能问答系统 - 云端版本
不依赖本地数据库，仅演示AI问答功能
"""
import streamlit as st
import os
from anthropic import Anthropic

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
    .answer-box {
        background-color: #f0f8ff;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# 初始化AI客户端
@st.cache_resource
def init_client():
    api_key = st.secrets.get("ANTHROPIC_API_KEY")
    base_url = st.secrets.get("ANTHROPIC_BASE_URL")
    if base_url:
        return Anthropic(api_key=api_key, base_url=base_url)
    return Anthropic(api_key=api_key)

try:
    client = init_client()
    client_available = True
except Exception as e:
    client_available = False
    st.error(f"AI客户端初始化失败: {str(e)}")

# 初始化session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# 主标题
st.markdown('<div class="main-header">🛡️ 保险智能助手</div>', unsafe_allow_html=True)

# 侧边栏
with st.sidebar:
    st.header("⚙️ 系统信息")

    st.info("""
    **功能说明**

    这是保险智能问答系统的演示版本。

    由于云端限制，暂未加载完整知识库。

    完整版包含：
    - 896篇公众号文章
    - 270个产品资料
    - 向量检索功能
    """)

    st.divider()

    if st.button("🗑️ 清空对话历史"):
        st.session_state.chat_history = []
        st.rerun()

# 主界面
st.subheader("💬 智能问答")

st.warning("""
⚠️ **演示版本说明**

当前为云端演示版本，未加载完整知识库。

如需体验完整功能（包含896篇文章和270个产品资料的知识库检索），请：
1. 克隆GitHub仓库：https://github.com/Avalokitesvara/insurance-qa-system
2. 本地运行：`streamlit run app.py`

完整版支持：
- 多数据库联合检索
- 向量相似度搜索
- 混合检索（BM25 + 向量）
- 对话历史记录
""")

# 问题输入
question = st.text_input(
    "请输入您的保险相关问题：",
    placeholder="例如：重疾险和医疗险有什么区别？",
    key="question_input"
)

# 快捷问题
st.caption("💡 快捷问题：")
quick_questions = [
    "重疾险和医疗险有什么区别？",
    "儿童保险应该怎么配置？",
    "如何选择合适的保险产品？",
    "保险理赔需要注意什么？"
]

cols = st.columns(2)
for i, q in enumerate(quick_questions):
    with cols[i % 2]:
        if st.button(q, key=f"quick_{i}"):
            question = q

# 提交按钮
if st.button("🔍 提问", type="primary", use_container_width=True):
    if question and client_available:
        with st.spinner('AI正在思考中...'):
            try:
                # 调用Claude API
                response = client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=2000,
                    temperature=0.3,
                    system="""你是一位专业的保险顾问助手。请根据用户的问题，提供专业、准确的保险咨询建议。

回答要求：
1. 专业准确，使用通俗易懂的语言
2. 结构清晰，分点说明
3. 提供实用建议
4. 必要时提醒用户咨询专业顾问""",
                    messages=[
                        {"role": "user", "content": question}
                    ]
                )

                answer = response.content[0].text

                # 保存到历史
                st.session_state.chat_history.append({
                    "question": question,
                    "answer": answer
                })

            except Exception as e:
                st.error(f"AI回答失败: {str(e)}")
    elif not client_available:
        st.error("AI客户端未初始化，请检查配置")
    else:
        st.warning("请输入问题")

# 显示对话历史
if st.session_state.chat_history:
    st.divider()
    st.subheader("📝 对话历史")

    for i, chat in enumerate(reversed(st.session_state.chat_history)):
        with st.expander(f"❓ {chat['question'][:50]}...", expanded=(i==0)):
            st.markdown(f"**问题：** {chat['question']}")
            st.markdown('<div class="answer-box">', unsafe_allow_html=True)
            st.markdown(f"**回答：**\n\n{chat['answer']}")
            st.markdown('</div>', unsafe_allow_html=True)

# 页脚
st.divider()
st.caption("© 2026 保险智能助手 | 基于Claude AI构建 | [GitHub](https://github.com/Avalokitesvara/insurance-qa-system)")
