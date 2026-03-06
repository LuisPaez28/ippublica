import streamlit as st
import requests
import ipaddress

st.set_page_config(page_title="Diagnóstico de Red", page_icon="🔧")
st.title("🔧 Modo Diagnóstico Extremo")
st.error("Vamos a descubrir exactamente dónde está escondiendo el servidor tu IP.")

# 1. Volcamos TODAS las cabeceras a la pantalla
st.subheader("🕵️‍♂️ Cabeceras HTTP Crudas")
st.write("Esta es la radiografía exacta de tu conexión. Busca tu IP pública real en este diccionario:")
cabeceras = dict(st.context.headers)
st.json(cabeceras)

st.write("---")

# 2. Búsqueda por fuerza bruta en las cabeceras más comunes de la nube
st.subheader("🎯 Búsqueda automática")
def buscar_ip_fuerza_bruta():
    # Estas son las cabeceras que usan AWS, Google Cloud, Cloudflare, Heroku, etc.
    posibles_cabeceras = [
        "X-Forwarded-For", 
        "X-Real-Ip", 
        "CF-Connecting-IP", 
        "True-Client-IP",
        "Fly-Client-IP",
        "X-Client-IP"
    ]
    
    for cabecera in posibles_cabeceras:
        # Buscamos la cabecera tanto en mayúsculas como minúsculas
        ip = cabeceras.get(cabecera, cabeceras.get(cabecera.lower(), ""))
        if ip:
            st.info(f"👉 Encontrada la cabecera `{cabecera}` con el valor: **{ip}**")
            
            # Limpiamos y validamos la IP
            ip_limpia = ip.split(',')[0].strip()
            try:
                obj_ip = ipaddress.ip_address(ip_limpia)
                if not obj_ip.is_private and not obj_ip.is_loopback:
                    return ip_limpia
                else:
                    st.warning(f"⚠️ La IP {ip_limpia} es privada/local. La ignoramos.")
            except ValueError:
                pass
                
    return None

ip_real = buscar_ip_fuerza_bruta()

if ip_real:
    st.success(f"🚀 ¡ÉXITO! Tu verdadera IP pública es: {ip_real}")
    
    # Ahora sí, hacemos la consulta de red segura
    respuesta = requests.get(f'https://ipinfo.io/{ip_real}/json')
    if respuesta.status_code == 200:
        datos = respuesta.json()
        st.write(f"🏢 **Proveedor:** {datos.get('org')}")
        st.write(f"📍 **Ubicación:** {datos.get('city')}")
else:
    st.error("El servidor definitivamente está bloqueando o eliminando tu IP pública de las cabeceras.")