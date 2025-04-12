import streamlit as st
import pandas as pd
from database.player_statistics import PlayerStatisticsManager

# Configuración inicial
st.title("Fantasy del fulbol")


# Opciones de navegación
menu = st.sidebar.selectbox(
    "Menú",
    ["Inicio", "Seleccionar Equipo", "Estadísticas", "Ranking"])

if menu == "Inicio":
    st.subheader("¡Bienvenido!")
    st.write("""
    Esta aplicación te permite participar en un Fantasy personal con tus amigos.
    Selecciona un equipo de jugadores, compite por ser el mejor y observa las estadísticas en tiempo real.
    Usa el menú de la izquierda para navegar por las secciones.
    """)

elif menu == "Seleccionar Equipo":
    # Cargar datos de jugadores
    jugadores_df = pd.DataFrame(jugadores)
    jugadores_df.sort_values("Media Fantasy", inplace=True, ascending=False)
    presupuesto = 77  # Presupuesto ficticio para prueba

    # Mostrar tabla de jugadores
    st.subheader("Jugadores disponibles")
    st.dataframe(jugadores_df)

    # Seleccionar jugadores
    st.subheader("Selecciona tu equipo")
    seleccionados = st.multiselect("Jugadores", jugadores_df["Nombre"])

    # Calcular costo total
    costo_total = sum(jugadores_df[jugadores_df["Nombre"].isin(seleccionados)]["Precio"])
    st.write(f"Presupuesto utilizado: {costo_total} / {presupuesto}")

    # Validar selección
    if len(seleccionados) == 7 and costo_total <= presupuesto:
        st.success("¡Equipo válido!")
    elif len(seleccionados) != 7:
        st.error("Debes seleccionar exactamente 7 jugadores.")
    elif costo_total > presupuesto:
        st.error("Has excedido el presupuesto disponible.")

elif menu == "Estadísticas":
    st.header("Estadísticas Generales")
    weekm = PlayerStatisticsManager()
    gen_df = weekm.get_general_statistics()
    st.dataframe(gen_df)
    # Crear un control para seleccionar la página

elif menu == "Ranking":
    st.header("Ranking de Participantes")
    # Mostrar ranking