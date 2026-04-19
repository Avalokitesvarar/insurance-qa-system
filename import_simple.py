"""
简化版文章导入工具（不使用向量嵌入）
"""
import sys
sys.path.append('.')

from pathlib import Path
from src.parser.markdown_parser import MarkdownParser

def import_articles_simple(source_dir: str):
    """简单导入Markdown文章"""
    print("=" * 60)
    print("公众号文章导入工具（简化版）")
    print("=" * 60)

    source_path = Path(source_dir)
    if not source_path.exists():
        print(f"[X] 目录不存在: {source_dir}")
        return

    md_files = list(source_path.glob("*.md"))
    print(f"\n[*] 发现 {len(md_files)} 个Markdown文件")
    print(f"    源目录: {source_dir}\n")

    articles = []
    for i, md_file in enumerate(md_files, 1):
        try:
            parser = MarkdownParser(str(md_file))
            parsed = parser.parse()
            articles.append(parsed)

            print(f"[{i}/{len(md_files)}] {parsed['title']}")
            if parsed['tags']:
                print(f"        标签: {', '.join(parsed['tags'])}")
            if parsed['product_mentions']:
                print(f"        提及产品: {', '.join(parsed['product_mentions'][:3])}")

        except Exception as e:
            print(f"[!] 解析失败 {md_file.name}: {e}")

    # 统计
    print("\n" + "=" * 60)
    print("[STAT] 导入统计")
    print("=" * 60)
    print(f"总文章数: {len(articles)}")

    # 按标签统计
    tag_count = {}
    for article in articles:
        for tag in article['tags']:
            tag_count[tag] = tag_count.get(tag, 0) + 1

    if tag_count:
        print("\n标签分布:")
        for tag, count in sorted(tag_count.items(), key=lambda x: x[1], reverse=True):
            print(f"  {tag}: {count}篇")

    # 产品提及统计
    product_count = {}
    for article in articles:
        for product in article['product_mentions']:
            product_count[product] = product_count.get(product, 0) + 1

    if product_count:
        print("\n热门产品（提及次数）:")
        for product, count in sorted(product_count.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {product}: {count}次")

    print(f"\n[OK] 文章解析完成！")
    print(f"     数据已保存到内存，可用于后续分析")

if __name__ == "__main__":
    import_articles_simple("D:/公众号文章")
