import streamlit as st

# --- PAGE SETUP ---
st.set_page_config(page_title="VisionPulse AI", layout="centered")
st.title("👁️ VisionPulse AI")
st.write("Niche diye gaye button par click karein aur Camera Permission 'Allow' karein.")

# --- GET API KEY ---
try:
    API_KEY = st.secrets["API_KEY"]
except:
    st.error("API Key nahi mili! Streamlit Secrets check karo.")
    st.stop()

# --- THE MASTERSTROKE: DIRECT BROWSER TO GEMINI API ---
# Hum pura logic Frontend (JS) mein handle kar rahe hain taaki delay na ho
html_code = f"""
    <div style="text-align: center;">
        <button id="startBtn" style="padding: 15px 30px; font-size: 18px; background-color: #4CAF50; color: white; border: none; border-radius: 10px; cursor: pointer; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
            Start Assistant
        </button>
        <p id="status" style="margin-top:15px; font-size:16px; color:#FFD700;">System Ready</p>
    </div>
    
    <video id="video" autoplay playsinline style="width:100%; margin-top: 10px; border-radius:10px; display:none; border: 3px solid #4CAF50;"></video>
    <canvas id="canvas" style="display:none;"></canvas>
    
    <div id="output_box" style="margin-top:20px; padding:15px; background-color:#2e2e2e; color:#fff; border-radius:10px; min-height:60px; font-size:22px; text-align:center; display:none; box-shadow: 0 4px 8px rgba(0,0,0,0.5);">
        <span id="result_text">Aas-paas ka drishya yahan aayega...</span>
    </div>

    <script>
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const startBtn = document.getElementById('startBtn');
    const statusText = document.getElementById('status');
    const outputBox = document.getElementById('output_box');
    const resultText = document.getElementById('result_text');

    // Passing key from Python to JS safely for this prototype
    const GEMINI_API_KEY = "{API_KEY}";

    startBtn.onclick = async () => {{
        try {{
            // Request Back Camera
            const stream = await navigator.mediaDevices.getUserMedia({{ 
                video: {{ facingMode: "environment" }},
                audio: false 
            }});
            video.srcObject = stream;
            video.style.display = "block";
            startBtn.style.display = "none";
            outputBox.style.display = "block";
            statusText.innerText = "Camera Chalu Hai! Har 5 second me scan hoga...";
            statusText.style.color = "#4CAF50";
            
            // Pehla scan 2 second baad
            setTimeout(processFrame, 2000);
            
            // Uske baad har 5 second (5000ms) mein pulse
            setInterval(processFrame, 5000);
            
        }} catch (err) {{
            statusText.innerText = "Camera Permission Denied!";
            statusText.style.color = "red";
        }}
    }};

    async function processFrame() {{
        statusText.innerText = "Aankhein scan kar rahi hain... 🔍";
        
        // 1. Photo kheencho
        const context = canvas.getContext('2d');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        // 2. Image ko Base64 format mein badlo (Compression 0.5 for fast speed)
        const imageDataFull = canvas.toDataURL('image/jpeg', 0.5);
        const base64Image = imageDataFull.split(',')[1]; 

        // 3. Gemini Prompt
        const promptStr = "Describe the scene concisely in ONE short sentence in HINDI. Mention any obstacles. Example: 'Aapke samne ek kursi hai, dhayan se chalein.'";
        
        const requestBody = {{
            "contents": [{{
                "parts": [
                    {{"text": promptStr}},
                    {{"inlineData": {{"mimeType": "image/jpeg", "data": base64Image}}}}
                ]
            }}]
        }};

        // 4. Direct Call to Google Gemini
        try {{
            const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${{GEMINI_API_KEY}}`, {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify(requestBody)
            }});
            
            const data = await response.json();
            
            if(data.candidates && data.candidates.length > 0) {{
                const description = data.candidates[0].content.parts[0].text;
                
                // Text dikhao
                resultText.innerText = description;
                statusText.innerText = "Next scan in 5 seconds... ⏱️";
                
                // Audio mein bolo (Native Browser TTS)
                const speech = new SpeechSynthesisUtterance(description);
                speech.lang = 'hi-IN';
                speech.rate = 1.0; 
                window.speechSynthesis.speak(speech);
            }} else {{
                resultText.innerText = "Kuch samajh nahi aaya, dubara try kar raha hu.";
            }}
            
        }} catch (e) {{
            console.error(e);
            statusText.innerText = "Internet ya API Error aaya!";
            statusText.style.color = "red";
        }}
    }}
    </script>
"""

# HTML component ko screen par render karo
st.components.v1.html(html_code, height=650)
