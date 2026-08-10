"""
Descarga adjuntos de los correos entrantes que cumplan los filtros
configurados (extensión, asunto, remitente).
"""
import imaplib
import email
import os
from email.header import decode_header


def _decode(value: str) -> str:
    if not value:
        return ""
    parts = decode_header(value)
    decoded = ""
    for text, enc in parts:
        if isinstance(text, bytes):
            decoded += text.decode(enc or "utf-8", errors="ignore")
        else:
            decoded += text
    return decoded


def download_attachments(cfg: dict) -> list:
    """Devuelve la lista de rutas de archivos descargados"""
    dc = cfg["file_downloader"]
    if not dc.get("enabled", True):
        return []

    os.makedirs(dc["download_path"], exist_ok=True)
    downloaded = []

    conn = imaplib.IMAP4_SSL(cfg["email"]["imap_server"], cfg["email"]["imap_port"])
    conn.login(cfg["email"]["address"], cfg["email"]["password"])
    try:
        conn.select(dc["source_folder"])
        search_criteria = "UNSEEN" if dc.get("only_unread", True) else "ALL"
        status, data = conn.search(None, search_criteria)
        if status != "OK":
            return []

        msg_ids = data[0].split()
        allowed_ext = [e.lower() for e in dc.get("allowed_extensions", [])]
        subj_filter = [s.lower() for s in dc.get("filter_subject_contains", [])]
        sender_filter = [s.lower() for s in dc.get("filter_sender_contains", [])]

        for msg_id in msg_ids:
            status, msg_data = conn.fetch(msg_id, "(RFC822)")
            if status != "OK":
                continue
            msg = email.message_from_bytes(msg_data[0][1])
            subject = _decode(msg.get("Subject", "")).lower()
            sender = _decode(msg.get("From", "")).lower()

            if subj_filter and not any(kw in subject for kw in subj_filter):
                continue
            if sender_filter and not any(kw in sender for kw in sender_filter):
                continue

            for part in msg.walk():
                if part.get_content_maintype() == "multipart":
                    continue
                filename = part.get_filename()
                if not filename:
                    continue
                filename = _decode(filename)
                ext = os.path.splitext(filename)[1].lower()
                if allowed_ext and ext not in allowed_ext:
                    continue

                filepath = os.path.join(dc["download_path"], filename)
                # Evitar sobrescribir archivos con el mismo nombre
                base, extension = os.path.splitext(filepath)
                counter = 1
                while os.path.exists(filepath):
                    filepath = f"{base}_{counter}{extension}"
                    counter += 1

                with open(filepath, "wb") as f:
                    f.write(part.get_payload(decode=True))
                downloaded.append(filepath)
    finally:
        conn.close()
        conn.logout()

    return downloaded
