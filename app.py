from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import json
import traceback

app = FastAPI(title="Social Media Downloader Debug Edition")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_video_link(video_url):
    try:
        # Command run kar rahe hain bina code crash kiye output dekhne ke liye
        command = ["social-media-downloader", video_url, "--json"]
        result = subprocess.run(command, capture_output=True, text=True)
        
        # Debugging ke liye Render ke logs me print karega
        print("STDOUT OUTPUT:", result.stdout)
        print("STDERR OUTPUT:", result.stderr)
        
        if result.returncode == 0 and result.stdout:
            try:
                data = json.loads(result.stdout.strip())
                download_url = data.get("url") or data.get("download_url") or data.get("direct_link")
                if download_url:
                    return {
                        "status": "success",
                        "title": data.get("title", "Facebook Video"),
                        "download_url": download_url
                    }
            except json.JSONDecodeError:
                # Agar output JSON nahi hai, toh raw text se URL nikalne ki koshish karenge
                pass

        # METHOD 2: Agar JSON flag kaam nahi kar raha, toh bina flag ke chala kar output check karte hain
        raw_command = ["social-media-downloader", video_url]
        raw_result = subprocess.run(raw_command, capture_output=True, text=True)
        print("RAW CLIENT OUTPUT:", raw_result.stdout)
        
        # Raw text me se http/https link extract karna
        urls = re.findall(r'(https?://[^\s]+)', raw_result.stdout)
        if urls:
            # Sabse aakhri ya pehli url jo video stream ho sakti hai
            return {"status": "success", "title": "Extracted Video", "download_url": urls[0]}

        return {
            "status": "error", 
            "message": f"Extraction failed. Server Logs: {result.stderr or raw_result.stdout}"
        }
        
    except Exception as e:
        print("CRASH LOG:", traceback.format_exc())
        return {"status": "error", "message": f"Internal Error: {str(e)}"}

@app.get("/api/download")
def download_api(url: str = Query(..., description="Video URL")):
    if not url:
        raise HTTPException(status_code=400, detail="URL missing hai boss!")
    result = extract_video_link(url)
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
        <title>FB Downloader - Debug Mode</title>
        <style>
            body { font-family: Arial, sans-serif; background: #764ba2; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
            .box { background: white; padding: 30px; border-radius: 12px; width: 90%; max-width: 450px; text-align: center; }
            input { width: 100%; padding: 12px; margin: 15px 0; border: 1px solid #ccc; border-radius: 6px; }
            button { width: 100%; padding: 12px; background: #764ba2; color: white; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; }
            #loader { display: none; margin-top: 15px; font-weight: bold; }
            #result { display: none; margin-top: 20px; padding: 15px; background: #f0f2f5; border-radius: 6px; text-align: left; }
        </style>
    </head>
    <body>
        <div class="box">
            <h2>Social Media Downloader</h2>
            <p>Debug Log Edition</p>
            <input type="text" id="fbUrl" placeholder="Paste link here...">
            <button onclick="downloadVideo()">Download Now</button>
            <div id="loader">Processing... ⏳</div>
            <div id="result">
                <a href="#" id="dlBtn" target="_blank" style="display:block; text-align:center; background:green; color:white; padding:10px; text-decoration:none; border-radius:4px;">📥 Download Video</a>
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
                        document.getElementById('dlBtn').href = data.download_url;
                        document.getElementById('result').style.display = 'block';
                    } else { alert('Error: ' + data.detail); }
                } catch(e) { document.getElementById('loader').style.display = 'none'; alert('Error reading output!'); }
            }
        </script>
    </body>
    </html>
    """
