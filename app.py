import streamlit as st
import google.generativeai as genai
import base64
from PIL import Image
from io import BytesIO

# --- CONFIGURATION ---
# Yahan apni API Key dalein (Google AI Studio se)
API_KEY = st.secrets["API_KEY"]
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="VisionPulse AI", page_icon="👁️")

# --- UI INTERFACE ---
st.title("👁️ VisionPulse AI")
st.markdown("### Assistant active hai. Har 5 second mein auto-scan hoga.")

# Hidden input jo JavaScript se image data receive karega
# Iska id 'camera_pulse' hai jo JS code mein use hua hai
img_data = st.text_input("Camera Data", key="camera_pulse", label_visibility="collapsed")

# --- JAVASCRIPT HACK (Camera + Interval + Audio) ---
st.markdown(f"""
    <video id="video" autoplay playsinline style="width:100%; border-radius:15px; background:#000;"></video>
    <canvas id="canvas" style="display:none;"></canvas>
    
    <script>
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    
    // 1. Camera Start Karo (Mobile environment mode = Back Camera)
    navigator.mediaDevices.getUserMedia({{ video: {{ facingMode: "environment" }} }})
        .then(stream => {{ video.srcObject = stream; }})
        .catch(err => console.error("Camera Error: ", err));

    // 2. Pulse Logic: Har 5 second mein frame capture karke Streamlit ko bhejo
    setInterval(() => {{
        const context = canvas.getContext('2d');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        const imageData = canvas.toDataURL('image/jpeg');
        
        // Streamlit ka internal trigger
        window.parent.postMessage({{
            type: 'streamlit:set_widget_value',
            data: {{ value: imageData, id: 'camera_pulse' }}
        }}, '*');
    }}, 5000); // 5000ms = 5 Seconds
    </script>
""", unsafe_allow_html=True)

# --- BACKEND PROCESSING ---
if img_data and img_data.startswith("data:image"):
    try:
        # 1. Base64 Image ko Decode karke PIL Image banana
        header, encoded = img_data.split(",", 1)
        data = base64.b64decode(encoded)
        image = Image.open(BytesIO(data))

        # 2. Gemini API se description mangwana
        prompt = "Describe the scene in 1 short sentence in Hindi. If there is a danger or obstacle, warn the person. Keep it very simple for a blind person."
        response = model.generate_content([prompt, image])
        description = response.text

        # 3. Result dikhana
        st.subheader(f"📢 {description}")

        # 4. Instant Audio (Browser-based Text-to-Speech)
        tts_script = f"""
            <script>
            var msg = new SpeechSynthesisUtterance("{description}");
            msg.lang = 'hi-IN';
            window.speechSynthesis.speak(msg);
            </script>
        """
        st.components.v1.html(tts_script, height=0)

    except Exception as e:
        st.error(f"Error: {{e}}")
