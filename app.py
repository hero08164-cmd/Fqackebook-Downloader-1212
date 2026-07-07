from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI(title="Render FB Downloader API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔑 APNI RAPIDAPI KEY YAHAN DALEIN
RAPIDAPI_KEY = "APNI_X_RAPIDAPI_KEY_YAHAN_DALEIN"

def fetch_via_rapidapi(video_url):
    # Hum ek reliable free-tier proxy API use kar rahe hain RapidAPI se
    url = "https://social-media-video-downloader.p.rapidapi.com/api/v1/facebook/video"
    querystring = {"url": video_url}
    
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "social-media-video-downloader.p.rapidapi.com"
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=15)
        if response.status_code == 200:
            data = response.json()
            # RapidAPI response ke data structure ke mutabiq keys format karein
            links = data.get("links", {})
            download_url = links.get("hd") or links.get("sd") or data.get("url")
            
            if download_url:
                return {
                    "status": "success",
                    "title": data.get("title", "Facebook Video"),
                    "download_url": download_url,
                    "thumbnail": data.get("picture")
                }
        return {"status": "error", "message": "Proxy bypass failed or API limit reached."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/download")
def download_api(url: str = Query(..., description="FB Link")):
    if not url:
        raise HTTPException(status_code=400, detail="URL missing hai boss!")
    
    result = fetch_via_rapidapi(url)
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
        <title>FB Downloader - Premium Proxy Edition</title>
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
            <p style="color: blue; font-weight: bold;">⚡ Premium Proxy Bypass Mode</p>
            <input type="text" id="fbUrl" placeholder="Paste Facebook link here...">
            <button onclick="downloadVideo()">Download Now</button>
            <div id="loader">Processing via Proxy... ⏳</div>
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
                } catch(e) { document.getElementById('loader').style.display = 'none'; alert('Server error!'); }
            }
        </script>
    </body>
    </html>
    """
