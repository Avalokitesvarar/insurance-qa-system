"""
多数据库管理器
支持创建和管理多个独立的向量数据库
"""
import sys
sys.path.append('.')

from pathlib import Path
from typing import List, Dict, Any
from src.retriever.vector_store import VectorStoreManager
from src.parser.markdown_parser import MarkdownParser
from src.parser.office_parser import DocxParser, PptxParser
from src.parser.pdf_parser import PDFParser
from langchain_core.documents import Document
import chromadb


class MultiDatabaseManager:
    """多数据库管理器"""

    def __init__(self, base_dir: str = "D:/保险数据库"):
        """
        初始化管理器

        Args:
            base_dir: 数据库根目录
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

        # 数据库配置
        self.databases = {
            "articles": {
                "name": "公众号文章库",
                "collection": "insurance_articles",
                "persist_dir": str(self.base_dir / "公众号文章库")
            },
            "materials": {
                "name": "产品资料库",
                "collection": "insurance_materials",
                "persist_dir": str(self.base_dir / "产品资料库")
            },
            "comprehensive": {
                "name": "综合知识库",
                "collection": "insurance_comprehensive",
                "persist_dir": str(self.base_dir / "综合知识库")
            }
        }

    def create_database(self, db_key: str) -> VectorStoreManager:
        """
        创建或连接数据库

        Args:
            db_key: 数据库键名 (articles/materials/comprehensive)

        Returns:
            VectorStoreManager实例
        """
        if db_key not in self.databases:
            raise ValueError(f"未知的数据库: {db_key}")

        config = self.databases[db_key]

        # 创建向量库管理器
        vm = VectorStoreManager()
        vm.persist_dir = config["persist_dir"]
        vm.collection_name = config["collection"]
        vm.client = chromadb.PersistentClient(path=vm.persist_dir)
        vm.init_vectorstore()

        return vm

    def import_markdown_articles(
        self,
        source_dir: str,
        db_key: str = "articles"
    ) -> int:
        """
        导入Markdown文章到文章库

        Args:
            source_dir: 源目录
            db_key: 目标数据库

        Returns:
            导入的文档数量
        """
        print(f"\n[*] 导入Markdown文章到【{self.databases[db_key]['name']}】")
        print(f"    源目录: {source_dir}")

        vm = self.create_database(db_key)
        source_path = Path(source_dir)

        if not source_path.exists():
            raise FileNotFoundError(f"目录不存在: {source_dir}")

        md_files = list(source_path.glob("*.md"))
        print(f"    发现 {len(md_files)} 个Markdown文件")

        documents = []
        for md_file in md_files:
            try:
                parser = MarkdownParser(str(md_file))
                doc = parser.to_document()
                documents.append(doc)
            except Exception as e:
                print(f"   [!]  解析失败 {md_file.name}: {e}")

        if documents:
            vm.add_documents(documents)
            print(f"   [OK] 成功导入 {len(documents)} 篇文章")

        return len(documents)

    def import_office_documents(
        self,
        source_dir: str,
        db_key: str = "materials"
    ) -> int:
        """
        导入Office文档（PDF/DOCX/PPTX）到资料库

        Args:
            source_dir: 源目录
            db_key: 目标数据库

        Returns:
            导入的文档数量
        """
        print(f"\n[DIR] 导入Office文档到【{self.databases[db_key]['name']}】")
        print(f"   源目录: {source_dir}")

        vm = self.create_database(db_key)
        source_path = Path(source_dir)

        if not source_path.exists():
            raise FileNotFoundError(f"目录不存在: {source_dir}")

        # 查找所有支持的文件
        pdf_files = list(source_path.glob("*.pdf"))
        docx_files = list(source_path.glob("*.docx"))
        pptx_files = list(source_path.glob("*.pptx"))

        total_files = len(pdf_files) + len(docx_files) + len(pptx_files)
        print(f"   发现 {total_files} 个文档 (PDF:{len(pdf_files)}, DOCX:{len(docx_files)}, PPTX:{len(pptx_files)})")

        documents = []

        # 处理PDF
        for pdf_file in pdf_files:
            try:
                parser = PDFParser(str(pdf_file))
                docs = parser.to_documents(chunk_by="section")
                documents.extend(docs)
                print(f"   [+] {pdf_file.name} ({len(docs)}块)")
            except Exception as e:
                print(f"   [!]  {pdf_file.name}: {e}")

        # 处理DOCX
        for docx_file in docx_files:
            try:
                parser = DocxParser(str(docx_file))
                doc = parser.to_document()
                documents.append(doc)
                print(f"   [+] {docx_file.name}")
            except Exception as e:
                print(f"   [!]  {docx_file.name}: {e}")

        # 处理PPTX
        for pptx_file in pptx_files:
            try:
                parser = PptxParser(str(pptx_file))
                doc = parser.to_document()
                documents.append(doc)
                print(f"   [+] {pptx_file.name}")
            except Exception as e:
                print(f"   [!]  {pptx_file.name}: {e}")

        if documents:
            vm.add_documents(documents)
            print(f"   [OK] 成功导入 {len(documents)} 个文档块")

        return len(documents)

    def get_statistics(self) -> Dict[str, Any]:
        """获取所有数据库的统计信息"""
        stats = {}

        for db_key, config in self.databases.items():
            try:
                vm = self.create_database(db_key)
                all_docs = vm.get_all_documents()

                stats[db_key] = {
                    "name": config["name"],
                    "total_documents": len(all_docs),
                    "persist_dir": config["persist_dir"]
                }
            except Exception as e:
                stats[db_key] = {
                    "name": config["name"],
                    "error": str(e)
                }

        return stats


def main():
    """命令行入口"""
    manager = MultiDatabaseManager()

    print("=" * 60)
    print("保险数据库批量导入工具")
    print("=" * 60)

    # 1. 导入公众号文章
    try:
        count = manager.import_markdown_articles(
            source_dir="D:/公众号文章",
            db_key="articles"
        )
    except Exception as e:
        print(f"[X] 文章导入失败: {e}")

    # 2. 导入桌面资料库
    try:
        count = manager.import_office_documents(
            source_dir="C:/Users/jren3/Desktop/资料库",
            db_key="materials"
        )
    except Exception as e:
        print(f"[X] 资料导入失败: {e}")

    # 3. 显示统计
    print("\n" + "=" * 60)
    print("[STAT] 数据库统计")
    print("=" * 60)

    stats = manager.get_statistics()
    for db_key, info in stats.items():
        print(f"\n【{info['name']}】")
        if "error" in info:
            print(f"   状态: [X] {info['error']}")
        else:
            print(f"   文档数: {info['total_documents']}")
            print(f"   位置: {info['persist_dir']}")

    print("\n[OK] 所有数据库创建完成！")


if __name__ == "__main__":
    main()
