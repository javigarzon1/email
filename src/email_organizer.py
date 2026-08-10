"""
Organiza el correo entrante: revisa mensajes y los mueve a carpetas
según reglas de coincidencia por asunto o remitente.
"""
import imaplib
import email
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


def _connect(cfg: dict) -> imaplib.IMAP4_SSL:
    conn = imaplib.IMAP4_SSL(cfg["email"]["imap_server"], cfg["email"]["imap_port"])
    conn.login(cfg["email"]["address"], cfg["email"]["password"])
    return conn


def _ensure_folder_exists(conn: imaplib.IMAP4_SSL, folder: str):
    status, folders = conn.list()
    existing = [f.decode().split('"')[-2] for f in folders] if status == "OK" else []
    if folder not in existing:
        conn.create(folder)


def _matches_rule(subject: str, sender: str, rule: dict) -> bool:
    conditions = rule.get("match_any", {})
    subject_kw = [s.lower() for s in conditions.get("subject_contains", [])]
    sender_kw = [s.lower() for s in conditions.get("sender_contains", [])]

    subject_l = subject.lower()
    sender_l = sender.lower()

    if any(kw in subject_l for kw in subject_kw):
        return True
    if any(kw in sender_l for kw in sender_kw):
        return True
    return False


def organize_inbox(cfg: dict) -> dict:
    """Devuelve un resumen {carpeta: n_correos_movidos}"""
    oc = cfg["email_organizer"]
    if not oc.get("enabled", True):
        return {}

    summary = {}
    conn = _connect(cfg)
    try:
        conn.select(oc["source_folder"])

        search_criteria = "UNSEEN" if oc.get("only_unread", True) else "ALL"
        status, data = conn.search(None, search_criteria)
        if status != "OK":
            return {}

        msg_ids = data[0].split()
        for msg_id in msg_ids:
            status, msg_data = conn.fetch(msg_id, "(RFC822)")
            if status != "OK":
                continue
            msg = email.message_from_bytes(msg_data[0][1])
            subject = _decode(msg.get("Subject", ""))
            sender = _decode(msg.get("From", ""))

            for rule in oc.get("rules", []):
                if _matches_rule(subject, sender, rule):
                    target = rule["folder"]
                    _ensure_folder_exists(conn, target)
                    conn.copy(msg_id, target)
                    conn.store(msg_id, "+FLAGS", "\\Deleted")
                    summary[target] = summary.get(target, 0) + 1
                    break  # primera regla que coincide gana

        conn.expunge()
    finally:
        conn.close()
        conn.logout()

    return summary
