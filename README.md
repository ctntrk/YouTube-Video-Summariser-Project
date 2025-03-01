# YouTube Video Summarizer

### Demo Video
([Drive](https://drive.google.com/file/d/1294Xwz75NfhJOdom50WJI3DTj9B3XcmE/view?usp=sharing))

# This is a working video of the YouTube Video Summariser project. This video is at 4x speed.



## Overview
This project is a Flask-based web application that downloads audio from a YouTube video, transcribes it, generates a summary, and displays relevant statistics. To run the application, you need Python, specific libraries, FFmpeg, and a virtual environment set up on your system.

## Prerequisites
- **Python 3.8+**: Verify with `python --version`. Download from [python.org](https://www.python.org/) if not installed.
- **Git (Optional)**: Required for cloning the repository. Check with `git --version`. Install from [git-scm.com](https://git-scm.com/) if needed.
- **FFmpeg**: Necessary for audio processing (installation steps below).

## Setup Instructions

### 1. Create Project Directory
```bash
mkdir youtube-summary
cd youtube-summary
```

### 2. Set Up Virtual Environment
Create and activate a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
source venv/bin/activate  # On macOS/Linux
```
You’ll see `(venv)` in your terminal when activated.

### 3. Create Project Files
- **Main Application File (`app.py`)**  
  Create `app.py` and add the following code:
  ```python
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
  ```

- **HTML Templates**  
  Create a `templates` folder:
  ```bash
  mkdir templates
  ```
  Add the following files inside `templates/`:

  - `index.html`:
    ```html
    <!DOCTYPE html>
    <html>
    <head>
        <title>YouTube Summarizer</title>
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
    </head>
    <body>
        <div class="container mt-5">
            <h1 class="mb-4">YouTube Video Summarizer</h1>
            <form method="POST">
                <div class="form-group">
                    <input type="text" class="form-control" name="url" placeholder="Enter YouTube URL" required>
                </div>
                <button type="submit" class="btn btn-primary">Summarize</button>
            </form>
        </div>
    </body>
    </html>
    ```

  - `result.html`:
    ```html
    <!DOCTYPE html>
    <html>
    <head>
        <title>Results</title>
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
    </head>
    <body>
        <div class="container mt-5">
            <h1>Processing Results</h1>
            <div class="card mt-4">
                <div class="card-header">Statistics</div>
                <div class="card-body">
                    <p><strong>Transcript:</strong> {{ stats.transcript_chars }} characters / {{ stats.transcript_words }} words</p>
                    <p><strong>Summary:</strong> {{ stats.summary_chars }} characters / {{ stats.summary_words }} words</p>
                </div>
            </div>
            <div class="card mt-4">
                <div class="card-header">Transcript (First 500 Characters)</div>
                <div class="card-body">
                    <p>{{ transcript[:500] }}...</p>
                </div>
            </div>
            <div class="card mt-4">
                <div class="card-header">Summary</div>
                <div class="card-body">
                    <p>{{ summary }}</p>
                </div>
            </div>
            <a href="/" class="btn btn-secondary mt-4">Go Back</a>
        </div>
    </body>
    </html>
    ```

  - `error.html`:
    ```html
    <!DOCTYPE html>
    <html>
    <head>
        <title>Error</title>
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
    </head>
    <body>
        <div class="container mt-5">
            <div class="alert alert-danger">
                <h4>An Error Occurred!</h4>
                <p>{{ error }}</p>
            </div>
            <a href="/" class="btn btn-secondary">Go Back</a>
        </div>
    </body>
    </html>
    ```

### 4. Install Dependencies
Install the required Python libraries (CPU version):
```bash
pip install flask yt-dlp openai-whisper transformers torch --extra-index-url https://download.pytorch.org/whl/cpu
```
**Note**: The first run downloads Whisper and BART models (2-3 GB), which may take time.

### 5. Install FFmpeg
- **Windows**: Use Winget:
  ```bash
  winget install Gyan.FFmpeg
  ```
  Confirm with "Y" and restart your terminal.
- **Verify**: Run `ffmpeg -version`. You should see version details.

### 6. Run the Application
Activate the virtual environment (if not already active):
```bash
venv\Scripts\activate  # On Windows
source venv/bin/activate  # On macOS/Linux
```
Start the Flask app:
```bash
python app.py
```
Visit [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

### 7. Test the Application
Enter a YouTube URL (e.g., `https://www.youtube.com/watch?v=X7j8F16eSqs`) and click "Summarize" to see the results.

## Troubleshooting
- **"ModuleNotFoundError"**: Re-run the `pip install` command from step 4.
- **"ffmpeg not found"**: Add FFmpeg’s `bin` folder (e.g., `C:\Program Files\ffmpeg\bin`) to your PATH.
- **Slow Processing**: Normal for CPU. Install a CUDA-supported PyTorch version for GPU acceleration.

## Example Terminal Commands
```
C:\Users\User>mkdir youtube-summary
C:\Users\User>cd youtube-summary
C:\Users\User\youtube-summary>python -m venv venv
C:\Users\User\youtube-summary>venv\Scripts\activate
(venv) C:\Users\User\youtube-summary>pip install flask yt-dlp openai-whisper transformers torch --extra-index-url https://download.pytorch.org/whl/cpu
(venv) C:\Users\User\youtube-summary>winget install Gyan.FFmpeg
(venv) C:\Users\User\youtube-summary>python app.py
```

## Support
If you encounter issues, feel free to reach out with details—I’ll help you resolve them quickly! Good luck! 🌟
