# 🤖 Bot de Automatización Personal

Bot en Python que cada mañana:

1. **Organiza tu correo** — clasifica y mueve correos entrantes a carpetas según reglas (remitente/asunto).
2. **Descarga archivos** — guarda automáticamente los adjuntos de correos que cumplan tus filtros.
3. **Te avisa de noticias/ofertas** — lee feeds RSS y te manda un resumen por correo cada mañana.

## 📦 Instalación

python3 -m venv venv
source venv/bin/activate   # En Windows: venv\Scripts\activate
pip install -r requirements.txt
``

## ⚙️ Configuración

1. Copia el archivo de ejemplo:
   ``bash
   cp config.example.yaml config.yaml
   ``
2. Edita `config.yaml` con tus datos:
   - Tu dirección de correo y **contraseña de aplicación** (no la contraseña normal).
     - Para Gmail: actívala en <https://myaccount.google.com/apppasswords> (requiere verificación en 2 pasos activada).
   - Las reglas de organización de correo (por remitente o asunto).
   - Los filtros de descarga de adjuntos.
   - Los feeds RSS que quieres seguir para el resumen matutino.
   - La hora a la que quieres que se ejecute cada día.

⚠️ **Nunca subas `config.yaml` a un repositorio público** — contiene tu contraseña. El `.gitignore` ya lo excluye.

## ▶️ Uso

**Ejecutar una sola vez** (para probar que todo funciona):
``bash
python main.py --once
``

**Dejarlo corriendo en segundo plano** (se ejecuta automáticamente cada día a la hora configurada):
``bash
python main.py
``

Para que siga corriendo aunque cierres la terminal, en Linux/Mac puedes usar:
``bash
nohup python main.py > bot.log 2>&1 &
``

O configurarlo como tarea programada (cron / Task Scheduler) que llame a `python main.py --once` cada mañana, en lugar de dejar el script corriendo indefinidamente.

## 🗂️ Estructura del proyecto

``
email_bot/
├── config.example.yaml   # Plantilla de configuración
├── config.yaml            # Tu configuración real (no subir a git)
├── requirements.txt
├── main.py                 # Orquestador + scheduler
├── downloads/              # Carpeta donde caen los adjuntos descargados
└── src/
    ├── config.py            # Carga config.yaml
    ├── email_organizer.py   # Clasifica y mueve correos por reglas
    ├── file_downloader.py   # Descarga adjuntos filtrados
    ├── news_digest.py       # Genera el resumen HTML de RSS
    └── notifier.py          # Envía el resumen por correo
``

## 🔧 Personalización rápida

- **Añadir una regla de organización**: agrega un bloque en `email_organizer.rules` en `config.yaml`.
- **Añadir un feed de noticias/ofertas**: agrega una entrada en `news_digest.feeds` con `name` y `url` del RSS.
- **Cambiar la hora de ejecución**: modifica `schedule.run_time`.

## 🚀 Ideas para ampliar

- Enviar el resumen también por Telegram (bot API) en vez de/además de correo.
- Añadir OCR o resumen con IA de los correos largos antes de organizarlos.
- Guardar un histórico de digests en una base de datos ligera (SQLite).
- Añadir scraping de páginas de ofertas específicas (no solo RSS).

## ⚠️ Notas de seguridad

- Usa siempre una **contraseña de aplicación**, nunca tu contraseña real de correo.
- Si usas Outlook/Hotmail, cambia `imap_server` a `outlook.office365.com` y revisa si necesitas habilitar IMAP en la configuración de tu cuenta.
- El bot borra el correo original de la bandeja de entrada al moverlo (usa `copy` + marca `\Deleted` + `expunge`). Si prefieres que **copie sin borrar**, elimina la línea `conn.store(msg_id, "+FLAGS", "\\Deleted")` en `src/email_organizer.py``
