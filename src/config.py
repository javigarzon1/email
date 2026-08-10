"""Carga y valida el archivo config.yaml"""
import os
import sys
import yaml


def load_config(path: str = "config.yaml") -> dict:
    if not os.path.exists(path):
        example = path.replace(".yaml", ".example.yaml")
        print(f"❌ No se encontró '{path}'.")
        if os.path.exists(example):
            print(f"   Copia '{example}' a '{path}' y rellena tus datos.")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    required = ["email", "email_organizer", "file_downloader", "news_digest", "schedule"]
    missing = [k for k in required if k not in cfg]
    if missing:
        print(f"❌ Faltan secciones en config.yaml: {missing}")
        sys.exit(1)

    return cfg
