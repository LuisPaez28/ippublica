import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Mi verdadera IP", page_icon="🌐")

st.title("🌐 Analizador de Red (Modo Frontend)")
st.write("Dado que el servidor en la nube bloquea las cabeceras, vamos a obligar a tu propio navegador a que busque y muestre tu IP pública.")

# Escribimos un pequeño componente en HTML y JavaScript
# Este código NO se ejecuta en el servidor (Backend), se ejecuta en tu computadora (Frontend)
codigo_html_js = """
<div style="font-family: sans-serif; padding: 20px; border-radius: 10px; background-color: #f0f2f6; border: 1px solid #d1d5db;">
    <h3 style="margin-top:0; color: #31333F;">Tu verdadera IP Pública es:</h3>
    <h1 id="ip-text" style="color: #ff4b4b;">Buscando... 🔍</h1>
    <p id="isp-text" style="font-weight: bold; color: #31333F;"></p>
    <p id="geo-text" style="color: #31333F;"></p>
</div>

<script>
    // Tu navegador hace la petición a ipinfo.io directamente, esquivando a la nube
    fetch('https://ipinfo.io/json')
        .then(response => response.json())
        .then(data => {
            // Actualizamos el HTML con los datos reales
            document.getElementById('ip-text').innerText = data.ip;
            document.getElementById('isp-text').innerText = '🏢 Proveedor: ' + data.org;
            document.getElementById('geo-text').innerText = '📍 Ubicación: ' + data.city + ', ' + data.region;
        })
        .catch(error => {
            document.getElementById('ip-text').innerText = 'Error al obtener IP';
            console.error('Error:', error);
        });
</script>
"""

# Renderizamos el componente de HTML/JS dentro de Streamlit
components.html(codigo_html_js, height=250)

st.write("---")
st.info("💡 **¿Por qué esto sí funciona?** Porque usamos JavaScript. La petición viaja de tu computadora B directo a `ipinfo.io`. El servidor en la nube ya no interviene para nada en la lectura de la IP.")