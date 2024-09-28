import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import paho.mqtt.client as paho
import json

# Adding custom CSS for background, fonts, and button animation
st.markdown(
    """
    <style>
    /* Custom background color */
    .stApp {
        background-color: black;
    }

    /* Header styling */
    .header-title {
        color: #f39c12;
        font-size: 48px;
        font-weight: bold;
        text-align: center;
        font-family: 'Comic Sans MS', cursive;
    }

    .header-subtitle {
        color: #3498db;
        font-size: 24px;
        text-align: center;
        margin-bottom: 20px;
    }

    /* Enlarged and blue Start button with pulsing animation */
    .pulse-button {
        animation: pulse 1.5s infinite;
        background-color: #3498db;
        border: none;
        color: white;
        padding: 20px 40px;  /* Increased padding for a bigger button */
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 20px;  /* Larger font size */
        margin: 10px 2px;
        cursor: pointer;
        border-radius: 8px;
        box-shadow: 0px 4px 6px #00000040;
    }

    @keyframes pulse {
        0% {
            transform: scale(1);
            box-shadow: 0 0 0 0 rgba(52, 152, 219, 0.7);
        }
        70% {
            transform: scale(1.1);
            box-shadow: 0 0 20px 20px rgba(52, 152, 219, 0);
        }
        100% {
            transform: scale(1);
            box-shadow: 0 0 0 0 rgba(52, 152, 219, 0);
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Displaying header with custom styling
st.markdown('<div class="header-title">Multimodal Interfaces</div>', unsafe_allow_html=True)
st.markdown('<div class="header-subtitle">Voice Control</div>', unsafe_allow_html=True)

# Displaying an image
try:
    image = Image.open('voice_ctrl.jpg')
    st.image(image, width=300)
except FileNotFoundError:
    st.error("Image file 'voice_ctrl.jpg' not found. Please check the file path.")

st.write("Tap the button and speak:")

# Wrap the blue Start button in a div and apply the 'pulse-button' CSS class
st.markdown(
    """
    <div style="display: flex; justify-content: center;">
        <button class="pulse-button" onclick="startRecognition()">Start</button>
    </div>
    <script>
    function startRecognition() {
        var recognition = new webkitSpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
 
        recognition.onresult = function (e) {
            var value = "";
            for (var i = e.resultIndex; i < e.results.length; ++i) {
                if (e.results[i].isFinal) {
                    value += e.results[i][0].transcript;
                }
            }
            if (value != "") {
                const event = new CustomEvent("GET_TEXT", {detail: value});
                document.dispatchEvent(event);
            }
        }
        recognition.start();
    }
    </script>
    """,
    unsafe_allow_html=True
)

result = streamlit_bokeh_events(
    Button(label="", width=0),  # Removed the old "Start" button
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

# Display the recognized text with more flair
if result and "GET_TEXT" in result:
    recognized_text = result.get("GET_TEXT").strip()
    st.markdown(
        f'<div style="text-align:center; color:#2ecc71; font-size:24px; border: 2px solid #2ecc71; border-radius: 5px; padding: 10px; margin: 20px;">'
        f'<b>Recognized Text:</b> "{recognized_text}"</div>',
        unsafe_allow_html=True
    )

    # MQTT setup
    broker = "broker.mqttdashboard.com"
    port = 1883
    client1 = paho.Client("GIT-HUB")
    client1.on_message = on_message
    client1.on_publish = on_publish
    client1.connect(broker, port)
    
    message = json.dumps({"Act1": recognized_text})
    ret = client1.publish("voice_ctrl", message)

# Ensure 'temp' directory exists
os.makedirs("temp", exist_ok=True)

