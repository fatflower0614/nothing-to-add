#!/usr/bin/env python3
"""
EPUB文字提取脚本
从EPUB文件中提取文字内容并转换为Markdown格式
"""

import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import re
from pathlib import Path
import sys


def extract_text_from_epub(epub_path, output_path):
    """
    从EPUB文件提取文字并保存为Markdown

    Args:
        epub_path: EPUB文件路径
        output_path: 输出Markdown文件路径
    """
    print(f"Processing: {epub_path}")

    try:
        # 读取EPUB文件
        book = epub.read_epub(epub_path)

        # 获取书名
        title = book.get_metadata('DC', 'title')[0][0] if book.get_metadata('DC', 'title') else Path(epub_path).stem
        print(f"  Title: {title}")

        # 提取所有章节内容
        content = []
        content.append(f"# {title}\n\n")
        content.append(f"*来源: EPUB文件*\n")
        content.append(f"*文件: {Path(epub_path).name}*\n\n")
        content.append("---\n\n")

        # 遍历所有项目
        chapter_num = 0
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                # 解析HTML内容
                soup = BeautifulSoup(item.get_content(), 'html.parser')

                # 提取文字
                text = soup.get_text()

                # 清洗文字
                text = clean_text(text)

                if text.strip():
                    chapter_num += 1
                    # 添加章节标题
                    if chapter_num > 1:
                        content.append(f"\n\n## Chapter {chapter_num}\n\n")
                    content.append(text)
                    content.append("\n\n")

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
            'title': title,
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

    # 去除特殊字符（保留中英文、标点）
    # text = re.sub(r'[^\w\s\u4e00-\u9fff\u3000-\u303f\uff00-\uffef.,!?;:()""''\-%]', ' ', text)

    # 去除多余空格
    text = re.sub(r' +', ' ', text)

    return text


def main():
    """主函数：批量处理所有EPUB文件"""

    # 定义EPUB文件路径
    epub_files = [
        # Core books
        ('data/books/core/Mungers_Way.epub', 'data/processed/core/mungers_way.md'),
        ('data/books/core/Poor_Richards_Almanack.epub', 'data/processed/core/poor_richards_almanack.md'),
        ('data/books/core/The_Snowball.epub', 'data/processed/core/snowball_buffett.md'),

        # Recommended books
        ('data/books/recommended/Common_Stocks_and_Uncommon_Profits.epub', 'data/processed/recommended/common_stocks_uncommon_profits.md'),
        ('data/books/recommended/Guns_Germs_and_Steel.epub', 'data/processed/recommended/guns_germs_steel.md'),
        ('data/books/recommended/Influence.epub', 'data/processed/recommended/influence.md'),
        ('data/books/recommended/Thinking_Fast_and_Slow.epub', 'data/processed/recommended/thinking_fast_slow.md'),
    ]

    # 创建输出目录
    for _, output_path in epub_files:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # 处理每个EPUB文件
    print("=" * 60)
    print("EPUB Text Extraction")
    print("=" * 60)

    results = []
    for epub_path, output_path in epub_files:
        if Path(epub_path).exists():
            result = extract_text_from_epub(epub_path, output_path)
            results.append((epub_path, result))
        else:
            print(f"[MISSING] File not found: {epub_path}")
            results.append((epub_path, {'success': False, 'error': 'File not found'}))

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
        print(f"Total characters: {total_chars:,}")
        print(f"Total words: {total_words:,}")

    return 0 if success_count == total_count else 1


if __name__ == '__main__':
    sys.exit(main())
