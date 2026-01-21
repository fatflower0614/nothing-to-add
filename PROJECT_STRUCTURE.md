# 项目结构说明

```
nothing-to-add/
├── data/                          # 数据目录
│   ├── books/                    # 原始书籍（EPUB/PDF/MOBI）
│   ├── letters/                  # 原始股东信
│   │   ├── shareholder_letters/   # 巴菲特致股东信（1965-2024）
│   │   └── wesco_letters/         # 威斯科金融信（PDF）
│   ├── processed/                # 提取的文字（Markdown）
│   │   ├── core/                 # 核心书籍
│   │   ├── letters/              # 威斯科信
│   │   └── recommended/          # 推荐书籍
│   ├── cleaned/                  # 清洗后的数据
│   │   ├── core/
│   │   ├── letters/
│   │   └── recommended/
│   └── chroma/                   # 向量数据库
│
├── rag/                          # RAG系统核心模块
│   ├── __init__.py
│   ├── embeddings.py             # 文字转向量
│   ├── vector_store.py           # 向量数据库管理
│   ├── retriever.py              # 检索器
│   ├── generator.py              # AI生成答案（支持GLM）
│   ├── pipeline.py               # 完整RAG流程
│   └── prompts.py                # 系统提示词
│
├── scripts/                      # 数据处理脚本
│   ├── extract_epub.py           # EPUB提取
│   ├── extract_pdf.py            # PDF提取
│   ├── extract_mobi.py           # MOBI提取
│   ├── process_all_data.py       # 批量处理
│   ├── clean_data.py             # 数据清洗
│   └── build_rag.py              # 构建向量数据库
│
├── tests/                        # 测试脚本
│   ├── test_rag.py               # RAG系统测试
│   ├── test_new_style.py         # 新风格测试
│   ├── test_career_advice.py     # 职业建议测试
│   ├── test_moat.py              # 护城河问题测试
│   └── test_moat_cn.py           # 护城河问题测试（中文）
│
├── docs/                         # 项目文档
│   ├── planning/                 # 开发计划文档
│   │   ├── 00-项目总览README.md
│   │   ├── 01-产品需求文档RPD.md
│   │   ├── 02-技术术语解释.md
│   │   ├── 03-技术选型文档.md
│   │   └── 04-完整开发计划.md
│   └── reports/                  # 开发报告
│       ├── 数据处理完成报告.md
│       ├── 数据来源分析报告.md
│       └── 数据清洗完成报告.md
│
├── api/                          # API接口（未来）
│   └── (待开发)
│
├── .env                          # 环境变量配置
├── .env.example                  # 环境变量模板
├── .gitignore                    # Git忽略文件
├── LICENSE                       # MIT许可证
├── requirements.txt              # Python依赖
├── README.md                     # 项目说明
└── PROJECT_STRUCTURE.md          # 本文件
```

## 数据文件说明

### processed/ vs cleaned/

**processed/** - 原始提取
- 从PDF/EPUB直接提取的文字
- 基本格式处理
- 包含元数据头部

**cleaned/** - 深度清洗
- 字符规范化
- 删除无用内容
- 格式统一
- 元数据完整

### 向量数据库

**chroma/** - ChromaDB数据库
- 自动生成
- 2089个文档块
- 384维向量
- 可重新构建

## 核心模块说明

### rag/ 目录

**embeddings.py**
- 文字转向量
- 使用sentence-transformers
- 模型：all-MiniLM-L6-v2

**vector_store.py**
- ChromaDB管理
- 存储和检索向量
- 余弦相似度搜索

**retriever.py**
- 文档检索
- 返回最相关文档
- 格式化上下文

**generator.py**
- AI生成答案
- 支持GLM和OpenAI
- 巴菲特芒格风格

**pipeline.py**
- 整合所有模块
- 提供简单接口
- 支持流式输出

**prompts.py**
- 系统提示词
- 巴菲特芒格风格
- 可扩展

## 脚本说明

### 数据处理流程

```
原始文件（EPUB/PDF）
    ↓
extract_epub.py / extract_pdf.py
    ↓
processed/（原始提取）
    ↓
clean_data.py
    ↓
cleaned/（深度清洗）
    ↓
build_rag.py
    ↓
chroma/（向量数据库）
```

## 测试文件

**tests/** 目录包含：
- test_rag.py - 基础测试
- test_new_style.py - 新风格测试
- test_career_advice.py - 职业建议
- test_moat.py - 护城河问题
- test_moat_cn.py - 护城河问题（中文）

运行测试：
```bash
cd "C:\Users\steve\nothing to add project"
python tests/test_new_style.py
```

## 环境变量

**.env** 文件配置：
```
GLM_API_KEY=your-key
GENERATOR_MODEL=glm-4-flash
VECTOR_DB_PATH=./data/chroma
```

## 下一步开发

### 短期（1-2周）
- [ ] 多轮对话功能
- [ ] 记忆功能
- [ ] 更精准的检索

### 中期（1个月）
- [ ] Web界面
- [ ] 用户系统
- [ ] 对话历史

### 长期（3个月+）
- [ ] 语音输出
- [ ] 个性化推荐
- [ ] 知识图谱
