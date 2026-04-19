"""
PDF解析器
处理保险条款PDF，提取文本和表格
"""
import pdfplumber
from typing import List, Dict, Any, Optional
from pathlib import Path
from langchain_core.documents import Document
import re


class PDFParser:
    """PDF条款解析器"""

    def __init__(self, pdf_path: str):
        """
        初始化解析器

        Args:
            pdf_path: PDF文件路径
        """
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")

    def parse(self) -> Dict[str, Any]:
        """
        解析PDF文档

        Returns:
            包含文本、表格和元数据的字典
        """
        result = {
            "file_name": self.pdf_path.name,
            "pages": [],
            "tables": [],
            "full_text": "",
            "sections": {}
        }

        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                # 提取文本
                text = page.extract_text() or ""
                result["pages"].append({
                    "page_num": page_num,
                    "text": text
                })
                result["full_text"] += f"\n--- 第{page_num}页 ---\n{text}"

                # 提取表格
                tables = page.extract_tables()
                for table_idx, table in enumerate(tables):
                    if table:
                        result["tables"].append({
                            "page": page_num,
                            "table_index": table_idx,
                            "data": table,
                            "formatted": self._format_table(table)
                        })

        # 提取章节
        result["sections"] = self._extract_sections(result["full_text"])

        return result

    def _format_table(self, table: List[List[str]]) -> str:
        """
        格式化表格为Markdown

        Args:
            table: 二维列表表示的表格

        Returns:
            Markdown格式的表格
        """
        if not table or len(table) < 2:
            return ""

        # 表头
        headers = [cell or "" for cell in table[0]]
        markdown = "| " + " | ".join(headers) + " |\n"
        markdown += "| " + " | ".join(["---"] * len(headers)) + " |\n"

        # 数据行
        for row in table[1:]:
            cells = [cell or "" for cell in row]
            # 补齐列数
            while len(cells) < len(headers):
                cells.append("")
            markdown += "| " + " | ".join(cells[:len(headers)]) + " |\n"

        return markdown

    def _extract_sections(self, text: str) -> Dict[str, str]:
        """
        提取保险条款的关键章节

        Args:
            text: 全文文本

        Returns:
            章节字典
        """
        sections = {}

        # 常见章节标题模式
        section_patterns = {
            "保险责任": r"(第[一二三四五六七八九十\d]+条?\s*)?保险责任(.*?)(?=第[一二三四五六七八九十\d]+条|责任免除|$)",
            "责任免除": r"(第[一二三四五六七八九十\d]+条?\s*)?责任免除(.*?)(?=第[一二三四五六七八九十\d]+条|保险期间|$)",
            "保险期间": r"(第[一二三四五六七八九十\d]+条?\s*)?保险期间(.*?)(?=第[一二三四五六七八九十\d]+条|保险金额|$)",
            "保险金额": r"(第[一二三四五六七八九十\d]+条?\s*)?保险金额(.*?)(?=第[一二三四五六七八九十\d]+条|保险费|$)",
            "等待期": r"(第[一二三四五六七八九十\d]+条?\s*)?等待期(.*?)(?=第[一二三四五六七八九十\d]+条|保险责任|$)",
        }

        for section_name, pattern in section_patterns.items():
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                content = match.group(2) if match.lastindex >= 2 else match.group(0)
                sections[section_name] = content.strip()

        return sections

    def to_documents(
        self,
        chunk_by: str = "section",
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        转换为LangChain Document对象

        Args:
            chunk_by: 分块策略 ("section", "page", "full")
            metadata: 额外的元数据

        Returns:
            Document列表
        """
        parsed = self.parse()
        documents = []
        base_metadata = metadata or {}
        base_metadata.update({
            "source": str(self.pdf_path),
            "file_name": parsed["file_name"],
            "type": "policy_document"
        })

        if chunk_by == "section":
            # 按章节分块
            for section_name, content in parsed["sections"].items():
                if content:
                    doc = Document(
                        page_content=f"【{section_name}】\n{content}",
                        metadata={
                            **base_metadata,
                            "section": section_name
                        }
                    )
                    documents.append(doc)

            # 添加表格
            for table_info in parsed["tables"]:
                doc = Document(
                    page_content=f"【表格 - 第{table_info['page']}页】\n{table_info['formatted']}",
                    metadata={
                        **base_metadata,
                        "section": "表格",
                        "page": table_info["page"]
                    }
                )
                documents.append(doc)

        elif chunk_by == "page":
            # 按页分块
            for page_info in parsed["pages"]:
                doc = Document(
                    page_content=page_info["text"],
                    metadata={
                        **base_metadata,
                        "page": page_info["page_num"]
                    }
                )
                documents.append(doc)

        else:  # full
            # 整个文档作为一个块
            doc = Document(
                page_content=parsed["full_text"],
                metadata=base_metadata
            )
            documents.append(doc)

        return documents
