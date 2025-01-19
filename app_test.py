import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

from database.player_statistics import PlayerStatisticsManager
from services.week_data_manager import WeekDataManager
from config.settings import WEEK_PATH


load_dotenv()

st.title("Fantasy del fulbol")

# Opciones de navegación
menu_opciones = [
    "Inicio",
    "Seleccionar Equipo",
    "Estadísticas",
    "Ranking",
    "Carga de Semana (Admin)"
]
menu = st.sidebar.selectbox("Menú", menu_opciones)

if menu == "Inicio":
    st.subheader("¡Bienvenido!")
    st.write("""
    Esta aplicación te permite participar en un Fantasy personal.
    Selecciona un equipo, compite por ser el mejor y revisa las estadísticas.
    Usa el menú de la izquierda para navegar.
    """)

elif menu == "Seleccionar Equipo":
    jugadores = [
        {"Nombre": "Jugador1", "Precio": 10, "Media Fantasy": 8.2},
        {"Nombre": "Jugador2", "Precio": 12, "Media Fantasy": 7.9},
        {"Nombre": "Jugador3", "Precio": 8, "Media Fantasy": 7.5},
        {"Nombre": "Jugador4", "Precio": 9, "Media Fantasy": 6.8},
        {"Nombre": "Jugador5", "Precio": 11, "Media Fantasy": 8.0},
        {"Nombre": "Jugador6", "Precio": 5, "Media Fantasy": 5.5},
        {"Nombre": "Jugador7", "Precio": 15, "Media Fantasy": 9.0},
        {"Nombre": "Jugador8", "Precio": 6, "Media Fantasy": 6.2},
    ]
    df_jugadores = pd.DataFrame(jugadores).sort_values("Media Fantasy", ascending=False)
    presupuesto = 77  # Presupuesto de ejemplo

    st.subheader("Jugadores disponibles")
    st.dataframe(df_jugadores)

    st.subheader("Selecciona tu equipo")
    seleccionados = st.multiselect("Jugadores", df_jugadores["Nombre"])

    costo_total = df_jugadores[df_jugadores["Nombre"].isin(seleccionados)]["Precio"].sum()
    st.write(f"Presupuesto utilizado: {costo_total} / {presupuesto}")

    if len(seleccionados) == 7 and costo_total <= presupuesto:
        st.success("¡Equipo válido!")
    elif len(seleccionados) != 7:
        st.error("Debes seleccionar exactamente 7 jugadores.")
    elif costo_total > presupuesto:
        st.error("Has excedido el presupuesto disponible.")

elif menu == "Estadísticas":
    st.header("Estadísticas Generales")
    gestor = PlayerStatisticsManager()
    df_gen = gestor.get_general_statistics()
    st.dataframe(df_gen)

elif menu == "Ranking":
    st.header("Ranking de Participantes")
    # Aquí se mostraría el ranking

elif menu == "Carga de Semana (Admin)":
    st.header("Carga de datos semanales")
    wdm = WeekDataManager(file_path=WEEK_PATH, year=2025, season=1, match_week=1)
    psm = PlayerStatisticsManager()

    if "admin_logged" not in st.session_state:
        st.session_state["admin_logged"] = False

    if not st.session_state["admin_logged"]:
        clave_admin = st.text_input("Ingrese clave de administrador", type="password", value="")
        if clave_admin:
            if clave_admin == os.getenv("ADMIN_PASS"):
                st.session_state["admin_logged"] = True
                st.write("Obteniendo los datos desde el excel y la APP ...")
                try:
                    # Simulación de carga de datos
                    wdm.upload_week()
                    st.success("Datos de la semana cargados correctamente.")
                    df_actualizado = psm.get_general_statistics()
                    st.dataframe(df_actualizado)
                except Exception as e:
                    st.error(f"Ocurrió un error al procesar la carga: {e}")
            else:
                st.error("Clave de administrador incorrecta.")
                st.session_state["admin_logged"] = False
    else:
        st.write("Bienvenido, administrador.")