from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI(title="Render FB Downloader API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dummy API Endpoint for compatibility (Kyuki Facebook server IPs ko block kar raha hai)
@app.get("/api/download")
def download_api(url: str = Query(..., description="FB Link")):
    if not url:
        raise HTTPException(status_code=400, detail="URL missing hai boss!")
    # Agar developers use kar rahe hain, toh unhe alert milega
    raise HTTPException(status_code=400, detail="Server IP rate-limited by Facebook. Please use Frontend Downloader.")

@app.get("/", response_class=HTMLResponse)
def home_page():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FB Downloader - Anti Block Edition</title>
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
            <p style="color: green; font-weight: bold;">🛡️ Anti-Block Client Mode</p>
            <input type="text" id="fbUrl" placeholder="Paste Facebook link here...">
            <button onclick="downloadVideo()">Download Now</button>
            <div id="loader">Processing... ⏳</div>
            <div id="result">
                <div id="title" style="font-weight:bold; word-break:break-all; margin-bottom: 5px;">Facebook Video</div>
                <a href="#" id="dlBtn" target="_blank" class="dl-link">📥 Save Video (High Quality)</a>
            </div>
        </div>
        <script>
            async function downloadVideo() {
                const url = document.getElementById('fbUrl').value.trim();
                if(!url) return alert('Link dalo boss!');
                
                document.getElementById('loader').style.display = 'block';
                document.getElementById('result').style.display = 'none';
                
                try {
                    // SERVER BYPASS: Hum direct client-side open-scrapers ka use kar rahe hain
                    // Jo Facebook ke block page ko bypass kar dete hain
                    const response = await fetch('https://api.samir.pro/download/facebook?url=' + encodeURIComponent(url));
                    const resData = await response.json();
                    
                    document.getElementById('loader').style.display = 'none';
                    
                    if(resData && resData.result && resData.result.hd) {
                        document.getElementById('dlBtn').href = resData.result.hd;
                        document.getElementById('result').style.display = 'block';
                    } else if(resData && resData.result && resData.result.sd) {
                        document.getElementById('dlBtn').href = resData.result.sd;
                        document.getElementById('result').style.display = 'block';
                    } else {
                        alert('Error: Facebook security high hai abhi. Dusra link try karein boss!');
                    }
                } catch(e) {
                    document.getElementById('loader').style.display = 'none';
                    alert('Network error ya link down hai!');
                }
            }
        </script>
    </body>
    </html>
    """
