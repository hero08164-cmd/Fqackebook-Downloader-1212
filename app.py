from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI(
    title="Premium Facebook Downloader API",
    description="Render Integrated Dedicated Engine",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------
# 1. DEVELOPER API ENDPOINT (Using sh13y Dedicated Engine)
# ----------------------------------------------------
@app.get("/api/download")
async def download_api(url: str = Query(..., description="Facebook Video/Reels URL")):
    if not url:
        raise HTTPException(status_code=400, detail="URL missing hai boss!")
        
    # Target production API base URL
    target_api = "https://facebook-video-download-api-qb6o.onrender.com/info"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # sh13y API expects a POST request with JSON payload {"url": "..."}
            response = await client.post(target_api, json={"url": url})
            
            if response.status_code == 200:
                data = response.json()
                
                # Check mapping based on standard FastAPI response structure
                if data.get("status") == "success" or "download_url" in data:
                    return {
                        "status": "success",
                        "developer": "sh13y-integrated-node",
                        "platform": "Facebook",
                        "title": data.get("video_info", {}).get("title", "FB Video"),
                        "thumbnail": data.get("video_info", {}).get("thumbnail", ""),
                        "download_url": data.get("download_url")
                    }
            
            # Fallback if status isn't 200 or custom schema mismatch
            raise HTTPException(status_code=400, detail="Target API process filter edge failure.")
            
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail="Target API responds with error layer.")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Engine connection failed: {str(e)}")

# ----------------------------------------------------
# 2. RESPONSIVE FRONTEND WEB INTERFACE
# ----------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def home_page():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FB Reels Downloader</title>
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; font-family: Arial, sans-serif; }
            body { background: linear-gradient(135deg, #1877f2 0%, #0056b3 100%); display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 20px; }
            .wrapper { background: white; padding: 40px 30px; border-radius: 16px; box-shadow: 0px 10px 30px rgba(0,0,0,0.2); width: 100%; max-width: 480px; text-align: center; }
            h1 { color: #1877f2; margin-bottom: 10px; font-size: 26px; }
            p { color: #666; margin-bottom: 25px; font-size: 14px; }
            input { width: 100%; padding: 15px; border: 2px solid #e2e8f0; border-radius: 8px; font-size: 16px; outline: none; margin-bottom: 15px; }
            button { width: 100%; padding: 15px; background: #1877f2; color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; }
            #loader { display: none; margin-top: 20px; color: #1877f2; font-weight: bold; }
            #result { margin-top: 25px; display: none; background: #f7fafc; padding: 20px; border-radius: 8px; text-align: left; border-left: 5px solid #2b6cb0; }
            .dl-btn { display: inline-block; text-align: center; width: 100%; padding: 12px; background: #48bb78; color: white; text-decoration: none; border-radius: 6px; font-weight: bold; margin-top: 10px; }
        </style>
    </head>
    <body>
        <div class="wrapper">
            <h1>FB Reels Downloader</h1>
            <p>100% Stable Dual-Mode API & Website</p>
            
            <input type="text" id="fbUrl" placeholder="Paste Facebook Link Here...">
            <button onclick="downloadFBVideo()">Download Now</button>

            <div id="loader">Extracting High-Quality Video Engine... ⏳</div>

            <div id="result">
                <div style="font-weight: bold; color: #2d3748; margin-bottom: 5px;" id="videoTitle">🎉 Video Ready Boss!</div>
                <a href="#" id="hdLink" target="_blank" class="dl-btn">📥 Save Video (MP4)</a>
            </div>
        </div>

        <script>
            async function downloadFBVideo() {
                var url = document.getElementById('fbUrl').value.trim();
                var loader = document.getElementById('loader');
                var resultDiv = document.getElementById('result');

                if (!url) {
                    alert('Pehle link dalo boss!');
                    return;
                }

                loader.style.display = 'block';
                resultDiv.style.display = 'none';

                try {
                    var response = await fetch('/api/download?url=' + encodeURIComponent(url));
                    var data = await response.json();

                    if (response.ok && data.status === "success") {
                        document.getElementById('hdLink').href = data.download_url;
                        if(data.title) {
                            document.getElementById('videoTitle').innerText = "🎥 " + data.title;
                        }
                        loader.style.display = 'none';
                        resultDiv.style.display = 'block';
                    } else {
                        loader.style.display = 'none';
                        alert("Error: " + (data.detail || "Video link process fail ho gayi."));
                    }
                } catch (err) {
                    loader.style.display = 'none';
                    alert("API Server under maintenance ya slow hai!");
                }
            }
        </script>
    </body>
    </html>
    """
