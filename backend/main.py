from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os, uuid, json, shutil
from pathlib import Path

app = FastAPI(title="Slide Platform API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / "output"
STYLES_DIR = BASE_DIR / "styles"
STATIC_DIR = BASE_DIR / "static"

# Detect if running on Vercel (serverless)
IS_VERCEL = os.environ.get("VERCEL", "") == "1"

# Only create output dir and mount static files in local dev
if not IS_VERCEL:
    OUTPUT_DIR.mkdir(exist_ok=True)
    try:
        app.mount("/output", StaticFiles(directory=str(OUTPUT_DIR)), name="output")
    except Exception:
        pass
    STATIC_DIR.mkdir(exist_ok=True)
    try:
        app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    except Exception:
        pass

# ===== Page Routes =====

@app.get("/", response_class=HTMLResponse)
async def serve_landing():
    return (BASE_DIR / "frontend" / "landing.html").read_text(encoding="utf-8")

@app.get("/app", response_class=HTMLResponse)
async def serve_frontend():
    return (BASE_DIR / "frontend" / "index.html").read_text(encoding="utf-8")

# ===== API Routes =====

@app.get("/api/styles")
async def list_styles():
    """获取所有可用风格列表"""
    styles = []
    for f in STYLES_DIR.glob("*.json"):
        data = json.loads(f.read_text(encoding="utf-8"))
        styles.append(data)
    return {"styles": styles}

@app.post("/api/preview")
async def generate_previews(style_name: str = Form(...), title: str = Form(""), subtitle: str = Form("")):
    """生成指定风格的预览 HTML（单页标题页）"""
    from .generator import generate_preview_html
    style_path = STYLES_DIR / f"{style_name}.json"
    if not style_path.exists():
        raise HTTPException(404, f"Style '{style_name}' not found")
    style = json.loads(style_path.read_text(encoding="utf-8"))
    html = generate_preview_html(style, title or "演示文稿标题", subtitle or "副标题")
    return HTMLResponse(content=html)

@app.post("/api/generate")
async def generate_presentation(
    style_name: str = Form(...),
    title: str = Form(...),
    slides_json: str = Form(...),  # JSON string of slides array
):
    """根据内容和风格生成完整演示文稿"""
    from .generator import generate_full_html
    style_path = STYLES_DIR / f"{style_name}.json"
    if not style_path.exists():
        raise HTTPException(404, f"Style '{style_name}' not found")
    style = json.loads(style_path.read_text(encoding="utf-8"))
    slides = json.loads(slides_json)
    html = generate_full_html(style, title, slides)

    # Try to save file (for local dev), but always return html for serverless
    file_id = str(uuid.uuid4())[:8]
    try:
        OUTPUT_DIR.mkdir(exist_ok=True)
        filename = f"{file_id}.html"
        filepath = OUTPUT_DIR / filename
        filepath.write_text(html, encoding="utf-8")
        return {"file_id": file_id, "url": f"/output/{filename}", "filename": filename, "html": html}
    except Exception:
        return {"file_id": file_id, "url": None, "filename": None, "html": html}

@app.post("/api/export-pdf")
async def export_pdf(file_id: str = Form(...)):
    """将 HTML 演示文稿导出为 PDF"""
    if IS_VERCEL:
        raise HTTPException(400, "PDF 导出在在线版本暂不可用，请使用浏览器的打印功能（Ctrl+P）导出 PDF")
    from .exporter import html_to_pdf
    html_path = OUTPUT_DIR / f"{file_id}.html"
    if not html_path.exists():
        raise HTTPException(404, "Presentation not found")
    pdf_path = OUTPUT_DIR / f"{file_id}.pdf"
    html_to_pdf(str(html_path), str(pdf_path))
    return FileResponse(
        str(pdf_path),
        media_type="application/pdf",
        filename=f"presentation-{file_id}.pdf"
    )

@app.post("/api/upload-image")
async def upload_image(file: UploadFile = File(...)):
    """上传图片素材"""
    file_id = str(uuid.uuid4())[:8]
    ext = Path(file.filename).suffix or ".png"
    filename = f"{file_id}{ext}"
    filepath = OUTPUT_DIR / filename
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"filename": filename, "url": f"/output/{filename}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
