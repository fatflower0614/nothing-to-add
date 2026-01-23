# 项目结构说明

```
nothing-to-add/
├── README.md                  # 项目说明
├── LICENSE                    # 开源协议
├── PROJECT_STRUCTURE.md       # 本文件
├── requirements.txt           # Python依赖
├── .env                       # 环境变量（不提交）
├── .env.example               # 环境变量模板
│
├── api/                       # FastAPI后端（新增）
│   ├── main.py               # API主文件
│   ├── routes/               # 路由定义
│   │   ├── chat.py          # 聊天API
│   │   └── search.py        # 搜索API
│   └── models/               # 数据模型
│
├── rag/                       # RAG系统核心
│   ├── __init__.py
│   ├── embeddings.py         # 向量化
│   ├── vector_store.py       # 向量数据库
│   ├── retriever.py          # 检索器
│   ├── generator.py          # AI生成
│   ├── pipeline.py           # RAG流程
│   ├── conversation.py       # 多轮对话
│   ├── search.py             # 联网搜索
│   └── prompts.py            # 提示词
│
├── frontend/                  # React前端（新增）
│   ├── package.json
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/       # React组件
│   │   │   ├── ChatBox.jsx  # 聊天框
│   │   │   ├── MessageList.jsx # 消息列表
│   │   │   └── InputArea.jsx # 输入区
│   │   └── api/              # API调用
│   │       └── client.js
│   └── public/
│
├── tests/                     # 测试文件
│   ├── README.md
│   ├── basic/                # 基础测试
│   │   ├── test_rag.py
│   │   └── test_new_style.py
│   ├── conversation/         # 对话测试
│   │   ├── test_conversation.py
│   │   └── test_polymarket_conversation.py
│   └── search/               # 搜索测试
│       ├── test_web_search.py
│       └── test_search_demo.py
│
├── scripts/                   # 数据处理脚本
│   ├── build_rag.py          # 构建向量库
│   ├── clean_data.py         # 清洗数据
│   ├── extract_epub.py       # EPUB提取
│   ├── extract_pdf.py        # PDF提取
│   ├── process_all_data.py   # 批量处理
│   └── download_wesco_letters.ps1
│
├── data/                      # 数据目录
│   ├── books/                # 原始书籍
│   ├── letters/              # 股东信
│   ├── processed/            # 提取的文本
│   ├── cleaned/              # 清洗后的文本
│   └── chroma/               # 向量数据库（自动生成）
│
└── docs/                      # 项目文档
    ├── planning/             # 开发计划
    │   ├── 00-项目总览README.md
    │   ├── 01-产品需求文档RPD.md
    │   ├── 02-技术术语解释.md
    │   ├── 03-技术选型文档.md
    │   └── 04-完整开发计划.md
    └── reports/              # 开发报告
        ├── 数据处理完成报告.md
        ├── 数据来源分析报告.md
        └── 数据清洗完成报告.md
```

## 目录说明

### api/ - FastAPI后端
- 后端API服务
- 处理前端请求
- 调用RAG系统

### rag/ - RAG系统核心
- 所有核心功能模块
- 向量化、检索、生成
- 多轮对话、联网搜索

### frontend/ - React前端
- 用户界面
- 聊天交互
- 响应式设计

### tests/ - 测试文件
- 按功能分类
- 基础、对话、搜索测试

### scripts/ - 数据处理
- 数据提取脚本
- 数据清洗脚本
- 向量库构建

### data/ - 数据存储
- 原始数据
- 处理后数据
- 向量数据库

## 快速导航

**想了解项目？** → README.md
**想修改RAG？** → rag/
**想修改界面？** → frontend/
**想运行测试？** → tests/
**想处理数据？** → scripts/
**想了解计划？** → docs/planning/
