from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import json
import re

app = FastAPI(
    title="Premium Social Media Downloader API",
    description="Free API to download Facebook Reels, Videos, and more!",
    version="1.1.12"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_video_link(video_url):
    try:
        # social-media-downloader ko CLI (command line) ke zariye call kar rahe hain JSON output ke liye
        # --json ya -j flag check karne ke liye standard subprocess call lagayi hai
        command = ["social-media-downloader", video_url, "--json"]
        
        # Command execute karke response capture kar rahe hain
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        
        if result.stdout:
            data = json.loads(result.stdout.strip())
            # Library ke output structure ke mutabiq best quality link nikalna
            download_url = data.get("url") or data.get("download_url") or data.get("direct_link")
            
            if download_url:
                return {
                    "status": "success",
                    "title": data.get("title", "Social Media Video"),
                    "download_url": download_url,
                    "thumbnail": data.get("thumbnail")
                }
                
        # Fallback agar command direct link na de par logs clean ho
        return {"status": "error", "message": "Video stream link nahi mil payi boss."}
        
    except subprocess.CalledProcessError as e:
        # Agar short links ke redirection me issue aaye toh error handle karne ke liye
        return {"status": "error", "message": f"Library extraction failed: {e.stderr}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ----------------------------------------------------
# 1. DUSRE DEVELOPERS KE LIYE: API ENDPOINT
# ----------------------------------------------------
@app.get("/api/download")
def download_api(url: str = Query(..., description="Video ka URL dalein")):
    if not url:
        raise HTTPException(status_code=400, detail="URL dalna zaroori hai boss!")
    
    result = extract_video_link(url)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
        
    return result

# ----------------------------------------------------
# 2. USERS KE LIYE: CLEAN WEBSITE FRONTEND
# ----------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def home_page():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>All-in-One Social Media Downloader</title>
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Arial, sans-serif; }
            body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #333; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 20px; }
            .wrapper { background: white; padding: 40px 30px; border-radius: 16px; box-shadow: 0px 10px 30px rgba(0,0,0,0.2); width: 100%; max-width: 500px; text-align: center; }
            h1 { color: #764ba2; margin-bottom: 10px; font-size: 26px; }
            p { color: #666; margin-bottom: 25px; font-size: 14px; }
            .input-group { display: flex; flex-direction: column; gap: 15px; }
            input { width: 100%; padding: 15px; border: 2px solid #e2e8f0; border-radius: 8px; font-size: 16px; outline: none; transition: 0.3s; }
            input:focus { border-color: #764ba2; }
            button { width: 100%; padding: 15px; background: #764ba2; color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; transition: 0.3s; }
            button:hover { background: #5a377d; }
            #loader { display: none; margin-top: 20px; color: #764ba2; font-weight: bold; }
            #result { margin-top: 25px; display: none; background: #f7fafc; padding: 20px; border-radius: 8px; text-align: left; }
            .video-title { font-weight: bold; margin-bottom: 15px; font-size: 15px; color: #2d3748; word-break: break-all; }
            .dl-btn { display: inline-block; text-align: center; width: 100%; padding: 12px; background: #48bb78; color: white; text-decoration: none; border-radius: 6px; font-weight: bold; transition: 0.3s; }
            .dl-btn:hover { background: #38a169; }
        </style>
    </head>
    <body>
        <div class="wrapper">
            <h1>Social Media Downloader</h1>
            <p>Paste Facebook, Instagram, or TikTok links below to download free!</p>
            
            <div class="input-group">
                <input type="text" id="videoUrl" placeholder="Paste your link here...">
                <button onclick="processVideo()">Download Video</button>
            </div>

            <div id="loader">Extracting high quality stream... ⏳</div>

            <div id="result">
                <div class="video-title" id="vTitle">Video Ready</div>
                <a href="#" id="vLink" target="_blank" class="dl-btn">📥 Save Video to Device</a>
            </div>
        </div>

        <script>
            async function processVideo() {
                const urlInput = document.getElementById('videoUrl').value.trim();
                const loader = document.getElementById('loader');
                const resultDiv = document.getElementById('result');
                
                if (!urlInput) {
                    alert('Boss, pehle link toh dalo!');
                    return;
                }

                loader.style.display = 'block';
                resultDiv.style.display = 'none';

                try {
                    const response = await fetch(`/api/download?url=${encodeURIComponent(urlInput)}`);
                    const data = await response.json();

                    loader.style.display = 'none';

                    if (response.ok) {
                        document.getElementById('vTitle').innerText = data.title || "Facebook Video";
                        document.getElementById('vLink').href = data.download_url;
                        resultDiv.style.display = 'block';
                    } else {
                        alert('Error: ' + (data.detail || 'Extraction me dikkat aayi. Dusra link try karein!'));
                    }
                } catch (error) {
                    loader.style.display = 'none';
                    alert('Server response error!');
                }
            }
        </script>
    </body>
    </html>
    """
