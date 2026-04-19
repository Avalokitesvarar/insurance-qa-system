# PDF条款解析模块使用指南

## 功能概述

PDF解析模块专门用于处理保险条款文档，支持：
- 自动提取文本和表格
- 按章节智能分块（识别"第X条"结构）
- 提取关键章节（保险责任、责任免除、等待期等）
- 批量导入PDF到向量库

## 核心组件

### 1. PDFParser - PDF解析器
```python
from src.parser.pdf_parser import PDFParser

parser = PDFParser("data/raw/产品条款.pdf")
result = parser.parse()

# 获取章节
sections = result["sections"]  # {"保险责任": "...", "责任免除": "..."}

# 转换为LangChain文档
documents = parser.to_documents(chunk_by="section")
```

### 2. InsuranceTextSplitter - 智能分块器
```python
from src.parser.text_splitter import InsuranceTextSplitter

splitter = InsuranceTextSplitter(
    chunk_size=500,
    strategy="semantic"  # 按条款逻辑分块
)

split_docs = splitter.split_documents(documents)
```

### 3. PolicyImporter - 批量导入工具
```python
from src.parser.import_policies import PolicyImporter

importer = PolicyImporter()

# 导入单个PDF
importer.import_pdf(
    "data/raw/超级玛丽9号条款.pdf",
    product_name="超级玛丽9号重疾险",
    company="信泰人寿"
)

# 批量导入目录
importer.import_directory("data/raw/")

# 查看统计
stats = importer.get_statistics()
```

## 使用流程

### 步骤1：准备PDF文件
将保险条款PDF放入 `data/raw/` 目录：
```
data/raw/
├── 超级玛丽9号条款.pdf
├── 达尔文8号条款.pdf
└── 蓝医保条款.pdf
```

### 步骤2：导入PDF
```bash
# 导入单个文件
python src/parser/import_policies.py data/raw/超级玛丽9号条款.pdf \
    --product "超级玛丽9号重疾险" \
    --company "信泰人寿"

# 批量导入目录
python src/parser/import_policies.py data/raw/ --stats
```

### 步骤3：验证导入
```bash
# 运行测试
python tests/test_pdf_parser.py
```

## 智能分块策略

### 语义分块（推荐）
按保险条款的逻辑结构分块：
- 识别"第X条"模式，每条作为独立块
- 表格单独成块，不拆分
- 保持列表项完整性

### 固定分块
按字符数固定分块（适用于无明确结构的文档）

## 表格提取

自动识别和提取常见表格：

### 保障项表格
```python
from src.parser.text_splitter import TableExtractor

text = "重大疾病 50万元 120种重疾"
coverages = TableExtractor.extract_coverage_table(text)
# [{"name": "重大疾病", "amount": "50万元", "description": "120种重疾"}]
```

### 保费表格
```python
text = "30岁 5280元\n40岁 8650元"
premiums = TableExtractor.extract_premium_table(text)
# [{"age": 30, "price": 5280}, {"age": 40, "price": 8650}]
```

## 章节识别

自动识别常见章节：
- 保险责任
- 责任免除
- 保险期间
- 保险金额
- 等待期

## 注意事项

1. **PDF质量**：扫描版PDF需要先OCR处理
2. **中文字体**：复杂排版可能需要调整解析参数
3. **表格格式**：复杂表格建议手动校验提取结果
4. **文件命名**：建议使用产品名作为文件名，便于自动识别

## 测试

```bash
# 测试PDF解析
python tests/test_pdf_parser.py

# 测试完整流程
python tests/test_hybrid_system.py
```

## 下一步

- 添加OCR支持处理扫描版PDF
- 优化表格识别算法
- 支持Word文档解析
- 实现条款对比功能
