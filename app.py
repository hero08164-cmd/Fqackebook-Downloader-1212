from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import requests
import re

app = FastAPI(title="Render FB Downloader API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def bypass_and_fetch(video_url):
    try:
        # Ek free global server ka use kar rahe hain jo direct link nikalta hai
        api_url = "https://expandurl.com/api/v1/shorturl" # Just a fallback resolver representation
        
        # Method 2: High-speed open proxy endpoint for FB
        backend_url = f"https://api.vytv.workers.dev/fb?url={video_url}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(backend_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            # Agar unka server direct link de raha hai
            dl_url = data.get("hd") or data.get("sd") or data.get("url")
            if dl_url:
                return {"status": "success", "title": "Facebook Video", "download_url": dl_url}

        # Method 3: Secondary Open Saver Endpoint
        backup_url = f"https://scrappy-fb.vercel.app/api/json?url={video_url}"
        res_backup = requests.get(backup_url, timeout=10)
        if res_backup.status_code == 200:
            b_data = res_backup.json()
            dl_url = b_data.get("url") or b_data.get("download")
            if dl_url:
                return {"status": "success", "title": "Facebook Video", "download_url": dl_url}

        return {"status": "error", "message": "Sabhi free scrapers busy hain boss. Kuch der baad try karein."}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/download")
def download_api(url: str = Query(..., description="FB Link")):
    if not url:
        raise HTTPException(status_code=400, detail="URL missing hai boss!")
    
    result = bypass_and_fetch(url)
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
        <title>FB Downloader - Ultimate Serverless</title>
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
            <p style="color: purple; font-weight: bold;">🚀 Free Serverless Bypass Mode</p>
            <input type="text" id="fbUrl" placeholder="Paste Facebook link here...">
            <button onclick="downloadVideo()">Download Now</button>
            <div id="loader">Fetching video stream... ⏳</div>
            <div id="result">
                <div id="title" style="font-weight:bold; word-break:break-all; margin-bottom: 5px;">Facebook Video</div>
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
                } catch(e) { document.getElementById('loader').style.display = 'none'; alert('Server response error!'); }
            }
        </script>
    </body>
    </html>
    """
