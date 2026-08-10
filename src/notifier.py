"""Envía el resumen matutino (y notificaciones) por correo vía SMTP."""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_digest_email(cfg: dict, html_content: str, extra_summary: dict = None,
                       downloaded_files: list = None):
    if not html_content and not extra_summary and not downloaded_files:
        return  # nada que enviar

    ec = cfg["email"]

    extras_html = ""
    if extra_summary:
        rows = "".join(f"<li>{folder}: {count} correo(s) movidos</li>"
                        for folder, count in extra_summary.items())
        extras_html += f"<h3>📥 Organización de correo</h3><ul>{rows}</ul>"

    if downloaded_files:
        rows = "".join(f"<li>{f}</li>" for f in downloaded_files)
        extras_html += f"<h3>📎 Archivos descargados</h3><ul>{rows}</ul>"

    full_html = f"<html><body>{extras_html}{html_content or ''}</body></html>"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "🤖 Tu resumen matutino"
    msg["From"] = ec["address"]
    msg["To"] = ec["digest_recipient"]
    msg.attach(MIMEText(full_html, "html"))

    with smtplib.SMTP(ec["smtp_server"], ec["smtp_port"]) as server:
        server.starttls()
        server.login(ec["address"], ec["password"])
        server.sendmail(ec["address"], ec["digest_recipient"], msg.as_string())

    print(f"✅ Resumen enviado a {ec['digest_recipient']}")
