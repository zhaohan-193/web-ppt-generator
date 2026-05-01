import subprocess, os

def html_to_pdf(html_path: str, pdf_path: str):
    """使用 Playwright 将 HTML 导出为 PDF"""
    # Check if playwright is installed
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        os.system("pip install playwright --break-system-packages -q")
        os.system("playwright install chromium")
        from playwright.sync_api import sync_playwright

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1920, "height": 1080})

        # Use file:// protocol
        file_url = "file://" + os.path.abspath(html_path)
        page.goto(file_url, wait_until="networkidle")
        page.wait_for_timeout(1000)

        # Get slide count
        slides = page.query_selector_all('.slide')
        total = len(slides)

        if total == 0:
            browser.close()
            raise Exception("No slides found")

        # Screenshot each slide
        from PIL import Image
        import io

        images = []
        for i in range(total):
            page.evaluate(f"""
                (function() {{
                    const slides = document.querySelectorAll('.slide');
                    slides.forEach((s, idx) => {{
                        s.style.transform = 'translateY(' + ((idx - {i}) * 100) + 'vh)';
                    }});
                    const cur = slides[{i}];
                    if (cur) cur.querySelectorAll('.reveal').forEach(el => el.classList.add('visible'));
                }})()
            """)
            page.wait_for_timeout(500)
            screenshot = page.screenshot(full_page=False)
            images.append(Image.open(io.BytesIO(screenshot)))

        browser.close()

        # Save as PDF
        first = images[0].convert('RGB')
        rest = [img.convert('RGB') for img in images[1:]]
        if rest:
            first.save(pdf_path, 'PDF', save_all=True, append_images=rest, resolution=150)
        else:
            first.save(pdf_path, 'PDF', resolution=150)
