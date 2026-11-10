"""Screenshot real Swagger and render saved, unmodified runtime evidence."""
import html
import json
import re
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import JsonLexer

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"
IMAGES = ROOT / "portfolio_images"
TITLE = "Multi-tenant analytics chatbot — rule-based mode, synthetic data"
FORMATTER = HtmlFormatter(nowrap=True, style="monokai")


def json_html(value):
    return highlight(json.dumps(value, indent=2), JsonLexer(), FORMATTER)


def document(title, content, extra_css=""):
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>{html.escape(title)}</title>
    <style>
    * {{ box-sizing: border-box; }}
    body {{ margin:0; padding:45px 48px; background:#edf2f8; color:#172338;
      font-family:Arial,sans-serif; width:1600px; height:1100px; }}
    .eyebrow {{ font-size:16px; font-weight:700; letter-spacing:2px; color:#50627a; margin-bottom:16px; }}
    h1 {{ margin:0 0 20px; font-size:32px; line-height:1.25; font-weight:700; }}
    .meta {{ color:#50627a; font-size:19px; margin-bottom:27px; }}
    .panels {{ display:grid; grid-template-columns:420px 1fr; gap:24px; }}
    .terminal {{ background:#132033; border-radius:17px; overflow:hidden; box-shadow:0 12px 30px #17324d15; }}
    .bar {{ display:flex; gap:16px; align-items:center; background:#203148; padding:17px 23px;
      color:#cfdaeb; font-size:17px; font-weight:700; }}
    .dots {{ color:#65d6ab; letter-spacing:5px; }}
    .content {{ padding:22px 25px; }}
    pre {{ color:#e7edf7; font-family:Menlo,Consolas,monospace; font-size:18px;
      line-height:1.38; margin:0; white-space:pre-wrap; overflow-wrap:anywhere; }}
    .note {{ font-size:18px; line-height:1.55; color:#50627a; margin-top:24px; }}
    .key {{ color:#75dfb7; }}
    {FORMATTER.get_style_defs()}
    {extra_css}
    </style></head><body>{content}</body></html>"""


def render_chat():
    record = json.loads((OUTPUT / "demo_records.json").read_text())[0]
    content = f"""
    <div class="eyebrow">ZHUANGYI QIU / PERSONAL PORTFOLIO DEMO</div>
    <h1>{TITLE}</h1>
    <div class="meta">{html.escape(record['tenant'])} · Actual curl request and response · HTTP {record['status']}</div>
    <div class="panels">
      <section class="terminal"><div class="bar"><span class="dots">● ● ●</span> REQUEST</div>
        <div class="content"><pre>POST /chat
Content-Type: application/json
X-API-Key: <span class="key">{record['masked_key']}</span>

{json_html(record['request'])}</pre></div></section>
      <section class="terminal"><div class="bar"><span class="dots">● ● ●</span> RESPONSE / HTTP {record['status']}</div>
        <div class="content"><pre>{json_html(record['response'])}</pre></div></section>
    </div>
    <div class="note">Source · output/demo_records.json, exchange 1. Complete JSON response.<br>
    Analytics clock fixed at 2026-11-10 12:00 UTC. API-key text masked for display.</div>
    """
    return document(TITLE, content)


def render_tests():
    raw = (OUTPUT / "pytest.txt").read_text()
    selected_names = [
        "test_health_confirms_real_db_role_and_rls",
        "test_missing_or_unknown_key_is_401",
        "test_answers_only_include_authenticated_tenant",
        "test_cross_tenant_session_read_and_reuse_are_404",
        "test_followups_keep_intent_and_unspecified_filters",
        "test_concurrent_turns_preserve_complete_session_history",
        "test_raw_queries_without_tenant_return_zero_for_every_data_table",
        "test_rls_rejects_wrong_repository_scope_and_unfiltered_sql",
        "test_rls_with_check_rejects_cross_tenant_write",
        "test_set_local_resets_after_commit_and_rollback",
        "test_help_uses_local_hashing_and_real_vector_distance_when_available",
        "test_llm_default_is_noop_and_not_called",
    ]
    selected = []
    for name in selected_names:
        line = next(line for line in raw.splitlines() if f"::{name}" in line and "PASSED" in line)
        # Remove just the repeated file prefix and progress percentage for readability.
        selected.append(re.sub(r"\s+\[\s*\d+%\]$", "", line.split("::", 1)[1]))
    summary = next(line for line in raw.splitlines() if re.search(r"\d+ passed", line))
    assert not re.search(r"\d+ failed|\d+ error", summary)
    health = json.loads((OUTPUT / "health.json").read_text())
    evidence = {key: health[key] for key in ("database_role", "rolsuper", "rolbypassrls", "rls_tables", "pgvector")}
    test_lines = "\n".join(selected)
    content = f"""
    <div class="eyebrow">ZHUANGYI QIU / PERSONAL PORTFOLIO DEMO</div>
    <h1>Tenant isolation verified against real PostgreSQL</h1>
    <div class="meta">Rule-based mode · Synthetic data · Selected lines from the actual pytest run</div>
    <section class="terminal"><div class="bar"><span class="dots">● ● ●</span> PYTEST / REAL DATABASE</div>
      <div class="content"><pre>$ .venv/bin/python -m pytest -v --tb=short

{html.escape(test_lines)}

<span class="key">{html.escape(summary)}</span></pre></div></section>
    <div class="evidence"><section class="terminal"><div class="bar">LIVE /health DATABASE FIELDS</div>
      <div class="content"><pre>{json_html(evidence)}</pre></div></section>
      <div class="note">Sources<br>output/pytest.txt<br>output/health.json<br><br>
      Test names retain their exact spelling.<br>Repeated file prefixes and progress markers omitted.<br>
      Full output includes the upstream TestClient deprecation warning.</div></div>
    """
    return document("Tenant isolation tests", content, """
        pre { font-size:18px; line-height:1.5; }
        .evidence { display:grid; grid-template-columns:680px 1fr; gap:28px; margin-top:24px; }
        .evidence pre { font-size:17px; line-height:1.35; }
        .evidence .content { padding:15px 25px; }
        .evidence .bar { padding:12px 23px; font-size:15px; }
        .evidence .note { font-size:17px; }
    """)


def main():
    IMAGES.mkdir(exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1600, "height": 1100}, device_scale_factor=1)
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto("http://127.0.0.1:8000/docs", wait_until="networkidle", timeout=60000)
        page.locator(".swagger-ui .info .title").wait_for(timeout=45000)
        page.locator("#operations-Analytics-chat_chat_post .opblock-summary").click()
        page.locator("#operations-Analytics-chat_chat_post .opblock-body").wait_for()
        page.screenshot(path=str(IMAGES / "01_swagger.png"))
        for name, source in (("02_chat_response", render_chat()), ("03_tenant_isolation_tests", render_tests())):
            (OUTPUT / f"{name}.html").write_text(source)
            page.set_content(source, wait_until="load")
            page.evaluate("document.fonts.ready")
            assert page.evaluate("document.documentElement.scrollWidth") == 1600
            assert page.evaluate("document.documentElement.scrollHeight") <= 1100, name
            page.screenshot(path=str(IMAGES / f"{name}.png"))
        assert not errors, errors
        browser.close()
    image_checks = []
    for path in sorted(IMAGES.glob("*.png")):
        with Image.open(path) as picture:
            assert picture.size == (1600, 1100)
            image_checks.append({"file": path.name, "width": picture.width, "height": picture.height,
                                 "bytes": path.stat().st_size})
    (OUTPUT / "image-verification.json").write_text(json.dumps(image_checks, indent=2) + "\n")
    print(json.dumps(image_checks, indent=2))


if __name__ == "__main__":
    main()
