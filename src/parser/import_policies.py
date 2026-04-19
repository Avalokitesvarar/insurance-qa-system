"""
批量导入PDF条款到向量库
"""
import sys
sys.path.append('.')

from pathlib import Path
from typing import List
from src.parser.pdf_parser import PDFParser
from src.parser.text_splitter import InsuranceTextSplitter
from src.retriever.vector_store import VectorStoreManager
from src.retriever.bm25_retriever import BM25Retriever
from config.settings import settings


class PolicyImporter:
    """保险条款导入器"""

    def __init__(self):
        self.vm = VectorStoreManager()
        self.vm.init_vectorstore()
        self.splitter = InsuranceTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            strategy="semantic"
        )

    def import_pdf(
        self,
        pdf_path: str,
        product_name: str = None,
        company: str = None
    ) -> int:
        """
        导入单个PDF条款

        Args:
            pdf_path: PDF文件路径
            product_name: 产品名称
            company: 保险公司

        Returns:
            导入的文档块数量
        """
        print(f"\n📄 解析PDF: {pdf_path}")

        # 解析PDF
        parser = PDFParser(pdf_path)

        # 提取元数据
        metadata = {
            "type": "policy",
        }
        if product_name:
            metadata["product_name"] = product_name
        if company:
            metadata["company"] = company

        # 转换为文档
        documents = parser.to_documents(chunk_by="section", metadata=metadata)
        print(f"   提取到 {len(documents)} 个章节/表格")

        # 智能分块
        split_docs = self.splitter.split_documents(documents)
        print(f"   分块后共 {len(split_docs)} 个文档块")

        # 添加到向量库
        self.vm.add_documents(split_docs)

        return len(split_docs)

    def import_directory(self, directory: str) -> int:
        """
        批量导入目录下的所有PDF

        Args:
            directory: 目录路径

        Returns:
            总共导入的文档块数量
        """
        dir_path = Path(directory)
        if not dir_path.exists():
            raise FileNotFoundError(f"目录不存在: {directory}")

        pdf_files = list(dir_path.glob("*.pdf"))
        print(f"\n🗂️  发现 {len(pdf_files)} 个PDF文件")

        total_chunks = 0
        for pdf_file in pdf_files:
            try:
                # 从文件名推断产品名
                product_name = pdf_file.stem

                chunks = self.import_pdf(
                    str(pdf_file),
                    product_name=product_name
                )
                total_chunks += chunks

            except Exception as e:
                print(f"   ❌ 导入失败: {e}")
                continue

        print(f"\n✅ 批量导入完成，共 {total_chunks} 个文档块")
        return total_chunks

    def get_statistics(self) -> dict:
        """获取导入统计信息"""
        all_docs = self.vm.get_all_documents()

        stats = {
            "total_documents": len(all_docs),
            "by_type": {},
            "by_product": {},
            "by_section": {}
        }

        for doc in all_docs:
            # 按类型统计
            doc_type = doc.metadata.get("type", "unknown")
            stats["by_type"][doc_type] = stats["by_type"].get(doc_type, 0) + 1

            # 按产品统计
            product = doc.metadata.get("product_name", "unknown")
            stats["by_product"][product] = stats["by_product"].get(product, 0) + 1

            # 按章节统计
            section = doc.metadata.get("section", "unknown")
            stats["by_section"][section] = stats["by_section"].get(section, 0) + 1

        return stats


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="导入保险条款PDF到向量库")
    parser.add_argument("path", help="PDF文件或目录路径")
    parser.add_argument("--product", help="产品名称", default=None)
    parser.add_argument("--company", help="保险公司", default=None)
    parser.add_argument("--stats", action="store_true", help="显示统计信息")

    args = parser.parse_args()

    importer = PolicyImporter()

    path = Path(args.path)
    if path.is_file():
        # 导入单个文件
        importer.import_pdf(str(path), args.product, args.company)
    elif path.is_dir():
        # 批量导入
        importer.import_directory(str(path))
    else:
        print(f"❌ 路径不存在: {args.path}")
        return

    # 显示统计
    if args.stats:
        print("\n📊 数据库统计:")
        stats = importer.get_statistics()
        print(f"   总文档数: {stats['total_documents']}")
        print(f"   按类型: {stats['by_type']}")
        print(f"   按产品: {stats['by_product']}")


if __name__ == "__main__":
    main()
