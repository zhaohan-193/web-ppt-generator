"""
HTML 生成引擎
使用 Jinja2 模板生成演示文稿 HTML
支持科技风格和中式风格
"""

import json
from jinja2 import Environment, FileSystemLoader, select_autoescape

# 模板目录
TEMPLATES_DIR = __import__('pathlib').Path(__file__).parent / 'templates'

# 初始化 Jinja2 环境
env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(default=False),
    trim_blocks=True,
    lstrip_blocks=True,
)


def _get_style_id(style: dict) -> str:
    """获取风格 ID"""
    return style.get('id', style.get('name_en', '')).lower()


def _is_zhongshi(style: dict) -> bool:
    """判断是否为中式风格"""
    sid = _get_style_id(style)
    return sid == 'zhongshi' or style.get('name') == '中式'


def generate_preview_html(style: dict, title: str, subtitle: str) -> str:
    """
    生成单页风格预览 HTML（封面页）
    """
    if _is_zhongshi(style):
        base_template = env.get_template('zhongshi_base.html')
        # 中式风格预览：直接用模板渲染封面
        from jinja2 import Template
        cover_html = _render_zhongshi_cover(title, subtitle, style)
        html = base_template.render(
            title=title,
            style=style,
            slides=cover_html,
        )
    else:
        base_template = env.get_template('base.html')
        cover_macro = env.get_template('cover.html')
        cover_html = cover_macro.module.cover_slide(title, subtitle, style)
        html = base_template.render(
            title=title,
            style=style,
            slides=cover_html,
        )
    return html


def generate_full_html(style: dict, title: str, slides: list) -> str:
    """
    生成完整演示文稿 HTML
    支持多种幻灯片类型：cover, content, toc, compare, timeline, chart/data, summary
    """
    if _is_zhongshi(style):
        return _generate_zhongshi_html(style, title, slides)
    else:
        return _generate_keji_html(style, title, slides)


def _generate_keji_html(style: dict, title: str, slides: list) -> str:
    """生成科技风格 HTML"""
    base_template = env.get_template('base.html')
    cover_macro = env.get_template('cover.html')
    content_macro = env.get_template('content.html')

    slides_html = []
    for idx, slide in enumerate(slides):
        slide_type = slide.get('type', 'content')
        heading = slide.get('heading', '') or slide.get('title', '')
        subheading = slide.get('subheading', '') or slide.get('subtitle', '')
        points = slide.get('points', [])
        layout = slide.get('layout', None)

        if slide_type == 'cover':
            cover_title = heading or title
            cover_subtitle = subheading
            html = cover_macro.module.cover_slide(cover_title, cover_subtitle, style)
        elif slide_type == 'toc':
            toc_points = [_p_text(p) for p in points]
            html = content_macro.module.content_slide(heading=heading, subheading=subheading, points=toc_points, layout=None)
        elif slide_type == 'compare':
            compare_points = [_p_dict(p) for p in points]
            html = content_macro.module.content_slide(heading=heading, subheading=subheading, points=compare_points, layout='horizontal')
        elif slide_type == 'timeline':
            timeline_points = [_p_dict(p, title_key='time') for p in points]
            html = content_macro.module.content_slide(heading=heading, subheading=subheading, points=timeline_points, layout='vertical')
        elif slide_type in ('chart', 'data'):
            chart_points = []
            for p in points:
                if isinstance(p, dict):
                    label = p.get('label', p.get('title', ''))
                    value = p.get('value', '')
                    chart_points.append(f"{label}: {value}" if value else label)
                else:
                    chart_points.append(str(p))
            html = content_macro.module.content_slide(heading=heading, subheading=subheading, points=chart_points, layout=None)
        elif slide_type == 'summary':
            summary_points = [_p_text(p) for p in points]
            html = content_macro.module.content_slide(heading=heading, subheading=subheading, points=summary_points, layout=None)
        else:
            content_points = []
            for p in points:
                if isinstance(p, str):
                    content_points.append(p)
                elif isinstance(p, dict):
                    content_points.append({'title': p.get('title', ''), 'text': p.get('text', p.get('description', ''))})
                else:
                    content_points.append(str(p))
            html = content_macro.module.content_slide(heading=heading, subheading=subheading, points=content_points, layout=layout)

        slides_html.append(html)

    html = base_template.render(title=title, style=style, slides='\n'.join(slides_html))
    return html


