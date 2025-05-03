from flask import Flask, request, jsonify, send_file
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

app = Flask(__name__)

def extract_video_id(url):
    try:
        query = urlparse(url)
        if query.hostname == 'youtu.be':
            return query.path[1:]
        if query.hostname in ('www.youtube.com', 'youtube.com'):
            if query.path == '/watch':
                return parse_qs(query.query)['v'][0]
            elif query.path.startswith('/embed/'):
                return query.path.split('/')[2]
            elif query.path.startswith('/v/'):
                return query.path.split('/')[2]
    except Exception:
        return None

@app.route('/')
def home():
    return send_from_directory('.', '/index.html')
@app.route('/transcript', methods=['POST'])
def get_transcript():
    data = request.get_json()
    url = data.get('url')
    video_id = extract_video_id(url)
    if not video_id:
        return jsonify({'error': 'Invalid YouTube URL'}), 400

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        full_text = " ".join([segment['text'] for segment in transcript])
        return jsonify({'transcript': full_text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    import os
port = int(os.environ.get("PORT", 5000))
app.run(host='0.0.0.0', port=port)
