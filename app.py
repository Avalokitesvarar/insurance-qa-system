"""
保险智能问答系统 - 云端版本
"""
import streamlit as st
from anthropic import Anthropic

st.set_page_config(
    page_title="保险智能助手",
    page_icon="🛡️",
    layout="wide"
)

# 初始化session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'current_question' not in st.session_state:
    st.session_state.current_question = ""

# 初始化AI客户端
@st.cache_resource
def init_client():
    try:
        api_key = st.secrets["ANTHROPIC_API_KEY"]
        base_url = st.secrets.get("ANTHROPIC_BASE_URL")
        if base_url:
            return Anthropic(api_key=api_key, base_url=base_url)
        return Anthropic(api_key=api_key)
    except Exception as e:
        st.error(f"❌ API配置错误: {str(e)}")
        return None

client = init_client()

# 标题
st.markdown("# 🛡️ 保险智能助手")

# 侧边栏
with st.sidebar:
    st.header("⚙️ 系统信息")
    st.info("""
    **云端演示版**

    ✅ AI智能问答
    ⚠️ 未加载知识库

    完整版包含：
    - 896篇文章
    - 270个产品资料
    - 向量检索
    """)

    if st.button("🗑️ 清空历史"):
        st.session_state.chat_history = []
        st.rerun()

# 主界面
st.subheader("💬 智能问答")

# 问题输入
question = st.text_input(
    "请输入保险相关问题：",
    value=st.session_state.current_question,
    placeholder="例如：重疾险和医疗险有什么区别？"
)

# 快捷问题
st.caption("💡 快捷问题：")
cols = st.columns(4)
quick_qs = [
    "重疾险和医疗险有什么区别？",
    "儿童保险应该怎么配置？",
    "如何选择合适的保险产品？",
    "保险理赔需要注意什么？"
]

for i, q in enumerate(quick_qs):
    with cols[i]:
        if st.button(q[:8]+"...", key=f"q{i}", use_container_width=True):
            st.session_state.current_question = q
            st.rerun()

# 提交按钮
if st.button("🔍 提问", type="primary", use_container_width=True):
    if not question:
        st.warning("⚠️ 请输入问题")
    elif not client:
        st.error("❌ AI客户端未初始化")
    else:
        with st.spinner('🤔 AI正在思考...'):
            try:
                response = client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=2000,
                    temperature=0.3,
                    system="你是专业的保险顾问。用通俗易懂的语言回答问题，结构清晰，提供实用建议。",
                    messages=[{"role": "user", "content": question}]
                )

                answer = response.content[0].text

                st.session_state.chat_history.append({
                    "question": question,
                    "answer": answer
                })
                st.session_state.current_question = ""
                st.success("✅ 回答完成！")

            except Exception as e:
                st.error(f"❌ AI回答失败: {str(e)}")

# 显示对话历史
if st.session_state.chat_history:
    st.divider()
    st.subheader("📝 对话历史")

    for i, chat in enumerate(reversed(st.session_state.chat_history)):
        with st.expander(f"❓ {chat['question'][:40]}...", expanded=(i==0)):
            st.markdown(f"**问题：** {chat['question']}")
            st.markdown("---")
            st.markdown(chat['answer'])

# 页脚
st.divider()
st.caption("💡 提示：完整版支持知识库检索，请本地运行体验")
