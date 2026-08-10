#!/usr/bin/env python3
"""
Bot de automatización — organiza correo, descarga adjuntos y envía
un resumen matutino de noticias/ofertas.

Uso:
    python main.py --once      # Ejecuta todo una vez y termina
    python main.py             # Se queda corriendo y ejecuta cada día a la hora configurada
"""
import argparse
import sys
import time
import schedule

sys.path.insert(0, "src")
from src.config import load_config
from src.email_organizer import organize_inbox
from src.file_downloader import download_attachments
from src.news_digest import build_digest
from src.notifier import send_digest_email


def run_all(cfg: dict):
    print("\n🚀 Ejecutando bot de automatización...")

    try:
        summary = organize_inbox(cfg)
        print(f"   📥 Correos organizados: {summary if summary else 'ninguno nuevo'}")
    except Exception as e:
        print(f"   ⚠️  Error organizando correo: {e}")
        summary = {}

    try:
        downloaded = download_attachments(cfg)
        print(f"   📎 Archivos descargados: {len(downloaded)}")
    except Exception as e:
        print(f"   ⚠️  Error descargando archivos: {e}")
        downloaded = []

    try:
        digest_html = build_digest(cfg)
        print(f"   📰 Digest generado: {'sí' if digest_html else 'sin novedades'}")
    except Exception as e:
        print(f"   ⚠️  Error generando digest: {e}")
        digest_html = ""

    try:
        send_digest_email(cfg, digest_html, summary, downloaded)
    except Exception as e:
        print(f"   ⚠️  Error enviando resumen: {e}")

    print("✅ Ejecución completada.\n")


def main():
    parser = argparse.ArgumentParser(description="Bot de automatización personal")
    parser.add_argument("--once", action="store_true", help="Ejecutar una sola vez y salir")
    parser.add_argument("--config", default="config.yaml", help="Ruta al archivo de configuración")
    args = parser.parse_args()

    cfg = load_config(args.config)

    if args.once:
        run_all(cfg)
        return

    run_time = cfg["schedule"]["run_time"]
    schedule.every().day.at(run_time).do(run_all, cfg)
    print(f"⏰ Bot programado para ejecutarse cada día a las {run_time}. Ctrl+C para detener.")

    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main()
