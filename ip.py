import streamlit as st
import requests
import ipaddress

st.set_page_config(page_title="Mi IP y Red", page_icon="🌐")
st.title("🌐 Analizador de IP Pública y Red")

def obtener_ip_cliente():
    """Extrae la IP leyendo los headers HTTP, pero filtra las IPs locales/privadas"""
    try:
        headers = st.context.headers
        ip_proxy = headers.get("X-Forwarded-For", "")
        
        if ip_proxy:
            # Separamos todas las IPs que vengan en el encabezado
            lista_ips = [ip.strip() for ip in ip_proxy.split(',')]
            
            for ip in lista_ips:
                try:
                    # Convertimos el texto a un objeto IP para analizarlo
                    obj_ip = ipaddress.ip_address(ip)
                    
                    # Si la IP NO es privada (192.168.x.x, 10.x.x.x, etc.) ni loopback (127.0.0.1)
                    if not obj_ip.is_private and not obj_ip.is_loopback:
                        return ip  # ¡Encontramos la IP pública real!
                except ValueError:
                    continue # Si no es una IP válida, la ignoramos y pasamos a la siguiente
                    
    except AttributeError:
        pass
        
    return None

@st.cache_data(ttl=60)
def obtener_datos_red(ip_objetivo=""):
    try:
        # Usamos ipinfo.io, que soporta HTTPS de forma gratuita
        url = f'https://ipinfo.io/{ip_objetivo}/json' if ip_objetivo else 'https://ipinfo.io/json'
        
        respuesta = requests.get(url, timeout=5)
        respuesta.raise_for_status()
        return respuesta.json()
    except requests.RequestException as e:
        return {"error": str(e)}

if st.button("Verificar mi red ahora"):
    with st.spinner('Analizando cabeceras y conexión...'):
        
        ip_usuario = obtener_ip_cliente()
        
        # --- PRÁCTICA SENIOR: MODO DEBUG ---
        # Esto nos permite ver qué IP estamos extrayendo realmente antes de enviarla a la API
        st.write(f"🔍 *Debug - IP extraída de las cabeceras:* `{ip_usuario}`")
        
        datos = obtener_datos_red(ip_usuario if ip_usuario else "")
        
        # ipinfo.io devuelve la IP en el campo "ip"
        if "error" not in datos and "ip" in datos:
            ip_publica = datos.get('ip')
            isp = datos.get('org', 'Proveedor Desconocido')
            ciudad = datos.get('city', 'Ciudad Desconocida')
            
            # Protegemos el cálculo por si detecta una IPv6 (que no se puede calcular como /24 directamente)
            try:
                ip_obj = ipaddress.IPv4Interface(f"{ip_publica}/24")
                segmento_red = str(ip_obj.network)
                rango_ips = f"{ip_obj.network[1]} - {ip_obj.network[-2]}"
            except ValueError:
                segmento_red = "Red IPv6 detectada"
                rango_ips = "No aplicable para IPv4"
            
            st.success(f"**Tu IP Pública detectada es:** {ip_publica}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.info(f"🏢 **Proveedor (ISP/ASN):**\n\n{isp}")
                st.info(f"📍 **Ubicación:**\n\n{ciudad}")
                
            with col2:
                st.warning(f"🗺️ **Segmento de Red:**\n\n{segmento_red}")
                st.warning(f"🔢 **Rango de IPs:**\n\n{rango_ips}")
                
        else:
            st.error("Hubo un problema al conectar con el servicio de verificación.")
            # --- PRÁCTICA SENIOR: MOSTRAR EL ERROR REAL ---
            st.error("Detalle técnico del error para depuración:")
            st.json(datos)