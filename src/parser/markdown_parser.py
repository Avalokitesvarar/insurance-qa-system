"""
Markdown文章解析器
处理公众号文章
"""
from pathlib import Path
from typing import List, Dict, Any
from langchain_core.documents import Document
import re
from datetime import datetime


class MarkdownParser:
    """Markdown文章解析器"""

    def __init__(self, md_path: str):
        """
        初始化解析器

        Args:
            md_path: Markdown文件路径
        """
        self.md_path = Path(md_path)
        if not self.md_path.exists():
            raise FileNotFoundError(f"文件不存在: {md_path}")

    def parse(self) -> Dict[str, Any]:
        """
        解析Markdown文档

        Returns:
            包含标题、内容、标签等的字典
        """
        with open(self.md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        result = {
            "file_name": self.md_path.name,
            "title": self._extract_title(content),
            "content": content,
            "tags": self._extract_tags(content),
            "product_mentions": self._extract_products(content),
            "sections": self._extract_sections(content)
        }

        return result

    def _extract_title(self, content: str) -> str:
        """提取标题"""
        # 从文件名提取
        title = self.md_path.stem
        # 去除前缀数字
        title = re.sub(r'^\d+_?', '', title)

        # 或从第一个一级标题提取
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if match:
            title = match.group(1).strip()

        return title

    def _extract_tags(self, content: str) -> List[str]:
        """提取标签（从标题和内容推断）"""
        tags = []

        # 产品类型标签
        if any(keyword in content for keyword in ['重疾险', '重大疾病']):
            tags.append('重疾险')
        if any(keyword in content for keyword in ['医疗险', '百万医疗']):
            tags.append('医疗险')
        if any(keyword in content for keyword in ['意外险']):
            tags.append('意外险')
        if any(keyword in content for keyword in ['储蓄险', '增额寿', '年金险']):
            tags.append('储蓄险')
        if any(keyword in content for keyword in ['分红险']):
            tags.append('分红险')

        # 内容类型标签
        if '榜单' in content:
            tags.append('产品榜单')
        if any(keyword in content for keyword in ['测评', '对比']):
            tags.append('产品测评')

        return list(set(tags))

    def _extract_products(self, content: str) -> List[str]:
        """提取提到的产品名称"""
        products = []

        # 常见产品名模式
        patterns = [
            r'([^\s，。、]+(?:重疾险|医疗险|意外险|寿险|年金险))',
            r'(超级玛丽\d+号)',
            r'(达尔文\d+号)',
            r'(蓝医保)',
            r'(大黄蜂\d+号)',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content)
            products.extend(matches)

        return list(set(products))

    def _extract_sections(self, content: str) -> Dict[str, str]:
        """提取章节"""
        sections = {}

        # 按二级标题分割
        parts = re.split(r'\n##\s+(.+?)\n', content)

        if len(parts) > 1:
            for i in range(1, len(parts), 2):
                if i + 1 < len(parts):
                    section_title = parts[i].strip()
                    section_content = parts[i + 1].strip()
                    sections[section_title] = section_content

        return sections

    def to_document(self, metadata: Dict[str, Any] = None) -> Document:
        """
        转换为LangChain Document

        Args:
            metadata: 额外的元数据

        Returns:
            Document对象
        """
        parsed = self.parse()

        base_metadata = metadata or {}
        base_metadata.update({
            "source": str(self.md_path),
            "file_name": parsed["file_name"],
            "title": parsed["title"],
            "type": "article"
        })

        # 只添加非空的列表字段
        if parsed["tags"]:
            base_metadata["tags"] = ",".join(parsed["tags"])  # 转为字符串
        if parsed["product_mentions"]:
            base_metadata["product_mentions"] = ",".join(parsed["product_mentions"])  # 转为字符串

        doc = Document(
            page_content=f"# {parsed['title']}\n\n{parsed['content']}",
            metadata=base_metadata
        )

        return doc
