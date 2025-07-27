from flask import Flask, request, render_template, send_file
import yt_dlp
import os
import uuid

app = Flask(__name__)
DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    fmt = request.form['format']
    uid = str(uuid.uuid4())
    
    ext = 'mp4' if fmt == 'mp4' else 'mp3'
    output_path = os.path.join(DOWNLOAD_FOLDER, f'{uid}.{ext}')

    if fmt == 'mp3':
        # For mp3, pick audio-only format that doesn't require FFmpeg
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio',
            'outtmpl': output_path,
            'noplaylist': True,
            'quiet': True,
            'postprocessors': [],  # avoid ffmpeg postprocessing
        }
    else:
        # For mp4, pick a progressive (audio+video) format that doesn't need merging
        ydl_opts = {
            'format': 'best[ext=mp4][acodec!=none][vcodec!=none]/best',
            'outtmpl': output_path,
            'noplaylist': True,
            'quiet': True,
            'postprocessors': [],  # no merging or conversions
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return f"Error downloading video: {e}"

if __name__ == '__main__':
    app.run(debug=True)