def _generate_zhongshi_html(style: dict, title: str, slides: list) -> str:
    """生成中式风格 HTML"""
    base_template = env.get_template('zhongshi_base.html')

    slides_html = []
    for idx, slide in enumerate(slides):
        slide_type = slide.get('type', 'content')
        heading = slide.get('heading', '') or slide.get('title', '')
        subheading = slide.get('subheading', '') or slide.get('subtitle', '')
        points = slide.get('points', [])
        layout = slide.get('layout', None)

        if slide_type == 'cover':
            html = _render_zhongshi_cover(heading or title, subheading, style)
        elif slide_type == 'toc':
            html = _render_zhongshi_toc(heading, subheading, points, style)
        elif slide_type == 'compare':
            html = _render_zhongshi_compare(heading, subheading, points, style)
        elif slide_type == 'timeline':
            html = _render_zhongshi_timeline(heading, subheading, points, style)
        elif slide_type in ('chart', 'data'):
            html = _render_zhongshi_data(heading, subheading, points, style)
        elif slide_type == 'summary':
            html = _render_zhongshi_summary(heading, subheading, points, style)
        else:
            html = _render_zhongshi_content(heading, subheading, points, layout, style)

        slides_html.append(html)

    html = base_template.render(title=title, style=style, slides='\n'.join(slides_html))
    return html


# ===== 中式风格页面渲染函数 =====

def _render_zhongshi_cover(title, subtitle, style):
    """中式封面页"""
    return f'''<div class="slide slide-cover active">
  <div class="cover-bg-image"></div>
  <div class="cover-content-layer">
    <div class="reveal"><h1 class="cover-title">{title}</h1></div>
    <div class="reveal"><div class="cover-divider"><div class="cover-divider-line"></div><div class="cover-divider-diamond"></div><div class="cover-divider-line"></div></div></div>
    <div class="reveal"><p class="cover-subtitle">{subtitle}</p></div>
    <div class="reveal"><div class="cover-date-area"><span class="cover-date"></span></div></div>
  </div>
</div>'''


def _render_zhongshi_toc(heading, subheading, points, style):
    """中式目录页"""
    cn_nums = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十',
               '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十']
    items = ''
    for i, p in enumerate(points):
        text = p if isinstance(p, str) else p.get('text', p.get('title', ''))
        num = cn_nums[i] if i < len(cn_nums) else str(i + 1)
        items += f'''    <div class="toc-item reveal">
      <div class="toc-num">（{num}）</div>
      <div class="toc-text">{text}</div>
    </div>\n'''
    return f'''<div class="slide slide-toc">
  <div class="zh-top-line"></div>
  <div class="zh-content">
    <div class="reveal"><h2 class="zh-title">{heading}</h2></div>
    {"<div class='reveal'><p class='zh-subtitle'>" + subheading + "</p></div>" if subheading else ""}
    <div class="toc-list">
{items}    </div>
  </div>
  <div class="zh-bottom-line"></div>
  <div class="corner-huiwen corner-tl"></div>
  <div class="corner-huiwen corner-tr"></div>
  <div class="corner-huiwen corner-bl"></div>
  <div class="corner-huiwen corner-br"></div>
</div>'''


def _render_zhongshi_content(heading, subheading, points, layout, style):
    """中式内容页"""
    cards = ''
    for p in points:
        if isinstance(p, dict):
            p_title = p.get('title', '')
            p_text = p.get('text', p.get('description', ''))
        else:
            p_title = ''
            p_text = str(p)
        title_html = f'<div class="zh-card-title">{p_title}</div>' if p_title else ''
        cards += f'''    <div class="zh-card reveal">
      <div class="zh-card-bar"></div>
      <div class="zh-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4l3 3"/></svg></div>
      <div class="zh-card-body">{title_html}<div class="zh-card-text">{p_text}</div></div>
    </div>\n'''

    cls = 'zh-cards-vertical' if layout == 'vertical' else f'zh-cards-grid cols-{min(len(points), 6)}'
    return f'''<div class="slide slide-content-page">
  <div class="zh-top-line"></div>
  <div class="zh-content">
    <div class="reveal"><div class="zh-header"><div class="zh-header-bar"></div><h2 class="zh-title">{heading}</h2></div></div>
    {"<div class='reveal'><p class='zh-subtitle'>" + subheading + "</p></div>" if subheading else ""}
    <div class="{cls}">
{cards}    </div>
  </div>
  <div class="zh-bottom-line"></div>
  <div class="corner-huiwen corner-tl"></div>
  <div class="corner-huiwen corner-tr"></div>
  <div class="corner-huiwen corner-bl"></div>
  <div class="corner-huiwen corner-br"></div>
</div>'''


def _render_zhongshi_compare(heading, subheading, points, style):
    """中式对比页"""
    left_items = ''
    right_items = ''
    for i, p in enumerate(points):
        if isinstance(p, dict):
            title = p.get('title', '')
            text = p.get('text', p.get('description', ''))
        else:
            title = ''
            text = str(p)
        item = f'<div class="compare-item reveal"><div class="compare-item-title">{title}</div><div class="compare-item-text">{text}</div></div>\n'
        if i < len(points) // 2 + len(points) % 2:
            left_items += item
        else:
            right_items += item

    return f'''<div class="slide slide-compare">
  <div class="zh-top-line"></div>
  <div class="zh-content">
    <div class="reveal"><h2 class="zh-title zh-title-center">{heading}</h2></div>
    {"<div class='reveal'><p class='zh-subtitle zh-subtitle-center'>" + subheading + "</p></div>" if subheading else ""}
    <div class="compare-columns">
      <div class="compare-col compare-col-left">
        {left_items}      </div>
      <div class="compare-vs reveal"><span>VS</span></div>
      <div class="compare-col compare-col-right">
        {right_items}      </div>
    </div>
  </div>
  <div class="zh-bottom-line"></div>
</div>'''


