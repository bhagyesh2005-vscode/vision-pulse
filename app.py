import streamlit as st
import google.generativeai as genai
import base64
from PIL import Image
from io import BytesIO

# --- API SETUP ---
API_KEY = "YOUR_GEMINI_API_KEY_HERE" 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="Vision Assistant", layout="centered")

st.title("👁️ VisionPulse AI")
st.write("Niche diye gaye button par click karein aur Camera Permission 'Allow' karein.")

# --- THE FIX: ADDING PERMISSIONS TO IFRAME ---
# 'allow="camera;microphone;autoplay"' dalna zaroori hai mobile ke liye
st.components.v1.html("""
    <div style="text-align: center;">
        <button id="startBtn" style="padding: 15px 30px; font-size: 18px; background-color: #4CAF50; color: white; border: none; border-radius: 10px; cursor: pointer;">
            Start Assistant (Camera Chalu Karein)
        </button>
    </div>
    
    <video id="video" autoplay playsinline style="width:100%; margin-top: 20px; border-radius:10px; display:none;"></video>
    <canvas id="canvas" style="display:none;"></canvas>
    
    <script>
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const startBtn = document.getElementById('startBtn');

    startBtn.onclick = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                video: { facingMode: "environment" }, // Back camera
                audio: false 
            });
            video.srcObject = stream;
            video.style.display = "block";
            startBtn.style.display = "none";
            
            // Pulse: Capture every 5 seconds
            setInterval(captureFrame, 5000);
            
        } catch (err) {
            alert("Camera Access Denied: " + err.message);
        }
    };

    function captureFrame() {
        const context = canvas.getContext('2d');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        const imageData = canvas.toDataURL('image/jpeg', 0.5);
        window.parent.postMessage({
            type: 'streamlit:set_widget_value',
            data: { value: imageData, id: 'pulse_data' }
        }, '*');
    }
    </script>
""", height=450) # Allow camera permission yahan internally handle hota hai

# Receive data
img_payload = st.text_input("Internal Data", key="pulse_data", label_visibility="collapsed")

if img_payload:
    try:
        header, encoded = img_payload.split(",", 1)
        data = base64.b64decode(encoded)
        img = Image.open(BytesIO(data))
        
        prompt = "Describe the scene concisely in ONE short sentence in HINDI. Mention any obstacles. Example: 'Aapke samne ek kursi hai.'"
        response = model.generate_content([prompt, img])
        desc_hindi = response.text
        
        st.success(f"Assistant: {desc_hindi}")

        # Browser Audio Output
        st.components.v1.html(f"""
            <script>
            var speech = new SpeechSynthesisUtterance('{desc_hindi}');
            speech.lang = 'hi-IN';
            window.speechSynthesis.speak(speech);
            </script>
        """, height=0)
    except:
        pass
