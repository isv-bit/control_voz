import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob
import paho.mqtt.client as paho
import json
from gtts import gTTS
from googletrans import Translator

# =====================================================
# 🎨 ESTILOS (COLORES + TIPOGRAFÍA)
# =====================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

html, body, [class*="css"]  {
    font-family: 'Poppins', sans-serif;
}

/* TÍTULO */
h1 {
    color: #38bdf8 !important;  /* azul claro */
    text-align: center;
}

/* SUBTÍTULOS */
h2, h3 {
    color: #ff4da6 !important;  /* magenta */
}

/* TEXTO */
p, span, label {
    color: #7dd3fc !important;
}

/* FONDO */
.stApp {
    background: linear-gradient(135deg, #0f172a, #1e293b);
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# MQTT
# =====================================================
def on_publish(client,userdata,result):
    print("el dato ha sido publicado \n")

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received=str(message.payload.decode("utf-8"))
    st.write("🎤 Resultado:", message_received)

broker="broker.mqttdashboard.com"
port=1883
client1= paho.Client("GIT-HUBC")
client1.on_message = on_message

# =====================================================
# UI
# =====================================================
st.title("🎤 INTERFACES MULTIMODALES")
st.subheader("🎙️ CONTROL POR VOZ")

image = Image.open('voice_ctrl.jpg')
st.image(image, width=200)

st.write("🎤 Toca el botón y habla")

# =====================================================
# BOTÓN DE VOZ (NO TOCADO)
# =====================================================
stt_button = Button(label="🎤 Iniciar", width=200)

stt_button.js_on_event("button_click", CustomJS(code="""
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
        if ( value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
"""))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

# =====================================================
# RESULTADO
# =====================================================
if result:
    if "GET_TEXT" in result:
        texto = result.get("GET_TEXT")
        st.write("🗣️ Dijiste:", texto)

        client1.on_publish = on_publish                            
        client1.connect(broker,port)  
        message = json.dumps({"Act1": texto.strip()})
        client1.publish("voice_ctrl_isa", message)

    try:
        os.mkdir("temp")
    except:
        pass
