#!/usr/bin/env python3
"""
PDF文字提取脚本
从PDF文件中提取文字内容并转换为Markdown格式
"""

import fitz  # PyMuPDF
from pathlib import Path
import sys
import re


def extract_text_from_pdf(pdf_path, output_path):
    """
    从PDF文件提取文字并保存为Markdown

    Args:
        pdf_path: PDF文件路径
        output_path: 输出Markdown文件路径
    """
    print(f"Processing: {pdf_path}")

    try:
        # 打开PDF文件
        doc = fitz.open(pdf_path)

        # 获取文件名作为标题
        title = Path(pdf_path).stem
        print(f"  Pages: {len(doc)}")

        # 开始提取
        content = []
        content.append(f"# {title}\n\n")
        content.append(f"*来源: PDF文件*\n")
        content.append(f"*文件: {Path(pdf_path).name}*\n")
        content.append(f"*页数: {len(doc)}*\n\n")
        content.append("---\n\n")

        # 逐页提取
        for page_num, page in enumerate(doc, 1):
            # 提取文字
            text = page.get_text()

            if text.strip():
                # 添加页码标记（可选）
                # content.append(f"\n\n[Page {page_num}]\n\n")

                # 清洗文字
                text = clean_text(text)

                # 添加内容
                content.append(text)
                content.append("\n\n")

        # 关闭文档
        doc.close()

        # 合并内容
        full_text = ''.join(content)

        # 保存为Markdown
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_text)

        # 统计信息
        word_count = len(full_text.split())
        char_count = len(full_text)

        print(f"  [OK] Extracted {char_count:,} characters, {word_count:,} words")
        print(f"  [OK] Saved to: {output_path}")

        return {
            'success': True,
            'pages': len(doc),
            'chars': char_count,
            'words': word_count
        }

    except Exception as e:
        print(f"  [ERROR] {e}")
        return {
            'success': False,
            'error': str(e)
        }


def clean_text(text):
    """
    清洗文本：去除多余空白、特殊字符等
    """
    # 去除多余空行
    text = re.sub(r'\n\s*\n', '\n\n', text)

    # 去除行首行尾空白
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)

    # 去除多余空格
    text = re.sub(r' +', ' ', text)

    return text


def main():
    """主函数：批量处理所有PDF文件"""

    # 定义PDF文件路径（威斯科信）
    pdf_files = [
        # Wesco Letters
        ('data/letters/wesco_letters/001-1997-letters.pdf', 'data/processed/letters/wesco_1997.md'),
        ('data/letters/wesco_letters/002-1998-letters.pdf', 'data/processed/letters/wesco_1998.md'),
        ('data/letters/wesco_letters/003-1999-letters.pdf', 'data/processed/letters/wesco_1999.md'),
        ('data/letters/wesco_letters/004-2000-letters.pdf', 'data/processed/letters/wesco_2000.md'),
        ('data/letters/wesco_letters/005-2001-letters.pdf', 'data/processed/letters/wesco_2001.md'),
        ('data/letters/wesco_letters/006-2002-letters.pdf', 'data/processed/letters/wesco_2002.md'),
        ('data/letters/wesco_letters/007-2003-letters.pdf', 'data/processed/letters/wesco_2003.md'),
        ('data/letters/wesco_letters/008-2004-letters.pdf', 'data/processed/letters/wesco_2004.md'),
        ('data/letters/wesco_letters/009-2005-letters.pdf', 'data/processed/letters/wesco_2005.md'),
        ('data/letters/wesco_letters/010-2006-letters.pdf', 'data/processed/letters/wesco_2006.md'),
        ('data/letters/wesco_letters/011-2007-letters.pdf', 'data/processed/letters/wesco_2007.md'),
        ('data/letters/wesco_letters/012-2008-letters.pdf', 'data/processed/letters/wesco_2008.md'),
        ('data/letters/wesco_letters/013-2009-letters.pdf', 'data/processed/letters/wesco_2009.md'),
    ]

    # 创建输出目录
    for _, output_path in pdf_files:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # 处理每个PDF文件
    print("=" * 60)
    print("Wesco Letters PDF Text Extraction")
    print("=" * 60)

    results = []
    for pdf_path, output_path in pdf_files:
        if Path(pdf_path).exists():
            result = extract_text_from_pdf(pdf_path, output_path)
            results.append((pdf_path, result))
        else:
            print(f"[MISSING] File not found: {pdf_path}")
            results.append((pdf_path, {'success': False, 'error': 'File not found'}))

    # 总结
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)

    success_count = sum(1 for _, r in results if r.get('success'))
    total_count = len(results)

    print(f"Processed: {success_count}/{total_count} files")

    if success_count > 0:
        total_chars = sum(r.get('chars', 0) for _, r in results if r.get('success'))
        total_words = sum(r.get('words', 0) for _, r in results if r.get('success'))
        total_pages = sum(r.get('pages', 0) for _, r in results if r.get('success'))
        print(f"Total pages: {total_pages}")
        print(f"Total characters: {total_chars:,}")
        print(f"Total words: {total_words:,}")

    return 0 if success_count == total_count else 1


if __name__ == '__main__':
    sys.exit(main())
