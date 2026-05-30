---
name: P10 个人文件库
id: P10
triggers: [个人文件, 简历, 文件库, 发我简历, 出租租约, 证书, personal library]
---

# P10 个人文件库 Playbook

## 快速启动

```bash
# 搜索文件（主要入口）
cd /home/cowork/cowork
python3 personal/search_personal.py "查询词"

# 重新索引（新增文件后）
python3 personal/index_files.py

# 数据库位置
personal/personal.db
```

## 进度指针
→ CURRENT_SESSION.md [P10]

## 当前状态（2026-04-25）
- 267文件已索引：简历13 + lease7 + 财务2 + 证书13 + cannabis232
- 阶段5-8暂停，等OCR安装：`sudo apt-get install -y tesseract-ocr tesseract-ocr-chi-sim poppler-utils && pip install pytesseract pdf2image`

## Discord使用模式
主公说"发我XXX简历/租约/证书" → search_personal.py检索 → Discord reply发送文件

## 分类规则
- `resume` — 简历（.docx/.pdf）
- `lease` — 出租租约
- `finance` — 财务（W2/税表）
- `certificate` — 证书
- `cannabis` — 大麻相关文件

## 搜索排序规则
filename/category命中 = 2分 > content命中 = 1分（避免内容分散排序）
