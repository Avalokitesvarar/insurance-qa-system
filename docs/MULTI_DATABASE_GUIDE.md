# 多数据库构建指南

## 数据库规划

在 D:\保险数据库\ 下创建3个独立数据库：

### 1. 公众号文章库
- **数据源**: D:\公众号文章\ (Markdown文件)
- **内容**: 保险产品榜单、测评文章、行业资讯
- **用途**: 产品推荐、市场趋势分析

### 2. 产品资料库
- **数据源**: C:\Users\jren3\Desktop\资料库\ (PDF/DOCX/PPTX)
- **内容**: 销售话术、产品分析报告、专业资料
- **用途**: 销售支持、专业知识查询

### 3. 综合知识库
- **数据源**: 混合来源
- **内容**: 条款文档、政策法规、客户案例
- **用途**: 综合查询、深度分析

## 快速开始

### 步骤1：安装依赖
```bash
cd insurance-agent
pip install python-pptx
```

### 步骤2：执行批量导入
```bash
python src/database_builder.py
```

这将自动：
1. 从 D:\公众号文章\ 导入所有Markdown文章到【公众号文章库】
2. 从 C:\Users\jren3\Desktop\资料库\ 导入所有PDF/DOCX/PPTX到【产品资料库】
3. 创建向量索引和BM25索引
4. 显示导入统计

### 步骤3：验证数据库
```bash
# 查看统计信息
python src/database_builder.py
```

## 数据库结构

```
D:\保险数据库\
├── 公众号文章库\
│   ├── chroma.sqlite3
│   └── [向量数据]
├── 产品资料库\
│   ├── chroma.sqlite3
│   └── [向量数据]
└── 综合知识库\
    ├── chroma.sqlite3
    └── [向量数据]
```

## 使用示例

### Python API
```python
from src.database_builder import MultiDatabaseManager

manager = MultiDatabaseManager()

# 查询文章库
vm_articles = manager.create_database("articles")
results = vm_articles.similarity_search("重疾险榜单", k=5)

# 查询资料库
vm_materials = manager.create_database("materials")
results = vm_materials.similarity_search("销售话术", k=5)

# 获取统计
stats = manager.get_statistics()
print(stats)
```

### 集成到智能体
```python
from src.agent.insurance_agent_v2 import InsuranceAgent
from src.retriever.hybrid_search import HybridSearchRetriever

# 使用文章库
vm = manager.create_database("articles")
retriever = vm.get_retriever()
agent = InsuranceAgent(retriever)

# 查询
result = agent.ask("4月医疗险榜单有哪些产品？")
```

## 数据源说明

### 公众号文章 (Markdown)
- 自动提取标题、标签、产品名称
- 识别产品类型（重疾险、医疗险、储蓄险等）
- 按章节分块

### Office文档 (PDF/DOCX/PPTX)
- PDF: 按章节提取，识别表格
- DOCX: 提取段落和表格
- PPTX: 按页提取内容

## 扩展功能

### 添加新数据源
```python
manager = MultiDatabaseManager()

# 导入新的Markdown文章
manager.import_markdown_articles(
    source_dir="新文章目录",
    db_key="articles"
)

# 导入新的Office文档
manager.import_office_documents(
    source_dir="新资料目录",
    db_key="materials"
)
```

### 创建自定义数据库
编辑 `src/database_builder.py`，在 `databases` 字典中添加新配置。

## 注意事项

1. **首次导入**: 需要下载中文嵌入模型（约400MB），请耐心等待
2. **文件编码**: Markdown文件需使用UTF-8编码
3. **文件大小**: 大文件会自动分块处理
4. **增量更新**: 重复运行会追加新文档，不会删除已有数据

## 性能优化

- 文章库适合语义搜索（产品推荐、趋势分析）
- 资料库适合精确查询（话术、报告）
- 建议使用混合检索提升准确率

## 故障排查

**问题**: 导入失败
- 检查文件路径是否正确
- 确认文件格式是否支持
- 查看错误日志

**问题**: 查询结果不准确
- 尝试使用混合检索
- 调整BM25和向量权重
- 优化查询关键词