def _render_zhongshi_timeline(heading, subheading, points, style):
    """中式时间线页"""
    items = ''
    for i, p in enumerate(points):
        if isinstance(p, dict):
            t_title = p.get('title', p.get('time', ''))
            t_text = p.get('text', p.get('description', ''))
        else:
            t_title = ''
            t_text = str(p)
        items += f'''    <div class="timeline-item reveal">
      <div class="timeline-node"></div>
      <div class="timeline-content">
        <div class="timeline-title">{t_title}</div>
        <div class="timeline-text">{t_text}</div>
      </div>
    </div>\n'''

    return f'''<div class="slide slide-timeline">
  <div class="zh-top-line"></div>
  <div class="zh-content">
    <div class="reveal"><div class="zh-header"><div class="zh-header-bar"></div><h2 class="zh-title">{heading}</h2></div></div>
    {"<div class='reveal'><p class='zh-subtitle'>" + subheading + "</p></div>" if subheading else ""}
    <div class="timeline-list">
{items}    </div>
  </div>
  <div class="zh-bottom-line"></div>
  <div class="corner-huiwen corner-tl"></div>
  <div class="corner-huiwen corner-tr"></div>
</div>'''


def _render_zhongshi_data(heading, subheading, points, style):
    """中式数据展示页"""
    bars = ''
    colors = ['#C41E3A', '#D4AF37', '#1E3A5F', '#C41E3A', '#D4AF37', '#1E3A5F']
    for i, p in enumerate(points):
        if isinstance(p, dict):
            label = p.get('label', p.get('title', ''))
            value = p.get('value', 0)
        else:
            label = str(p)
            value = 50
        try:
            pct = min(float(value), 100)
        except (ValueError, TypeError):
            pct = 50
        color = colors[i % len(colors)]
        bars += f'''    <div class="data-bar-item reveal">
      <div class="data-bar-label">{label}</div>
      <div class="data-bar-track"><div class="data-bar-fill" style="width:{pct}%;background:{color}"></div></div>
      <div class="data-bar-value">{value}</div>
    </div>\n'''

    return f'''<div class="slide slide-data">
  <div class="zh-top-line"></div>
  <div class="zh-content">
    <div class="reveal"><h2 class="zh-title zh-title-center">{heading}</h2></div>
    {"<div class='reveal'><p class='zh-subtitle zh-subtitle-center'>" + subheading + "</p></div>" if subheading else ""}
    <div class="data-card">
      <div class="data-card-inner">
{bars}      </div>
    </div>
  </div>
  <div class="zh-bottom-line"></div>
  <div class="corner-huiwen corner-tl"></div>
  <div class="corner-huiwen corner-tr"></div>
  <div class="corner-huiwen corner-bl"></div>
  <div class="corner-huiwen corner-br"></div>
</div>'''


def _render_zhongshi_summary(heading, subheading, points, style):
    """中式总结页"""
    items = ''
    for p in points:
        if isinstance(p, dict):
            text = p.get('text', p.get('title', ''))
        else:
            text = str(p)
        items += f'''    <div class="summary-item reveal">
      <div class="summary-diamond"></div>
      <div class="summary-text">{text}</div>
    </div>\n'''

    conclusion = ''
    if points:
        first = points[0] if isinstance(points[0], str) else points[0].get('text', points[0].get('title', ''))
        conclusion = f'<div class="summary-conclusion reveal">{first}</div>'

    return f'''<div class="slide slide-summary">
  <div class="zh-top-line"></div>
  <div class="zh-content">
    <div class="reveal"><h2 class="zh-title zh-title-center">{heading}</h2></div>
    {"<div class='reveal'><p class='zh-subtitle zh-subtitle-center'>" + subheading + "</p></div>" if subheading else ""}
    {conclusion}
    <div class="summary-list">
{items}    </div>
  </div>
  <div class="zh-bottom-line"></div>
  <div class="cover-seal cover-seal-small reveal"><div class="seal-inner">印</div></div>
</div>'''


# ===== 工具函数 =====

def _p_text(p) -> str:
    """提取纯文本"""
    if isinstance(p, str):
        return p
    return p.get('text', p.get('title', p.get('description', '')))


def _p_dict(p, title_key='title') -> dict:
    """提取字典"""
    if isinstance(p, dict):
        return {'title': p.get('title', p.get(title_key, '')), 'text': p.get('text', p.get('description', ''))}
    return {'title': '', 'text': str(p)}
