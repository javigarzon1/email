"""
Genera un resumen (digest) en HTML con las últimas noticias/ofertas
de una lista de feeds RSS, filtradas por antigüedad.
"""
from datetime import datetime, timedelta, timezone
import feedparser
from dateutil import parser as date_parser


def _entry_datetime(entry):
    for field in ("published", "updated"):
        if hasattr(entry, field):
            try:
                return date_parser.parse(getattr(entry, field))
            except (ValueError, TypeError):
                continue
    return None


def _highlight(text: str, keywords: list) -> str:
    for kw in keywords:
        if kw.lower() in text.lower():
            # Resalta con <mark> conservando el texto original
            idx = text.lower().find(kw.lower())
            original = text[idx: idx + len(kw)]
            text = text.replace(original, f"<mark>{original}</mark>")
    return text


def build_digest(cfg: dict) -> str:
    """Devuelve el digest como HTML. Vacío si no hay novedades o está desactivado."""
    nc = cfg["news_digest"]
    if not nc.get("enabled", True):
        return ""

    cutoff = datetime.now(timezone.utc) - timedelta(hours=nc.get("hours_lookback", 24))
    keywords = nc.get("highlight_keywords", [])
    sections = []

    for feed_cfg in nc.get("feeds", []):
        parsed = feedparser.parse(feed_cfg["url"])
        items_html = []

        for entry in parsed.entries[: nc.get("max_items_per_feed", 5) * 2]:
            entry_dt = _entry_datetime(entry)
            if entry_dt and entry_dt.tzinfo is None:
                entry_dt = entry_dt.replace(tzinfo=timezone.utc)
            if entry_dt and entry_dt < cutoff:
                continue

            title = _highlight(entry.get("title", "Sin título"), keywords)
            link = entry.get("link", "#")
            items_html.append(f'<li><a href="{link}">{title}</a></li>')

            if len(items_html) >= nc.get("max_items_per_feed", 5):
                break

        if items_html:
            sections.append(
                f'<h3>{feed_cfg["name"]}</h3><ul>{"".join(items_html)}</ul>'
            )

    if not sections:
        return ""

    today = datetime.now().strftime("%d/%m/%Y")
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: auto;">
        <h2>📰 Resumen matutino — {today}</h2>
        {"".join(sections)}
        <hr>
        <p style="color:#888; font-size:12px;">Generado automáticamente por tu bot de automatización.</p>
    </body>
    </html>
    """
    return html
