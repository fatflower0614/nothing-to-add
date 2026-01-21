#!/usr/bin/env python3
"""
MOBI文字提取脚本（简化版）
从MOBI文件中提取文字内容

注意：MOBI格式较复杂，此脚本使用简化方法
如果提取失败，建议使用Calibre转换工具
"""

import subprocess
from pathlib import Path
import sys


def extract_text_from_mobi(mobi_path, output_path):
    """
    从MOBI文件提取文字

    方法：使用ebooklib（如果支持）或建议用户用Calibre

    Args:
        mobi_path: MOBI文件路径
        output_path: 输出Markdown文件路径
    """
    print(f"Processing: {mobi_path}")

    try:
        # 尝试使用ebooklib读取
        import ebooklib
        from ebooklib import epub
        from bs4 import BeautifulSoup

        # MOBI文件可以用ebooklib读取
        # 但可能需要先转换为EPUB

        # 简化方法：尝试直接读取
        # 如果失败，建议用户使用Calibre

        # 这里我们用Python的zipfile尝试读取（MOBI可能是类似格式）
        import zipfile

        try:
            # 尝试作为ZIP打开（有些MOBI是压缩格式）
            with zipfile.ZipFile(mobi_path, 'r') as zip_ref:
                # 读取第一个HTML文件
                html_files = [f for f in zip_ref.namelist() if f.endswith('.html') or f.endswith('.htm')]

                if html_files:
                    content = []
                    title = Path(mobi_path).stem

                    content.append(f"# {title}\n\n")
                    content.append(f"*来源: MOBI文件*\n")
                    content.append(f"*文件: {Path(mobi_path).name}*\n\n")
                    content.append("---\n\n")

                    for html_file in html_files[:10]:  # 只读前10个文件
                        with zip_ref.open(html_file) as f:
                            html_content = f.read().decode('utf-8', errors='ignore')
                            soup = BeautifulSoup(html_content, 'html.parser')
                            text = soup.get_text()
                            content.append(text)
                            content.append("\n\n")

                    full_text = ''.join(content)

                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(full_text)

                    word_count = len(full_text.split())
                    char_count = len(full_text)

                    print(f"  ✓ Extracted {char_count:,} characters, {word_count:,} words")
                    print(f"  ✓ Saved to: {output_path}")

                    return {
                        'success': True,
                        'chars': char_count,
                        'words': word_count
                    }

        except Exception as zip_error:
            print(f"  ZIP method failed: {zip_error}")

        # 如果ZIP方法失败，建议使用Calibre
        print(f"  ⚠ MOBI extraction is complex")
        print(f"  ⚠ Consider using Calibre:")
        print(f"     ebook-convert \"{mobi_path}\" \"{output_path.replace('.md', '.epub')}\"")
        print(f"     Then use extract_epub.py")

        return {
            'success': False,
            'error': 'MOBI format requires Calibre'
        }

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def main():
    """主函数：处理MOBI文件"""

    # 定义MOBI文件路径
    mobi_files = [
        ('data/books/core/Charlie_Munger_Biography.mobi', 'data/processed/core/charlie_munger_biography.md'),
    ]

    # 创建输出目录
    for _, output_path in mobi_files:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # 处理
    print("=" * 60)
    print("MOBI Text Extraction")
    print("=" * 60)
    print("Note: MOBI format is complex. If extraction fails,")
    print("      use Calibre: ebook-convert input.mobi output.epub")
    print("=" * 60)
    print()

    results = []
    for mobi_path, output_path in mobi_files:
        if Path(mobi_path).exists():
            result = extract_text_from_mobi(mobi_path, output_path)
            results.append((mobi_path, result))
        else:
            print(f"✗ File not found: {mobi_path}")
            results.append((mobi_path, {'success': False, 'error': 'File not found'}))

    return 0


if __name__ == '__main__':
    sys.exit(main())
