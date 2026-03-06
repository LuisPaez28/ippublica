import streamlit as st
import requests
import ipaddress

# Configuración de la página
st.set_page_config(page_title="Mi IP y Red", page_icon="🌐")

st.title("🌐 Analizador de IP Pública y Red")
st.write("Esta aplicación web verifica la IP con la que sales a Internet y calcula tu segmento.")

@st.cache_data(ttl=60) # Usamos caché para no saturar la API si recargas la página rápido
def obtener_datos_red():
    try:
        # Usamos una API gratuita que nos da IP y detalles de red sin necesidad de registrarse
        respuesta = requests.get('http://ip-api.com/json/')
        respuesta.raise_for_status()
        return respuesta.json()
    except requests.RequestException as e:
        return {"error": str(e)}

if st.button("Verificar mi red ahora"):
    with st.spinner('Analizando conexión...'):
        datos = obtener_datos_red()
        
        if "error" not in datos and datos.get('status') == 'success':
            ip_publica = datos['query']
            isp = datos['isp']
            ciudad = datos['city']
            
            # --- CÁLCULO DEL SEGMENTO DE RED ---
            # En redes públicas de Internet, los ISPs anuncian bloques (segmentos). 
            # Aquí calculamos dinámicamente el segmento /24 (Clase C), que es la agrupación lógica más común.
            ip_obj = ipaddress.IPv4Interface(f"{ip_publica}/24")
            segmento_red = ip_obj.network
            
            # Mostramos los resultados en la interfaz de Streamlit
            st.success(f"**Tu IP Pública actual es:** {ip_publica}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.info(f"🏢 **Proveedor (ISP):**\n\n{isp}")
                st.info(f"📍 **Ubicación:**\n\n{ciudad}")
                
            with col2:
                # Mostramos la información técnica de la red
                st.warning(f"🗺️ **Segmento de Red (Subnet /24):**\n\n{segmento_red}")
                st.warning(f"🔢 **Rango de IPs de tu segmento:**\n\n{segmento_red[1]} - {segmento_red[-2]}")
                
            st.write("---")
            st.write("💡 *Nota técnica: El segmento mostrado asume una máscara de subred de 24 bits (255.255.255.0). Los proveedores de internet (ISP) administran las redes en bloques más grandes (Autonomous Systems), pero a nivel de tu nodo geográfico, perteneces a este bloque.*")
            
        else:
            st.error("Hubo un problema al conectar con el servicio de verificación.")