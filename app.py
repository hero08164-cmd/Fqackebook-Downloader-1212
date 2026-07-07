from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx # Iske liye requirements.txt me httpx likhna zaroori hai

app = FastAPI(
    title="Premium Facebook Downloader API",
    description="Developers ke liye free API aur users ke liye tools",
    version="1.0.0"
)

# CORS Allow karna zaroori hai taaki dusre developers ki website se aapki API block na ho
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------
# 1. DUSRE DEVELOPERS KE LIYE: REAL API ENDPOINT
# ----------------------------------------------------
@app.get("/api/download")
async def download_api(url: str = Query(..., description="Facebook Video/Reels ka URL yahan dalein")):
    if not url:
        raise HTTPException(status_code=400, detail="Boss, URL dalna zaroori hai!")
        
    # Multi-Proxy Web Scraper Pipeline
    proxies = [
        f"https://api.allorigins.win/get?url={url}",
        f"https://api.codetabs.com/v1/proxy?quest={url}",
        f"https://corsproxy.io/?{url}"
    ]
    
    html_content = ""
    async with httpx.AsyncClient(timeout=10.0) as client:
        for p_url in proxies:
            try:
                response = await client.get(p_url)
                if response.status_code == 200:
                    # Allorigins JSON response deta hai, baki raw text dete hain
                    if "allorigins" in p_url:
                        html_content = response.json().get("contents", "")
                    else:
                        html_content = response.text
                        
                    if html_content and len(html_content) > 1000:
                        break
            except Exception:
                continue

    if not html_content:
        raise HTTPException(status_code=500, detail="Saare scraping servers busy hain, thodi der baad try karein.")

    # HTML me se HD/SD direct MP4 video link nikalna
    final_video_url = ""
    if '"browser_native_hd_url":"' in html_content:
        final_video_url = html_content.split('"browser_native_hd_url":"')[1].split('"')[0]
    elif '"browser_native_sd_url":"' in html_content:
        final_video_url = html_content.split('"browser_native_sd_url":"')[1].split('"')[0]
    elif 'hd_src:"' in html_content:
        final_video_url = html_content.split('hd_src:"')[1].split('"')[0]
    elif 'sd_src:"' in html_content:
        final_video_url = html_content.split('sd_src:"')[1].split('"')[0]

    if final_video_url:
        # JSON standard formats me convert karna (Backslashes clean karke)
        clean_url = final_video_url.replace(r'\\', '').replace(r'\/', '/')
        
        # Dusre developers ko ek professional JSON output milega
        return {
            "status": "success",
            "developer": "sh13y clone",
            "platform": "Facebook",
            "download_url": clean_url
        }
    
    raise HTTPException(status_code=404, detail="Video link nahi mil payi. Ya toh video private hai ya link galat hai.")

# ----------------------------------------------------
# 2. USERS KE LIYE: FRONTEND WEBSITE
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

            <div id="loader">Extracting Video via API... ⏳</div>

            <div id="result">
                <div style="font-weight: bold; color: #2d3748; margin-bottom: 5px;">🎉 Video Ready Boss!</div>
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
                    // Ab hamara frontend bhi hamari banayi hui real API ko hit karega!
                    var response = await fetch('/api/download?url=' + encodeURIComponent(url));
                    var data = await response.json();

                    if (response.ok && data.status === "success") {
                        document.getElementById('hdLink').href = data.download_url;
                        loader.style.display = 'none';
                        resultDiv.style.display = 'block';
                    } else {
                        loader.style.display = 'none';
                        alert("Error: " + (data.detail || "Link extract nahi ho payi."));
                    }
                } catch (err) {
                    loader.style.display = 'none';
                    alert("API Server respond nahi kar raha hai!");
                }
            }
        </script>
    </body>
    </html>
    """
