import streamlit as st
import streamlit.components.v1 as components
import socket

st.set_page_config(page_title="Mi verdadera IP", page_icon="🌐")
st.title("Ip")

# Obtenemos la IP local real de la computadora/servidor donde está corriendo la app
nombre_host = socket.gethostname()
try:
    ip_local_maquina = socket.gethostbyname(nombre_host)
except Exception:
    ip_local_maquina = "No detectada"

# Obtenemos lo que las cabeceras HTTP le dicen a Python
ip_cabeceras = st.context.headers.get("X-Forwarded-For", "Conexión Directa (Sin Proxy)")

col1, col2 = st.columns(2)
with col1:
    st.info(f"🖥️ **IP Local de la Máquina (Servidor):**\n\n`{ip_local_maquina}`\n\n*(IP tarjeta de red de la computadora).*")
with col2:
    st.info(f"🕵️ **IP Detectada por la Nube (Cabeceras):**\n\n`{ip_cabeceras}`\n\n*(IP que el balanceador de carga reporta).*")

st.write("---")
# --- PARTE 2: TU IP PÚBLICA Y SEGMENTO (Frontend / JavaScript) ---
st.subheader("Ip Publica")

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
components.html(codigo_html_js, height=260)

st.write("---")
st.info("by Luis Páez")