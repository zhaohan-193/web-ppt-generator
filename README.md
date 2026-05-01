# Slide Platform

一个基于 FastAPI 的在线演示文稿生成平台，支持多种风格模板、实时预览和 PDF 导出。

## 快速开始（Docker 部署）

```bash
# 1. 启动服务
docker-compose up -d

# 2. 打开浏览器
# 访问 http://localhost:8000

# 3. 开始使用
# 选择风格 → 编辑内容 → 生成演示文稿 → 导出 PDF
```

## 本地开发

```bash
# 1. 安装依赖
pip install -r backend/requirements.txt
playwright install chromium

# 2. 启动服务
cd backend
python main.py

# 3. 打开浏览器访问 http://localhost:8000
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 前端页面 |
| GET | `/api/styles` | 获取所有可用风格列表 |
| POST | `/api/preview` | 生成指定风格的预览 HTML |
| POST | `/api/generate` | 根据内容和风格生成完整演示文稿 |
| POST | `/api/export-pdf` | 将 HTML 演示文稿导出为 PDF |
| POST | `/api/upload-image` | 上传图片素材 |

## 项目结构

```
slide-platform/
├── backend/
│   ├── templates/          # Jinja2 HTML 模板
│   │   ├── base.html       # 基础布局模板
│   │   ├── cover.html      # 封面页模板
│   │   └── content.html    # 内容页模板
│   ├── main.py             # FastAPI 主应用入口
│   ├── generator.py        # HTML 生成引擎
│   ├── exporter.py         # PDF 导出模块（Playwright）
│   └── requirements.txt    # Python 依赖
├── styles/                 # 风格配置文件
│   ├── bold_signal.json
│   ├── swiss_modern.json
│   └── yuansu.json
├── frontend/               # 前端静态文件
├── output/                 # 生成的文件输出目录
├── Dockerfile
├── docker-compose.yml
└── .dockerignore
```

## 技术栈

- **后端框架**：FastAPI + Uvicorn
- **模板引擎**：Jinja2
- **PDF 导出**：Playwright + Chromium
- **前端**：HTML / CSS / JavaScript
- **部署**：Docker / Docker Compose
