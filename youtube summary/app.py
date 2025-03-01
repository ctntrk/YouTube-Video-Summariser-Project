from flask import Flask, render_template, request
import yt_dlp
import whisper
from transformers import pipeline

app = Flask(__name__)

def download_audio(url):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "audio",
        "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "wav"}],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return "audio.wav"

def transcribe(audio_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result["text"]

def summarize(text):
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
    summaries = []
    for chunk in chunks:
        summary = summarizer(chunk, max_length=150, min_length=30)[0]["summary_text"]
        summaries.append(summary)
    return " ".join(summaries)

def count_words(text):
    return len(text.split())

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        try:
            audio_path = download_audio(url)
            transcript = transcribe(audio_path)
            summary = summarize(transcript)
            stats = {
                'transcript_chars': len(transcript),
                'transcript_words': count_words(transcript),
                'summary_chars': len(summary),
                'summary_words': count_words(summary)
            }
            return render_template('result.html', 
                                transcript=transcript,
                                summary=summary,
                                stats=stats)
        except Exception as e:
            return render_template('error.html', error=str(e))
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
