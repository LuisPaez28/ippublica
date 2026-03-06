import streamlit as st
import requests
import ipaddress

st.set_page_config(page_title="Mi IP y Red", page_icon="🌐")

st.title("🌐 Analizador de IP Pública y Red")
st.write("Esta aplicación verifica tu verdadera IP leyendo las cabeceras HTTP de tu conexión.")

def obtener_ip_cliente():
    """Extrae la IP real del usuario leyendo los headers HTTP del servidor"""
    try:
        # st.context.headers nos permite leer las cabeceras que envió el navegador
        headers = st.context.headers
        
        # En entornos cloud, la IP original viene en 'X-Forwarded-For'
        ip_proxy = headers.get("X-Forwarded-For")
        
        if ip_proxy:
            # Si pasaste por varios proxies, vienen separados por coma. Tomamos el primero.
            ip_real = ip_proxy.split(',')[0].strip()
            return ip_real
            
    except AttributeError:
        # Por si estás usando una versión muy antigua de Streamlit
        st.warning("Tu versión de Streamlit no soporta lectura de cabeceras. Actualiza a >=1.37.0")
        return None
        
    return None

@st.cache_data(ttl=60)
def obtener_datos_red(ip_objetivo=""):
    try:
        # Si tenemos la IP del cliente, se la pasamos a la API. 
        # Si está vacío (ej. corriendo en local), la API tomará la del que hace la petición.
        url = f'http://ip-api.com/json/{ip_objetivo}' if ip_objetivo else 'http://ip-api.com/json/'
        
        respuesta = requests.get(url)
        respuesta.raise_for_status()
        return respuesta.json()
    except requests.RequestException as e:
        return {"error": str(e)}

if st.button("Verificar mi red ahora"):
    with st.spinner('Analizando cabeceras y conexión...'):
        
        # 1. Obtenemos tu IP desde el encabezado HTTP
        ip_usuario = obtener_ip_cliente()
        
        # 2. Consultamos la API enviándole explícitamente tu IP
        datos = obtener_datos_red(ip_usuario if ip_usuario else "")
        
        if "error" not in datos and datos.get('status') == 'success':
            ip_publica = datos['query']
            isp = datos['isp']
            ciudad = datos['city']
            
            # --- CÁLCULO DEL SEGMENTO DE RED ---
            ip_obj = ipaddress.IPv4Interface(f"{ip_publica}/24")
            segmento_red = ip_obj.network
            
            if ip_usuario:
                st.success(f"**Tu IP Pública real (detectada por el servidor) es:** {ip_publica}")
            else:
                st.info(f"**IP detectada (Modo Local/Directo):** {ip_publica}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.info(f"🏢 **Proveedor (ISP):**\n\n{isp}")
                st.info(f"📍 **Ubicación:**\n\n{ciudad}")
                
            with col2:
                st.warning(f"🗺️ **Segmento de Red (Subnet /24):**\n\n{segmento_red}")
                st.warning(f"🔢 **Rango de IPs de tu segmento:**\n\n{segmento_red[1]} - {segmento_red[-2]}")
                
        else:
            st.error("Hubo un problema al conectar con el servicio de verificación.")