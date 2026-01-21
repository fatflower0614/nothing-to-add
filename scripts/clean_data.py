#!/usr/bin/env python3
"""
数据深度清洗脚本
清理和优化提取的文本数据，为RAG系统做准备
"""

import re
from pathlib import Path
import sys
from datetime import datetime


class DataCleaner:
    """数据清洗器"""

    def __init__(self):
        self.stats = {
            'files_processed': 0,
            'chars_before': 0,
            'chars_after': 0,
            'replacements': 0,
        }

    def clean_text(self, text, metadata=None):
        """
        深度清洗文本

        Args:
            text: 原始文本
            metadata: 文件元数据（用于添加标题）

        Returns:
            清洗后的文本
        """
        original_length = len(text)

        # 1. 字符规范化
        text = self.normalize_chars(text)

        # 2. 删除表格边框线
        text = self.remove_table_borders(text)

        # 3. 删除无用内容（版权信息等）
        text = self.remove_boilerplate(text)

        # 4. 删除页码
        text = self.remove_page_numbers(text)

        # 5. 修复段落
        text = self.fix_paragraphs(text)

        # 6. 统一格式
        text = self.unify_format(text)

        # 7. 清理空白
        text = self.clean_whitespace(text)

        # 8. 添加元数据头部
        if metadata:
            text = self.add_metadata_header(text, metadata)

        new_length = len(text)

        self.stats['replacements'] += (original_length - new_length)

        return text

    def normalize_chars(self, text):
        """字符规范化：修复特殊引号和乱码"""

        # 智能引号 → 普通引号
        text = text.replace('"', '"')
        text = text.replace(''', "'")
        text = text.replace('"', '"')
        text = text.replace(''', "'")

        # 特殊乱码字符
        text = text.replace('Ï', ' ')      # 表格线
        text = text.replace('Ç', 'C')
        text = text.replace('ç', 'c')
        text = text.replace('ö', 'o')
        text = text.replace('ü', 'u')
        text = text.replace('ä', 'a')
        text = text.replace('ë', 'e')
        text = text.replace('ï', 'i')

        # 其他常见OCR错误
        text = text.replace('|', 'I')      # 有时|会被识别为I
        text = text.replace('[', '(')      # 括号统一
        text = text.replace(']', ')')

        return text

    def remove_table_borders(self, text):
        """删除表格边框线"""
        # 删除只包含表格线的行
        lines = text.split('\n')
        cleaned_lines = []

        for line in lines:
            # 如果一行主要是表格线字符，删除它
            if re.match(r'^[\sÏ\-|]+$', line):
                continue
            cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def remove_boilerplate(self, text):
        """删除样板内容（版权信息、ISBN等）"""

        # 要删除的段落
        boilerplate_patterns = [
            r'版权所有.*?侵权必究',
            r'ISBN[:：]\s*[\dX]+',
            r'出版时间[:：]\s*[\d\-]+',
            r'版权信息',
            r'书名[:：].*',
            r'著者[:：].*',
            r'编者[:：].*',
            r'译者[:：].*',
            r'中信出版集团.*',
        ]

        for pattern in boilerplate_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)

        return text

    def remove_page_numbers(self, text):
        """删除独立的页码"""
        # 删除单独一行的页码
        lines = text.split('\n')
        cleaned_lines = []

        for line in lines:
            # 跳过只包含数字的行（可能是页码）
            if re.match(r'^\s*\d+\s*$', line.strip()):
                continue
            # 删除行首的页码
            line = re.sub(r'^\d+\s+', '', line)
            cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def fix_paragraphs(self, text):
        """修复段落问题"""

        # 删除断行（把被断开的单词连接起来）
        # 例如：hello world → hello world
        text = re.sub(r'([a-z])\n([a-z])', r'\1\2', text)

        # 修复被分页打断的数字
        # 例如：$3, -> $3,
        #       507 -> 507
        text = re.sub(r'(\d),\n(\d)', r'\1,\2', text)
        text = re.sub(r'\$(\d+)\n(\d+)', r'$\1\2', text)

        return text

    def unify_format(self, text):
        """统一格式"""

        # 统一标题级别（将多个#改成合适的形式）
        # 章节标题
        text = re.sub(r'#{4,}\s*', '###', text)

        # 修复标题格式（去掉多余空格）
        text = re.sub(r'#+\s+', '# ', text)

        return text

    def clean_whitespace(self, text):
        """清理空白字符"""

        # 多个空行变成最多2个
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)

        # 删除行首行尾空白
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)

        # 删除段落内多余的空格
        text = re.sub(r' {3,}', ' ', text)

        return text

    def add_metadata_header(self, text, metadata):
        """添加元数据头部"""
        header = f"""---
source: {metadata.get('source', 'Unknown')}
type: {metadata.get('type', 'Document')}
year: {metadata.get('year', 'Unknown')}
title: {metadata.get('title', 'Unknown')}
processed: {datetime.now().strftime('%Y-%m-%d')}
---

"""
        return header + text


