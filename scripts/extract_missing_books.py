#!/usr/bin/env python3
"""
提取所有遗漏的重要书籍
解决：穷查理宝典、聪明的投资者、证券分析等核心数据缺失问题
"""

import fitz  # PyMuPDF
from pathlib import Path
import sys
import re


def extract_text_from_pdf(pdf_path, output_path):
    """从PDF提取文字"""
    print(f"\n{'='*60}")
    print(f"Processing: {Path(pdf_path).name}")
    print(f"{'='*60}")

    try:
        doc = fitz.open(pdf_path)
        title = Path(pdf_path).stem

        print(f"  Pages: {len(doc)}")
        print(f"  Extracting text...")

        content = []
        content.append(f"# {title}\n\n")
        content.append(f"*来源: PDF书籍*\n")
        content.append(f"*文件: {Path(pdf_path).name}*\n")
        content.append(f"*页数: {len(doc)}*\n\n")
        content.append("---\n\n")

        # 逐页提取
        for page_num, page in enumerate(doc, 1):
            if page_num % 50 == 0:
                print(f"  Progress: {page_num}/{len(doc)} pages")

            text = page.get_text()

            if text.strip():
                # 清洗文字
                text = clean_text(text)
                content.append(text)
                content.append("\n\n")

        doc.close()

        # 保存
        full_text = ''.join(content)
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_text)

        # 统计
        word_count = len(full_text.split())
        char_count = len(full_text)

        print(f"  [OK] Extracted {char_count:,} characters, {word_count:,} words")
        print(f"  [OK] Saved to: {output_path}")

        return {'success': True, 'pages': len(doc), 'chars': char_count, 'words': word_count}

    except Exception as e:
        print(f"  [ERROR] {e}")
        return {'success': False, 'error': str(e)}


def clean_text(text):
    """清洗文本"""
    # 去除多余空行
    text = re.sub(r'\n\s*\n', '\n\n', text)
    # 去除行首行尾空白
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    # 去除多余空格
    text = re.sub(r' +', ' ', text)
    return text


def main():
    """提取所有遗漏的书籍"""

    # 遗漏的重要书籍
    missing_books = [
        # 核心书籍（最重要的）
        ('data/books/core/穷查理宝典.pdf', 'data/cleaned/core/Poor_Charlies_Almanack.md', '[*****CORE*****]'),
        ('data/books/core/The_Intelligent_Investor.pdf', 'data/cleaned/core/The_Intelligent_Investor.md', '[*****CORE*****]'),
        ('data/books/core/Security_Analysis.pdf', 'data/cleaned/core/Security_Analysis.md', '[*****CORE*****]'),
        ('data/books/core/Franklin_Autobiography.pdf', 'data/cleaned/core/Franklin_Autobiography.md', '[*****CORE*****]'),

        # 推荐书籍
        ('data/books/recommended/The_Most_ImportantThing.pdf', 'data/cleaned/recommended/The_Most_ImportantThing.md', '[****IMPORTANT****]'),
        ('data/books/recommended/Reminiscences_of_a_Stock_Operator.pdf', 'data/cleaned/recommended/Reminiscences_of_a_Stock_Operator.md', '[***GOOD***]'),
        ('data/books/recommended/The_Crowd.pdf', 'data/cleaned/recommended/The_Crowd.md', '[***GOOD***]'),
        ('data/books/recommended/Index_Fund_Guide.pdf', 'data/cleaned/recommended/Index_Fund_Guide.md', '[**OK**]'),
    ]

    print("="*60)
    print("提取遗漏的重要书籍")
    print("="*60)
    print("\n待提取文件列表：\n")

    for pdf_path, output_path, importance in missing_books:
        exists = "[OK]" if Path(pdf_path).exists() else "[MISSING]"
        print(f"  {exists} {importance} {Path(pdf_path).name}")

    print("\n" + "="*60)
    print("开始提取...")
    print("="*60)

    results = []
    success_count = 0

    for pdf_path, output_path, importance in missing_books:
        if not Path(pdf_path).exists():
            print(f"\n[X] 跳过（文件不存在）: {pdf_path}")
            results.append((pdf_path, {'success': False, 'error': 'File not found'}))
            continue

        result = extract_text_from_pdf(pdf_path, output_path)
        results.append((pdf_path, result))

        if result.get('success'):
            success_count += 1

    # 总结
    print("\n" + "="*60)
    print("提取总结")
    print("="*60)
    print(f"\n成功: {success_count}/{len(missing_books)} 本书籍\n")

    if success_count > 0:
        total_chars = sum(r.get('chars', 0) for _, r in results if r.get('success'))
        total_words = sum(r.get('words', 0) for _, r in results if r.get('success'))
        total_pages = sum(r.get('pages', 0) for _, r in results if r.get('success'))

        print(f"总页数: {total_pages:,}")
        print(f"总字符数: {total_chars:,}")
        print(f"总词数: {total_words:,}")

    print("\n下一步：运行 python scripts/build_rag.py 重新构建向量数据库")
    print("="*60)

    return 0 if success_count == len(missing_books) else 1


if __name__ == '__main__':
    sys.exit(main())
