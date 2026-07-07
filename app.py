from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Ultimate FB Downloader Fixed")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/download")
def download_api():
    return {"status": "client_mode"}

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
            <p>100% Stable Client Extraction</p>
            
            <input type="text" id="fbUrl" placeholder="Paste Facebook Link Here...">
            <button onclick="downloadFBVideo()">Download Now</button>

            <div id="loader">Extracting Video... ⏳</div>

            <div id="result">
                <div style="font-weight: bold; color: #2d3748; margin-bottom: 5px;">🎉 Video Ready!</div>
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
                    var proxyUrl = 'https://api.allorigins.win/get?url=' + encodeURIComponent(url);
                    var response = await fetch(proxyUrl);
                    var data = await response.json();
                    var htmlContent = data.contents;

                    var hdMatch = htmlContent.match(/"browser_native_hd_url":"(.*?)"/) || htmlContent.match(/hd_src:"(.*?)"/);
                    var sdMatch = htmlContent.match(/"browser_native_sd_url":"(.*?)"/) || htmlContent.match(/sd_src:"(.*?)"/);
                    
                    var finalVideoUrl = "";
                    if (hdMatch && hdMatch[1]) {
                        finalVideoUrl = hdMatch[1];
                    } else if (sdMatch && sdMatch[1]) {
                        finalVideoUrl = sdMatch[1];
                    }

                    if (!finalVideoUrl) {
                        var fallbackMatch = htmlContent.match(/video_url":"(.*?)"/);
                        if (fallbackMatch && fallbackMatch[1]) {
                            finalVideoUrl = fallbackMatch[1];
                        }
                    }

                    if (finalVideoUrl) {
                        var cleanUrl = finalVideoUrl.replace(/\\\\/g, '').replace(/\\/g, '');
                        document.getElementById('hdLink').href = cleanUrl;
                        loader.style.display = 'none';
                        resultDiv.style.display = 'block';
                    } else {
                        loader.style.display = 'none';
                        alert("Facebook secure wall hit ho gayi boss. Firse try karein.");
                    }
                } catch (err) {
                    loader.style.display = 'none';
                    alert("Connection temporary slow hai. Firse click karein!");
                }
            }
        </script>
    </body>
    </html>
    """
