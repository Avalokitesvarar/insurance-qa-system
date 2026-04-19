"""
文本分块策略
针对保险条款的智能分块
"""
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import re


class InsuranceTextSplitter:
    """保险条款专用文本分块器"""

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        strategy: str = "semantic"
    ):
        """
        初始化分块器

        Args:
            chunk_size: 块大小
            chunk_overlap: 重叠大小
            strategy: 分块策略 ("semantic", "fixed")
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.strategy = strategy

        # 基础分块器
        self.base_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", "。", "；", "，", " ", ""]
        )

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        分块文档

        Args:
            documents: 文档列表

        Returns:
            分块后的文档列表
        """
        if self.strategy == "semantic":
            return self._semantic_split(documents)
        else:
            return self.base_splitter.split_documents(documents)

    def _semantic_split(self, documents: List[Document]) -> List[Document]:
        """
        语义分块：按保险条款的逻辑结构分块

        保险条款通常有明确的结构：
        - 第X条：单独成块
        - 表格：单独成块
        - 列表项：保持完整
        """
        result = []

        for doc in documents:
            content = doc.page_content
            metadata = doc.metadata

            # 如果是表格，不分块
            if "表格" in content or metadata.get("section") == "表格":
                result.append(doc)
                continue

            # 按条款分块
            chunks = self._split_by_clauses(content)

            for i, chunk in enumerate(chunks):
                if len(chunk.strip()) > 0:
                    new_doc = Document(
                        page_content=chunk,
                        metadata={
                            **metadata,
                            "chunk_index": i
                        }
                    )
                    result.append(new_doc)

        return result

    def _split_by_clauses(self, text: str) -> List[str]:
        """
        按条款分块

        识别"第X条"模式，每条作为一个块
        """
        # 匹配"第X条"模式
        clause_pattern = r'第[一二三四五六七八九十百\d]+条'
        matches = list(re.finditer(clause_pattern, text))

        if not matches:
            # 没有条款标记，使用基础分块
            return self.base_splitter.split_text(text)

        chunks = []
        for i, match in enumerate(matches):
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)

            clause_text = text[start:end].strip()

            # 如果单条过长，进一步分块
            if len(clause_text) > self.chunk_size * 1.5:
                sub_chunks = self.base_splitter.split_text(clause_text)
                chunks.extend(sub_chunks)
            else:
                chunks.append(clause_text)

        return chunks

    def split_by_section(self, sections: Dict[str, str]) -> List[Document]:
        """
        按章节分块

        Args:
            sections: 章节字典 {章节名: 内容}

        Returns:
            文档列表
        """
        documents = []

        for section_name, content in sections.items():
            # 每个章节作为独立文档
            doc = Document(
                page_content=f"【{section_name}】\n{content}",
                metadata={
                    "section": section_name,
                    "type": "section"
                }
            )

            # 如果章节过长，进一步分块
            if len(content) > self.chunk_size * 2:
                sub_docs = self.base_splitter.split_documents([doc])
                documents.extend(sub_docs)
            else:
                documents.append(doc)

        return documents


class TableExtractor:
    """表格提取和格式化工具"""

    @staticmethod
    def extract_coverage_table(text: str) -> List[Dict[str, str]]:
        """
        从文本中提取保障项表格

        Args:
            text: 包含表格的文本

        Returns:
            保障项列表
        """
        # 识别常见的保障项模式
        patterns = [
            r'([^\n]+?)\s+(\d+万?元?)\s+([^\n]+)',  # 保障项 保额 说明
            r'([^\n]+?)[:：]\s*(\d+万?元?)',  # 保障项: 保额
        ]

        coverages = []
        for pattern in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                coverage = {
                    "name": match.group(1).strip(),
                    "amount": match.group(2).strip(),
                    "description": match.group(3).strip() if match.lastindex >= 3 else ""
                }
                coverages.append(coverage)

        return coverages

    @staticmethod
    def extract_premium_table(text: str) -> List[Dict[str, Any]]:
        """
        从文本中提取保费表格

        Args:
            text: 包含保费表格的文本

        Returns:
            保费信息列表
        """
        # 识别保费模式：年龄 + 价格
        pattern = r'(\d+)岁\s+(\d+\.?\d*)元?'
        matches = re.finditer(pattern, text)

        premiums = []
        for match in matches:
            premium = {
                "age": int(match.group(1)),
                "price": float(match.group(2))
            }
            premiums.append(premium)

        return premiums
