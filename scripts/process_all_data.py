#!/usr/bin/env python3
"""
数据处理主脚本
统一运行所有数据提取任务
"""

import subprocess
import sys
from pathlib import Path


def run_script(script_name):
    """运行脚本并返回结果"""
    script_path = Path(__file__).parent / script_name
    print(f"\n{'='*60}")
    print(f"Running: {script_name}")
    print(f"{'='*60}\n")

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=Path(__file__).parent.parent,
            capture_output=False,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error running {script_name}: {e}")
        return False


def main():
    """主函数"""

    print("="*60)
    print("Nothing to Add - Data Processing Pipeline")
    print("="*60)
    print("\nThis script will:")
    print("1. Extract text from EPUB files (7 books)")
    print("2. Extract text from PDF files (13 Wesco letters)")
    print("3. Extract text from MOBI files (1 book)")
    print("\nOutput will be saved to: data/processed/")
    print("="*60)

    # 确认开始
    response = input("\nStart processing? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled.")
        return 0

    # 创建输出目录
    Path("data/processed").mkdir(parents=True, exist_ok=True)
    Path("data/processed/core").mkdir(parents=True, exist_ok=True)
    Path("data/processed/recommended").mkdir(parents=True, exist_ok=True)
    Path("data/processed/letters").mkdir(parents=True, exist_ok=True)

    # 运行各个提取脚本
    scripts = [
        'extract_epub.py',
        'extract_pdf.py',
        'extract_mobi.py',
    ]

    results = {}
    for script in scripts:
        success = run_script(script)
        results[script] = success

    # 总结
    print("\n" + "="*60)
    print("Processing Complete!")
    print("="*60)

    for script, success in results.items():
        status = "✓ Success" if success else "✗ Failed"
        print(f"  {script}: {status}")

    # 检查输出文件
    print("\n" + "="*60)
    print("Generated Files:")
    print("="*60)

    output_files = list(Path("data/processed").rglob("*.md"))
    if output_files:
        for f in sorted(output_files):
            size_kb = f.stat().st_size / 1024
            print(f"  {f.relative_to('data/processed')}: {size_kb:.1f} KB")
    else:
        print("  No files generated. Check for errors above.")

    print("\n" + "="*60)
    print("Next Steps:")
    print("="*60)
    print("1. Review extracted text in data/processed/")
    print("2. Run data cleaning and formatting")
    print("3. Build RAG system")
    print("="*60)

    return 0


if __name__ == '__main__':
    sys.exit(main())
