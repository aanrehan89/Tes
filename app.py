import os
import shutil
import tempfile
from flask import Flask, render_template, request, send_file, redirect, url_for, flash
import yt_dlp

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "ganti_dengan_rahasia")  # ganti di env
DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def yt_dlp_download(url: str, target_dir: str) -> str:
    """
    Download video dengan yt-dlp ke target_dir. Return path file.
    """
    outtmpl = os.path.join(target_dir, "downloaded_video.%(ext)s")
    ydl_opts = {
        "outtmpl": outtmpl,
        "format": "mp4[height<=720]+bestaudio/best",
        "quiet": True,
        "merge_output_format": "mp4",
        # Jika server headless tanpa ffmpeg, pastikan ffmpeg terinstal
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        if not filename.endswith(".mp4"):
            filename = filename.rsplit(".", 1)[0] + ".mp4"
        return filename

def is_allowed_url(url: str) -> bool:
    url = url.lower().strip()
    # validasi sederhana: hanya izinkan domain tiktok / instagram
    return ("tiktok.com" in url) or ("instagram.com" in url) or ("vm.tiktok.com" in url)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/download", methods=["POST"])
def download():
    url = request.form.get("url", "").strip()
    if not url:
        flash("Masukkan URL terlebih dahulu.")
        return redirect(url_for("index"))

    if not is_allowed_url(url):
        flash("Hanya URL TikTok atau Instagram yang diizinkan.")
        return redirect(url_for("index"))

    # buat temp dir untuk setiap request supaya aman
    tmpdir = tempfile.mkdtemp(dir=DOWNLOAD_DIR)
    try:
        # lakukan download (blocking)
        filepath = yt_dlp_download(url, tmpdir)
        if not os.path.exists(filepath):
            flash("Gagal mengunduh video.")
            return redirect(url_for("index"))

        # kirim file sebagai attachment (download)
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        flash(f"Error saat mengunduh: {e}")
        return redirect(url_for("index"))
    finally:
        # bersihkan folder temp (jika file sudah dikirim, send_file membaca file sebelum kode lanjut)
        # untuk safety, hapus tmpdir pada akhirnya
        try:
            shutil.rmtree(tmpdir)
        except Exception:
            pass

if __name__ == "__main__":
    # untuk production: gunakan gunicorn/uvicorn dan reverse-proxy
    app.run(host="0.0.0.0", port=5000, debug=False)