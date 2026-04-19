"""
测试PDF解析功能
"""
import sys
sys.path.append('.')

from src.parser.pdf_parser import PDFParser
from src.parser.text_splitter import InsuranceTextSplitter, TableExtractor


def create_sample_pdf():
    """创建示例PDF用于测试"""
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    # 注册中文字体（如果有的话）
    try:
        pdfmetrics.registerFont(TTFont('SimSun', 'simsun.ttc'))
        font_name = 'SimSun'
    except:
        font_name = 'Helvetica'

    pdf_path = "data/raw/sample_policy.pdf"

    c = canvas.Canvas(pdf_path, pagesize=A4)
    c.setFont(font_name, 12)

    # 第一页
    y = 800
    c.drawString(50, y, "XX保险公司重大疾病保险条款")
    y -= 40

    c.drawString(50, y, "第一条 保险责任")
    y -= 20
    c.drawString(70, y, "在本合同保险期间内，本公司承担以下保险责任：")
    y -= 20
    c.drawString(70, y, "1. 重大疾病保险金：被保险人初次确诊重大疾病，赔付100%基本保额")
    y -= 20
    c.drawString(70, y, "2. 轻症疾病保险金：被保险人初次确诊轻症疾病，赔付30%基本保额")

    y -= 40
    c.drawString(50, y, "第二条 责任免除")
    y -= 20
    c.drawString(70, y, "因下列情形之一导致被保险人患重大疾病的，本公司不承担保险责任：")
    y -= 20
    c.drawString(70, y, "1. 投保人对被保险人的故意杀害、故意伤害")
    y -= 20
    c.drawString(70, y, "2. 被保险人故意犯罪或抗拒依法采取的刑事强制措施")

    c.showPage()
    c.save()

    print(f"✓ 创建示例PDF: {pdf_path}")
    return pdf_path


def test_pdf_parser():
    """测试PDF解析"""
    print("=" * 60)
    print("测试 1: PDF解析")
    print("=" * 60)

    # 创建示例PDF
    pdf_path = create_sample_pdf()

    # 解析
    parser = PDFParser(pdf_path)
    result = parser.parse()

    print(f"\n文件名: {result['file_name']}")
    print(f"页数: {len(result['pages'])}")
    print(f"表格数: {len(result['tables'])}")
    print(f"章节数: {len(result['sections'])}")

    print("\n提取的章节:")
    for section_name in result['sections'].keys():
        print(f"  - {section_name}")

    print("\n全文预览（前500字符）:")
    print(result['full_text'][:500])


def test_text_splitter():
    """测试文本分块"""
    print("\n" + "=" * 60)
    print("测试 2: 智能分块")
    print("=" * 60)

    sample_text = """
第一条 保险责任
在本合同保险期间内，本公司承担以下保险责任：
1. 重大疾病保险金：被保险人初次确诊重大疾病，赔付100%基本保额
2. 轻症疾病保险金：被保险人初次确诊轻症疾病，赔付30%基本保额

第二条 责任免除
因下列情形之一导致被保险人患重大疾病的，本公司不承担保险责任：
1. 投保人对被保险人的故意杀害、故意伤害
2. 被保险人故意犯罪或抗拒依法采取的刑事强制措施
"""

    splitter = InsuranceTextSplitter(chunk_size=200, strategy="semantic")
    chunks = splitter._split_by_clauses(sample_text)

    print(f"\n分块数量: {len(chunks)}")
    for i, chunk in enumerate(chunks, 1):
        print(f"\n--- 块 {i} ---")
        print(chunk[:100] + "..." if len(chunk) > 100 else chunk)


def test_table_extractor():
    """测试表格提取"""
    print("\n" + "=" * 60)
    print("测试 3: 表格提取")
    print("=" * 60)

    sample_text = """
保障项目表：
重大疾病 50万元 120种重疾，赔付100%基本保额
中症疾病 30万元 20种中症，赔付60%基本保额
轻症疾病 15万元 40种轻症，赔付30%基本保额

保费表：
30岁 5280元
40岁 8650元
50岁 15200元
"""

    # 提取保障项
    coverages = TableExtractor.extract_coverage_table(sample_text)
    print("\n提取的保障项:")
    for cov in coverages:
        print(f"  - {cov['name']}: {cov['amount']} ({cov['description']})")

    # 提取保费
    premiums = TableExtractor.extract_premium_table(sample_text)
    print("\n提取的保费:")
    for prem in premiums:
        print(f"  - {prem['age']}岁: {prem['price']}元")


if __name__ == "__main__":
    print("🧪 开始测试PDF解析模块...\n")

    try:
        test_pdf_parser()
        test_text_splitter()
        test_table_extractor()

        print("\n" + "=" * 60)
        print("✅ 所有测试完成！")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