def clean_file(input_path, output_path, metadata):
    """清洗单个文件"""
    print(f"Cleaning: {Path(input_path).name}")

    try:
        # 读取文件
        with open(input_path, 'r', encoding='utf-8') as f:
            text = f.read()

        cleaner = DataCleaner()
        cleaner.stats['chars_before'] += len(text)

        # 清洗文本
        cleaned_text = cleaner.clean_text(text, metadata)

        cleaner.stats['chars_after'] += len(cleaned_text)
        cleaner.stats['files_processed'] += 1

        # 保存清洗后的文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_text)

        chars_removed = cleaner.stats['chars_before'] - cleaner.stats['chars_after']

        print(f"  [OK] Before: {cleaner.stats['chars_before']:,} chars")
        print(f"  [OK] After:  {cleaner.stats['chars_after']:,} chars")
        print(f"  [OK] Removed: {chars_removed:,} chars")
        print(f"  [OK] Saved to: {output_path}")

        return True

    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def main():
    """主函数"""

    print("=" * 70)
    print("Deep Data Cleaning - 数据深度清洗")
    print("=" * 70)
    print()
    print("This script will:")
    print("1. Normalize special characters")
    print("2. Remove table borders")
    print("3. Delete boilerplate content")
    print("4. Remove page numbers")
    print("5. Fix broken paragraphs")
    print("6. Unify formatting")
    print("7. Add metadata headers")
    print()
    print("=" * 70)
    print()

    # 定义文件及其元数据
    files_to_clean = [
        # Wesco Letters
        {
            'input': 'data/processed/letters/wesco_1997.md',
            'output': 'data/cleaned/letters/wesco_1997.md',
            'metadata': {
                'source': 'Wesco Financial Letter',
                'type': 'Shareholder Letter',
                'year': '1997',
                'title': 'Wesco Financial 1997 Letter to Shareholders'
            }
        },
        {
            'input': 'data/processed/letters/wesco_1998.md',
            'output': 'data/cleaned/letters/wesco_1998.md',
            'metadata': {
                'source': 'Wesco Financial Letter',
                'type': 'Shareholder Letter',
                'year': '1998',
                'title': 'Wesco Financial 1998 Letter to Shareholders'
            }
        },
        {
            'input': 'data/processed/letters/wesco_1999.md',
            'output': 'data/cleaned/letters/wesco_1999.md',
            'metadata': {
                'source': 'Wesco Financial Letter',
                'type': 'Shareholder Letter',
                'year': '1999',
                'title': 'Wesco Financial 1999 Letter to Shareholders'
            }
        },
        {
            'input': 'data/processed/letters/wesco_2000.md',
            'output': 'data/cleaned/letters/wesco_2000.md',
            'metadata': {
                'source': 'Wesco Financial Letter',
                'type': 'Shareholder Letter',
                'year': '2000',
                'title': 'Wesco Financial 2000 Letter to Shareholders'
            }
        },
        {
            'input': 'data/processed/letters/wesco_2001.md',
            'output': 'data/cleaned/letters/wesco_2001.md',
            'metadata': {
                'source': 'Wesco Financial Letter',
                'type': 'Shareholder Letter',
                'year': '2001',
                'title': 'Wesco Financial 2001 Letter to Shareholders'
            }
        },
        {
            'input': 'data/processed/letters/wesco_2002.md',
            'output': 'data/cleaned/letters/wesco_2002.md',
            'metadata': {
                'source': 'Wesco Financial Letter',
                'type': 'Shareholder Letter',
                'year': '2002',
                'title': 'Wesco Financial 2002 Letter to Shareholders'
            }
        },
        {
            'input': 'data/processed/letters/wesco_2003.md',
            'output': 'data/cleaned/letters/wesco_2003.md',
            'metadata': {
                'source': 'Wesco Financial Letter',
                'type': 'Shareholder Letter',
                'year': '2003',
                'title': 'Wesco Financial 2003 Letter to Shareholders'
            }
        },
        {
            'input': 'data/processed/letters/wesco_2004.md',
            'output': 'data/cleaned/letters/wesco_2004.md',
            'metadata': {
                'source': 'Wesco Financial Letter',
                'type': 'Shareholder Letter',
                'year': '2004',
                'title': 'Wesco Financial 2004 Letter to Shareholders'
            }
        },
        {
            'input': 'data/processed/letters/wesco_2005.md',
            'output': 'data/cleaned/letters/wesco_2005.md',
            'metadata': {
                'source': 'Wesco Financial Letter',
                'type': 'Shareholder Letter',
                'year': '2005',
                'title': 'Wesco Financial 2005 Letter to Shareholders'
            }
        },
        {
            'input': 'data/processed/letters/wesco_2006.md',
            'output': 'data/cleaned/letters/wesco_2006.md',
            'metadata': {
                'source': 'Wesco Financial Letter',
                'type': 'Shareholder Letter',
                'year': '2006',
                'title': 'Wesco Financial 2006 Letter to Shareholders'
            }
        },
        {
            'input': 'data/processed/letters/wesco_2007.md',
            'output': 'data/cleaned/letters/wesco_2007.md',
            'metadata': {
                'source': 'Wesco Financial Letter',
                'type': 'Shareholder Letter',
                'year': '2007',
                'title': 'Wesco Financial 2007 Letter to Shareholders'
            }
        },
        {
            'input': 'data/processed/letters/wesco_2008.md',
            'output': 'data/cleaned/letters/wesco_2008.md',
            'metadata': {
                'source': 'Wesco Financial Letter',
                'type': 'Shareholder Letter',
                'year': '2008',
                'title': 'Wesco Financial 2008 Letter to Shareholders'
            }
        },
        {
            'input': 'data/processed/letters/wesco_2009.md',
            'output': 'data/cleaned/letters/wesco_2009.md',
            'metadata': {
                'source': 'Wesco Financial Letter',
                'type': 'Shareholder Letter',
                'year': '2009',
                'title': 'Wesco Financial 2009 Letter to Shareholders'
            }
        },
        # Core Books
        {
            'input': 'data/processed/core/mungers_way.md',
            'output': 'data/cleaned/core/mungers_way.md',
            'metadata': {
                'source': 'Mungers Way',
                'type': 'Book',
                'year': '1987-2022',
                'title': 'Mungers Way: Charlie Munger Shareholder Meetings 1987-2022'
            }
        },
        {
            'input': 'data/processed/core/poor_richards_almanack.md',
            'output': 'data/cleaned/core/poor_richards_almanack.md',
            'metadata': {
                'source': 'Poor Richards Almanack',
                'type': 'Book',
                'year': '1700-1758',
                'title': 'Poor Richards Almanack by Benjamin Franklin'
            }
        },
        {
            'input': 'data/processed/core/snowball_buffett.md',
            'output': 'data/cleaned/core/snowball_buffett.md',
            'metadata': {
                'source': 'The Snowball',
                'type': 'Biography',
                'year': '2008',
                'title': 'The Snowball: Warren Buffett and the Business of Life'
            }
        },
        # Recommended Books
        {
            'input': 'data/processed/recommended/common_stocks_uncommon_profits.md',
            'output': 'data/cleaned/recommended/common_stocks_uncommon_profits.md',
            'metadata': {
                'source': 'Common Stocks and Uncommon Profits',
                'type': 'Book',
                'year': '1958',
                'title': 'Common Stocks and Uncommon Profits by Philip Fisher'
            }
        },
        {
            'input': 'data/processed/recommended/guns_germs_steel.md',
            'output': 'data/cleaned/recommended/guns_germs_steel.md',
            'metadata': {
                'source': 'Guns Germs and Steel',
                'type': 'Book',
                'year': '1997',
                'title': 'Guns, Germs, and Steel by Jared Diamond'
            }
        },
        {
            'input': 'data/processed/recommended/influence.md',
            'output': 'data/cleaned/recommended/influence.md',
            'metadata': {
                'source': 'Influence',
                'type': 'Book',
                'year': '1984',
                'title': 'Influence: The Psychology of Persuasion by Robert Cialdini'
            }
        },
        {
            'input': 'data/processed/recommended/thinking_fast_slow.md',
            'output': 'data/cleaned/recommended/thinking_fast_slow.md',
            'metadata': {
                'source': 'Thinking Fast and Slow',
                'type': 'Book',
                'year': '2011',
                'title': 'Thinking, Fast and Slow by Daniel Kahneman'
            }
        },
    ]

    # 创建输出目录
    for file_info in files_to_clean:
        Path(file_info['output']).parent.mkdir(parents=True, exist_ok=True)

    # 清洗所有文件
    results = []
    for file_info in files_to_clean:
        if Path(file_info['input']).exists():
            success = clean_file(
                file_info['input'],
                file_info['output'],
                file_info['metadata']
            )
            results.append((file_info['input'], success))
        else:
            print(f"[MISSING] {file_info['input']}")
            results.append((file_info['input'], False))

    # 总结
    print()
    print("=" * 70)
    print("Cleaning Summary")
    print("=" * 70)

    success_count = sum(1 for _, s in results if s)
    total_count = len(results)

    print(f"Processed: {success_count}/{total_count} files")

    return 0 if success_count == total_count else 1


if __name__ == '__main__':
    sys.exit(main())
