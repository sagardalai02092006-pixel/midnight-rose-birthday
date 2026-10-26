# Little Moments — Birthday Surprise Website

A mobile-first, WishCupid-inspired **original** birthday-page builder. Create a page for a partner, friend, or family member with a personal letter, cover photo, photo gallery, optional uploaded voice note, optional song link, theme selection, confetti, and a final surprise reveal.

## Features

- Responsive design made for phones first
- Birthday page builder with four themes
- Cover photo and up to 8 gallery photos
- Personal message with preserved line breaks
- Optional audio message upload and external song link
- Unique unlisted share URL and copy-link button
- Interactive reveal and confetti effects
- Flask backend and SQLite database
- Upload validation and 24 MB total request limit

## Run locally

Requires Python 3.10 or newer.

```bash
# Windows PowerShell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000. On macOS/Linux, activate with `source .venv/bin/activate`.

By default, uploaded files and SQLite data are stored in `data/`. You can override locations with `DATA_DIR`, `UPLOAD_DIR`, and `DB_PATH` environment variables.

## Deploy on Render

1. Push this folder to a GitHub repository.
2. In Render, choose **New + → Blueprint** and select the repository. Render reads `render.yaml`; or create a Python web service manually.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn --workers 1 --threads 4 --timeout 120 app:app`
5. For durable uploads and pages, attach a **persistent disk** mounted at `/var/data` and keep `DATA_DIR=/var/data`, `UPLOAD_DIR=/var/data/uploads`, and `DB_PATH=/var/data/birthday.db`.
6. Set a strong `SECRET_KEY` in the Render environment. The Blueprint asks Render to generate one automatically.
7. Deploy, then test creating a page, opening its share link in a private browser window, and uploading a photo.

**Important hosting note:** the filesystem on many free web-service plans is ephemeral, and persistent disks may require a paid plan. Without persistent storage, uploaded photos and the SQLite database can disappear on redeploy/restart. For a public production service, use managed object storage for uploads and a managed database rather than relying on a local SQLite file.

## How to use

1. Open the homepage and select **Create their surprise**.
2. Enter recipient/sender names, title, and message.
3. Upload a cover photo and optionally up to eight extra photos or a voice note.
4. Optionally add an `https://` song link, and select a theme.
5. Create the page and copy the generated share link.

## Privacy and safety notes

- Anyone with the unlisted URL can view the page; this is not password-protected. Do not upload private or sensitive images unless you are comfortable with anyone holding the link seeing them.
- This starter project has no account system, page editing/deletion dashboard, moderation, or automated expiry. Add these before operating it as a public multi-user service.
- Uploads are extension-checked and renamed randomly, but production deployments should additionally inspect MIME/content, add rate limiting, malware scanning, and storage quotas.
- Song links open on the music provider; browsers generally block autoplay, so music is not played automatically.
- Fonts and the optional confetti script use external CDNs. A network connection is needed for those extras; core page content works without the confetti library.

## Project structure

```text
wishcupid-inspired/
├── app.py
├── requirements.txt
├── render.yaml
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── create.html
│   ├── created.html
│   ├── birthday.html
│   └── 404.html
└── static/
    ├── css/style.css
    └── js/main.js
```

## Future upgrades

- Secure creator accounts and private dashboard
- Password-protected pages and delete/expiry controls
- Cloud object storage (S3-compatible) and managed PostgreSQL
- Theme previews and editable existing pages
- QR code for sharing
- Custom domain and Open Graph preview image
