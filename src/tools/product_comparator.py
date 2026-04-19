"""
产品对比工具
结构化对比，避免LLM幻觉
"""
from typing import List, Dict, Any
import json


class ProductComparator:
    """产品对比工具"""

    def __init__(self, retriever):
        self.retriever = retriever

    def compare(
        self,
        product_names: List[str],
        dimensions: List[str] = None
    ) -> Dict[str, Any]:
        """
        结构化产品对比

        Args:
            product_names: 产品名称列表
            dimensions: 对比维度

        Returns:
            结构化对比结果
        """
        dimensions = dimensions or ["保障内容", "保费", "产品特色", "责任免除"]

        # 1. 检索产品信息
        products_data = []
        for name in product_names:
            docs = self.retriever.get_relevant_documents(f"产品名称：{name}")
            if docs:
                products_data.append(self._extract_product_info(docs[0]))

        if len(products_data) < 2:
            return {"error": "未找到足够的产品信息进行对比"}

        # 2. 构建对比表格
        comparison_table = self._build_comparison_table(products_data, dimensions)

        # 3. 生成对比摘要
        summary = self._generate_summary(products_data, dimensions)

        return {
            "products": products_data,
            "comparison_table": comparison_table,
            "summary": summary,
            "dimensions": dimensions
        }

    def _extract_product_info(self, doc) -> Dict[str, Any]:
        """从文档中提取产品信息"""
        metadata = doc.metadata
        content = doc.page_content

        # 解析内容
        info = {
            "product_id": metadata.get("product_id", ""),
            "name": metadata.get("product_name", ""),
            "company": metadata.get("company", ""),
            "type": metadata.get("product_type", ""),
            "content": content
        }

        # 解析保障内容
        if "保障内容：" in content:
            coverages_section = content.split("保障内容：")[1].split("\n产品特色")[0]
            info["coverages"] = [line.strip() for line in coverages_section.split("\n") if line.strip()]

        # 解析产品特色
        if "产品特色：" in content:
            features_section = content.split("产品特色：")[1].split("\n责任免除")[0]
            info["features"] = features_section.strip()

        # 解析责任免除
        if "责任免除：" in content:
            exclusions_section = content.split("责任免除：")[1]
            info["exclusions"] = exclusions_section.strip()

        return info

    def _build_comparison_table(
        self,
        products: List[Dict],
        dimensions: List[str]
    ) -> str:
        """构建Markdown对比表格"""
        # 表头
        headers = ["对比项"] + [p["name"] for p in products]
        table = "| " + " | ".join(headers) + " |\n"
        table += "| " + " | ".join(["---"] * len(headers)) + " |\n"

        # 维度映射
        dimension_map = {
            "保障内容": "coverages",
            "产品特色": "features",
            "责任免除": "exclusions",
            "保险公司": "company",
            "产品类型": "type"
        }

        # 填充数据
        for dim in dimensions:
            row = [dim]
            field = dimension_map.get(dim, dim.lower())

            for product in products:
                value = product.get(field, "")
                if isinstance(value, list):
                    value = "<br>".join(value[:3])  # 只显示前3项
                elif not value:
                    value = "-"
                row.append(value)

            table += "| " + " | ".join(row) + " |\n"

        return table

    def _generate_summary(
        self,
        products: List[Dict],
        dimensions: List[str]
    ) -> str:
        """生成对比摘要"""
        summary_parts = []

        # 基本信息
        summary_parts.append(f"共对比 {len(products)} 款产品：")
        for p in products:
            summary_parts.append(f"- {p['name']}（{p['company']}）")

        # 对比维度
        summary_parts.append(f"\n对比维度：{', '.join(dimensions)}")

        return "\n".join(summary_parts)

    def format_for_llm(self, comparison_result: Dict[str, Any]) -> str:
        """
        格式化对比结果供LLM分析

        Args:
            comparison_result: compare()方法的返回结果

        Returns:
            格式化的文本，可直接传给LLM
        """
        if "error" in comparison_result:
            return comparison_result["error"]

        output = []
        output.append("# 产品对比分析\n")
        output.append(comparison_result["summary"])
        output.append("\n## 详细对比\n")
        output.append(comparison_result["comparison_table"])

        return "\n".join(output)
