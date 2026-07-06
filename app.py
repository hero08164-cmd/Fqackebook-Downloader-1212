from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
import re
import requests

app = FastAPI(title="Render FB Downloader API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_fb_video(video_url):
    # JUGAD: Agar share/r wala link hai, toh uski asli redirected URL nikalna
    if "share/r" in video_url or "facebook.com/share" in video_url:
        try:
            # Server se ek choti HEAD request bhej kar asli link pata karenge
            response = requests.head(video_url, allow_redirects=True, timeout=10)
            video_url = response.url
        except Exception:
            pass # Agar network fail ho toh standard link hi rehne dein

    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'socket_timeout': 20,
        'nocheckcertificate': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        }
    }
    # Baaki niche ka code same rahega...
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            # Formats check karna agar direct url blank mile
            download_url = info.get("url")
            if not download_url and info.get("formats"):
                # Filters to get normal progressive formats (mp4)
                for f in reversed(info["formats"]):
                    if f.get("vcodec") != "none" and f.get("acodec") != "none" and f.get("url"):
                        download_url = f.get("url")
                        break
                if not download_url:
                    download_url = info["formats"][-1].get("url")
                
            if not download_url:
                return {"status": "error", "message": "Facebook secure login wall hit ho gayi boss. Dusra link try karein."}

            return {
                "status": "success",
                "title": info.get("title", "Facebook Video"),
                "download_url": download_url,
                "thumbnail": info.get("thumbnail")
            }
    except Exception as e:
        # JUGAD 3: Agar normal extraction fail ho jaye, toh clean generic error message
        return {"status": "error", "message": f"Parsing failed. Link protection active. Error: {str(e)}"}

@app.get("/api/download")
def download_api(url: str = Query(..., description="FB Link")):
    if not url:
        raise HTTPException(status_code=400, detail="URL missing hai boss!")
    result = extract_fb_video(url)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@app.get("/", response_class=HTMLResponse)
def home_page():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FB Downloader - Render</title>
        <style>
            body { font-family: Arial, sans-serif; background: #1877f2; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
            .box { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 5px 15px rgba(0,0,0,0.2); width: 90%; max-width: 450px; text-align: center; }
            input { width: 100%; padding: 12px; margin: 15px 0; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box; font-size: 15px; }
            button { width: 100%; padding: 12px; background: #0056b3; color: white; border: none; border-radius: 6px; font-size: 16px; font-weight: bold; cursor: pointer; }
            #loader { display: none; margin-top: 15px; font-weight: bold; color: #1877f2; }
            #result { display: none; margin-top: 20px; padding: 15px; background: #f0f2f5; border-radius: 6px; text-align: left; }
            .dl-link { display: block; text-align: center; margin-top: 10px; background: #28a745; color: white; padding: 10px; text-decoration: none; border-radius: 4px; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="box">
            <h2>FB Reels Downloader</h2>
            <p>Render Free Hosting Edition</p>
            <input type="text" id="fbUrl" placeholder="Paste Facebook link here...">
            <button onclick="downloadVideo()">Download Now</button>
            <div id="loader">Processing... ⏳</div>
            <div id="result">
                <div id="title" style="font-weight:bold; word-break:break-all;"></div>
                <a href="#" id="dlBtn" target="_blank" class="dl-link">📥 Save Video</a>
            </div>
        </div>
        <script>
            async function downloadVideo() {
                const url = document.getElementById('fbUrl').value.trim();
                if(!url) return alert('Link dalo boss!');
                document.getElementById('loader').style.display = 'block';
                document.getElementById('result').style.display = 'none';
                try {
                    const res = await fetch(`/api/download?url=${encodeURIComponent(url)}`);
                    const data = await res.json();
                    document.getElementById('loader').style.display = 'none';
                    if(res.ok) {
                        document.getElementById('title').innerText = data.title;
                        document.getElementById('dlBtn').href = data.download_url;
                        document.getElementById('result').style.display = 'block';
                    } else { alert('Error: ' + data.detail); }
                } catch(e) { document.getElementById('loader').style.display = 'none'; alert('Server error ya link login mang raha hai!'); }
            }
        </script>
    </body>
    </html>
    """
    
