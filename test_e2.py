import streamlit as st

# Estado de navegación
if 'nav' not in st.session_state:
    st.session_state.nav = None

# Mostrar contenido según navegación
if st.session_state.nav == 'inicio':
    st.write("📄 Página de Inicio")
elif st.session_state.nav == 'buscar':
    st.write("🔍 Página de Búsqueda")
elif st.session_state.nav == 'perfil':
    st.write("👤 Página de Perfil")
else:
    st.write("Selecciona una opción del menú inferior.")


# CSS: estilo barra fija horizontal tipo app móvil
st.markdown("""
    <style>
    .st-key-bottom-nav {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #f0f2f6;
        padding: 5px 0;
        box-shadow: 0 -2px 8px rgba(0,0,0,0.1);
        z-index: 9999;
        display: flex;
        justify-content: space-around;
        align-items: center;
    }
    .st-key-btn-inicio {
        background-color: transparent;
        border: none;
        color: #4CAF50;
        font-size: 24px;
        padding: 8px;
        border-radius: 50%;
        transition: background-color 0.2s;
    }
    .st-key-btn-inicio button:hover {
        background-color: #d4edd9;
    }
    </style>
""", unsafe_allow_html=True)

# Barra fija como contenedor con key
with st.container(key='bottom-nav'):
    col1, col2, col3 = st.columns(3, gap="large", vertical_alignment="center")
    with col1:
        if st.button("🏠", key="btn-inicio"):
            st.session_state.nav = 'inicio'
    with col2:
        if st.button("🔍", key="btn-buscar"):
            st.session_state.nav = 'buscar'
    with col3:
        if st.button("👤", key="btn-perfil"):
            st.session_state.nav = 'perfil'
