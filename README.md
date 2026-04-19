# 保险智能助手

基于Claude AI和向量检索技术的保险智能问答系统

## 功能特点

- 🤖 AI智能问答
- 📚 知识库检索（896篇文章 + 270个产品资料）
- 💬 对话历史记录
- 🎯 多数据库联合查询

## 在线体验

访问：[部署后的URL]

## 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 配置API密钥
# 编辑 config/.env 文件，添加 ANTHROPIC_API_KEY

# 启动应用
streamlit run app.py
```

## 技术栈

- Streamlit - Web界面
- Claude AI - 智能问答
- ChromaDB - 向量数据库
- LangChain - 检索框架
- BGE - 中文嵌入模型

## 项目结构

```
insurance-agent/
├── app.py                 # Web界面
├── qa_system.py          # 问答系统
├── src/                  # 源代码
│   ├── retriever/       # 检索模块
│   └── parser/          # 解析模块
├── config/              # 配置文件
└── data/                # 数据目录
```

## 注意事项

⚠️ 本系统仅供参考，具体投保请咨询专业顾问

## License

MIT
