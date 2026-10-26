import os, sqlite3, uuid, re
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get('DATA_DIR', BASE_DIR / 'data'))
UPLOAD_DIR = Path(os.environ.get('UPLOAD_DIR', DATA_DIR / 'uploads'))
DB_PATH = Path(os.environ.get('DB_PATH', DATA_DIR / 'birthday.db'))
ALLOWED_IMAGES = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
ALLOWED_AUDIO = {'mp3', 'wav', 'ogg', 'm4a'}
MAX_CONTENT_LENGTH = 24 * 1024 * 1024

DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'change-this-before-deploying-' + uuid.uuid4().hex)
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with db() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT UNIQUE NOT NULL,
            recipient TEXT NOT NULL,
            sender TEXT NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            date_text TEXT,
            theme TEXT NOT NULL DEFAULT 'midnight-rose',
            music_url TEXT,
            cover_image TEXT,
            audio_file TEXT,
            created_at TEXT NOT NULL
        )''')
        conn.execute('''CREATE TABLE IF NOT EXISTS photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            page_slug TEXT NOT NULL,
            filename TEXT NOT NULL,
            caption TEXT DEFAULT '',
            FOREIGN KEY(page_slug) REFERENCES pages(slug)
        )''')

init_db()


def allowed_file(filename, allowed):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed


def save_upload(file_storage, allowed):
    if not file_storage or not file_storage.filename:
        return None
    if not allowed_file(file_storage.filename, allowed):
        raise ValueError('That file type is not supported. Please choose an image or audio file of a supported type.')
    original = secure_filename(file_storage.filename)
    ext = original.rsplit('.', 1)[1].lower()
    filename = f'{uuid.uuid4().hex}.{ext}'
    file_storage.save(UPLOAD_DIR / filename)
    return filename


def upload_url(filename):
    return url_for('uploaded_file', filename=filename) if filename else None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'GET':
        return render_template('create.html')
    recipient = request.form.get('recipient', '').strip()[:80]
    sender = request.form.get('sender', '').strip()[:80]
    title = request.form.get('title', '').strip()[:120]
    message = request.form.get('message', '').strip()[:5000]
    date_text = request.form.get('date_text', '').strip()[:100]
    theme = request.form.get('theme', 'midnight-rose')
    music_url = request.form.get('music_url', '').strip()[:500]
    if not all([recipient, sender, title, message]):
        flash('Please fill in the recipient, your name, title, and message.', 'error')
        return render_template('create.html', form=request.form)
    if theme not in {'midnight-rose', 'golden-hour', 'lavender-galaxy', 'candy-pop'}:
        theme = 'midnight-rose'
    if music_url and not re.match(r'^https://', music_url, re.I):
        flash('Music links must start with https://', 'error')
        return render_template('create.html', form=request.form)
    slug = uuid.uuid4().hex[:10]
    saved_files = []
    try:
        cover = save_upload(request.files.get('cover_image'), ALLOWED_IMAGES)
        if cover: saved_files.append(cover)
        audio = save_upload(request.files.get('audio_file'), ALLOWED_AUDIO)
        if audio: saved_files.append(audio)
        photo_files = request.files.getlist('photos')
        photos = []
        for photo in photo_files[:8]:
            if photo and photo.filename:
                name = save_upload(photo, ALLOWED_IMAGES)
                photos.append(name)
                saved_files.append(name)
    except ValueError as exc:
        for name in saved_files:
            (UPLOAD_DIR / name).unlink(missing_ok=True)
        flash(str(exc), 'error')
        return render_template('create.html', form=request.form)
    try:
        with db() as conn:
            conn.execute('INSERT INTO pages (slug, recipient, sender, title, message, date_text, theme, music_url, cover_image, audio_file, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (slug, recipient, sender, title, message, date_text, theme, music_url, cover, audio, datetime.utcnow().isoformat()))
            for name in photos:
                conn.execute('INSERT INTO photos (page_slug, filename) VALUES (?, ?)', (slug, name))
    except Exception:
        for name in saved_files:
            (UPLOAD_DIR / name).unlink(missing_ok=True)
        app.logger.exception('Could not save birthday page')
        flash('Something went wrong while saving. Please try again.', 'error')
        return render_template('create.html', form=request.form)
    return redirect(url_for('created', slug=slug))


@app.route('/created/<slug>')
def created(slug):
    with db() as conn:
        page = conn.execute('SELECT slug, recipient, title FROM pages WHERE slug = ?', (slug,)).fetchone()
    if not page: abort(404)
    return render_template('created.html', page=page, share_url=url_for('birthday', slug=slug, _external=True))


@app.route('/b/<slug>')
def birthday(slug):
    with db() as conn:
        page = conn.execute('SELECT * FROM pages WHERE slug = ?', (slug,)).fetchone()
        if not page: abort(404)
        photos = conn.execute('SELECT filename, caption FROM photos WHERE page_slug = ?', (slug,)).fetchall()
    return render_template('birthday.html', page=page, photos=photos)


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    # Only serve a plain basename from the configured upload folder.
    from flask import send_from_directory
    if Path(filename).name != filename:
        abort(404)
    return send_from_directory(UPLOAD_DIR, filename, as_attachment=False, max_age=3600)


@app.errorhandler(413)
def too_large(_error):
    flash('The upload is too large. Please keep the total under 24 MB.', 'error')
    return render_template('create.html'), 413


@app.errorhandler(404)
def not_found(_error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
