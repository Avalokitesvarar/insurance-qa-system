# 快速开始指南

## 第一步：安装依赖

```bash
cd insurance-agent
pip install -r requirements.txt
```

**注意**：首次安装会下载中文嵌入模型（约400MB），需要等待几分钟。

## 第二步：配置API密钥

```bash
# 复制配置文件
cp config/.env.example config/.env

# 编辑 config/.env，添加你的 Anthropic API Key
# ANTHROPIC_API_KEY=sk-ant-xxxxx
```

## 第三步：初始化数据库

```bash
python src/vectorstore/init_db.py
```

预期输出：
```
🚀 开始初始化向量数据库...
📦 导入 4 个产品...
✓ 已添加 XX 个文档块
✅ 数据库初始化完成！
```

## 第四步：测试功能（可选）

```bash
python tests/test_agent.py
```

## 第五步：启动应用

```bash
streamlit run app.py
```

浏览器会自动打开 http://localhost:8501

## 功能演示

### 1. 智能问答
- 点击示例问题快速体验
- 或输入自定义问题

### 2. 产品对比
- 选择2-4个产品
- 选择对比维度
- 查看AI生成的对比分析

### 3. 需求分析
- 填写客户信息
- 获取个性化保险方案

## 常见问题

**Q: 初始化数据库时报错？**
A: 确保已安装所有依赖，特别是 chromadb 和 sentence-transformers

**Q: API调用失败？**
A: 检查 config/.env 中的 ANTHROPIC_API_KEY 是否正确

**Q: 嵌入模型下载慢？**
A: 可以手动下载模型到 ~/.cache/huggingface/

## 下一步

- 添加更多产品数据到 `data/products/`
- 导入公众号文章到 `data/articles/`
- 自定义 prompt 模板优化回答质量
