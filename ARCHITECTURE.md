# 架构重构说明 v2.0

## 核心改进

### 1. 混合检索（Hybrid Search）
**问题**：纯向量检索对精确产品名匹配不准确  
**解决方案**：BM25（关键词）+ 向量检索 + RRF融合

```
查询: "超级玛丽9号"
├─ 向量检索 → 语义相似产品
├─ BM25检索 → 精确匹配产品名
└─ RRF融合 → 综合排序结果
```

**文件**：
- `src/retriever/bm25_retriever.py` - BM25关键词检索
- `src/retriever/hybrid_search.py` - RRF融合算法
- `src/retriever/vector_store.py` - 向量检索（重构）

### 2. 工具化对比（Tool-based Comparison）
**问题**：LLM直接生成对比容易产生幻觉  
**解决方案**：结构化数据提取 + 模板填充 + LLM分析

```
产品对比流程：
1. 检索产品信息（结构化）
2. 填充Markdown表格模板
3. LLM基于表格生成分析
```

**文件**：
- `src/tools/product_comparator.py` - 产品对比工具

### 3. 配置管理优化
**问题**：配置分散在代码中  
**解决方案**：统一配置管理

**文件**：
- `config/settings.py` - Pydantic配置类

### 4. Prompt分离
**问题**：Prompt与代码耦合  
**解决方案**：独立Prompt模块

**文件**：
- `src/agent/prompt.py` - Prompt模板管理

## 新增目录结构

```
insurance-agent/
├── config/
│   └── settings.py          # [新增] 配置管理
├── data/
│   └── raw/                 # [新增] 原始文档目录
├── src/
│   ├── parser/              # [预留] 文档解析
│   ├── retriever/           # [重构] 检索层
│   │   ├── vector_store.py
│   │   ├── bm25_retriever.py    # [新增]
│   │   ├── hybrid_search.py     # [新增]
│   │   └── init_db.py
│   ├── tools/               # [新增] 工具层
│   │   └── product_comparator.py
│   └── agent/
│       ├── prompt.py        # [新增]
│       └── insurance_agent_v2.py  # [重构]
├── app_v2.py                # [新增] 重构版应用
└── tests/
    └── test_hybrid_system.py  # [新增] 混合检索测试
```

## 使用方式

### 初始化（支持混合检索）
```bash
python src/retriever/init_db.py
```

### 测试系统
```bash
python tests/test_hybrid_system.py
```

### 启动应用
```bash
streamlit run app_v2.py
```

## 配置说明

编辑 `config/.env`：

```bash
# 启用混合检索
USE_HYBRID_SEARCH=true

# 调整权重（总和应为1.0）
BM25_WEIGHT=0.3      # 关键词权重
VECTOR_WEIGHT=0.7    # 向量权重
```

## 性能对比

| 场景 | 纯向量检索 | 混合检索 |
|------|-----------|---------|
| 精确产品名 | ⚠️ 可能匹配错误 | ✅ 准确匹配 |
| 语义查询 | ✅ 效果好 | ✅ 效果更好 |
| 产品对比 | ⚠️ 易产生幻觉 | ✅ 结构化准确 |

## 下一步优化

- [ ] 增加 `src/parser/` 处理PDF条款
- [ ] 实现产品数据的JSON/YAML管理
- [ ] 添加日志和监控
- [ ] 单元测试覆盖
