import streamlit as st

st.set_page_config(
    page_title="PreBar League Page",
    page_icon="🏆<e",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --- PAGE SETUP ---
inicio_page = st.Page(
    page="views/home_page.py",
    title="Inicio",
    icon=":material/home:",
    default=True
)

estadisticas_page = st.Page(
    page="views/stats_page.py",
    title="Estadísticas",
    icon=":material/sports_soccer:"
)

actualiza_jornada_page = st.Page(
    page="views/upload_week_page.py",
    title="Subir Jornada(Admin)",
    icon=":material/publish:"
)

# --- NAVIGATION SETUP ---
pg = st.navigation(
    {
        "": [inicio_page, estadisticas_page],
        "admin": [actualiza_jornada_page]
    }
)

pg.run()


# --- SHARED ON ALL PAGES ---
st.logo("assets/logo.png", size="large")
st.sidebar.text("Hecho con ❤️ por FrEddy")
