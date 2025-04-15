import streamlit as st
from database.player_statistics import PlayerStatisticsManager
from st_aggrid import AgGrid, GridOptionsBuilder

# Cacheamos la instancia del PlayerStatisticsManager para evitar recrearla en cada rerun
@st.cache_resource
def get_psm():
    return PlayerStatisticsManager()

psm = get_psm()


@st.cache_resource
def get_aggregations():
    # Obtener la lista de años
    años = psm.get_years()

    # Crear un diccionario para almacenar las asociaciones
    aggregations = {}
    for year in años:
        bimestres = psm.get_bimestres(year)
        weeks_dict = {}
        for bimestre in bimestres:
            weeks_dict[bimestre] = psm.get_weeks(year, bimestre)
        aggregations[year] = {
            "bimestres": bimestres,
            "weeks": weeks_dict
        }

    return aggregations


# Obtenemos la información precargada (cacheada)
aggregations = get_aggregations()

st.header("Estadísticas Generales")
st.markdown(
    """
        Ajusta los filtros para visualizar las estadísticas basadas en los datos asociados.
        Agregaremos ChatGPT en el futuro para que haga queries
        Notas:
        - En el año 2023 no contábamos los bimestres
    """
    )

# Selector para el nivel de agregación usando un radio button
nivel_agregacion = st.radio("Seleccione el nivel de agregación:", options=["Año", "Bimestre", "Semana"], index=1)

# El selector de año se basa en las claves del diccionario precargado
años = sorted(list(aggregations.keys()), reverse=True)
año = st.selectbox("Seleccione el Año:", options=años)

# Selector de bimestre: se muestra si el nivel de agregación es "Bimestre" o "Semana"
if nivel_agregacion in ["Bimestre", "Semana"]:
    bimestres = sorted(aggregations[año]["bimestres"], reverse=True)
    bimestre = st.selectbox("Seleccione el Bimestre:", options=bimestres)
else:
    bimestre = None

# Selector de semana: solo se muestra si el nivel de agregación es "Semana"
if nivel_agregacion == "Semana":
    # Obtenemos las semanas disponibles para el año y bimestre seleccionados.
    weeks_options = sorted(aggregations[año]["weeks"].get(bimestre, []), reverse=True)
    semana = st.selectbox("Seleccione la Semana:", options=weeks_options)
else:
    semana = None

# Botón para cargar la consulta y mostrar la tabla de estadísticas
if st.button("Mostrar estadísticas"):
    try:
        # Se asume que get_statistics acepta los parámetros de forma opcional según el nivel de agregación
        df = psm.fetch_general_statistics(year=año, season=bimestre, match_week=semana)
        if df.empty:
            st.info("No se encontraron datos con los filtros seleccionados.")
        else:
            # Configurar las opciones de la grilla
            gb = GridOptionsBuilder.from_dataframe(df)
            gb.configure_pagination(paginationAutoPageSize=True)  # Habilita la paginación automática
            gb.configure_side_bar()  # Muestra el panel lateral con opciones de filtros y columnas
            gb.configure_default_column(filter=True, sortable=True, editable=False)  # Configura filtro y ordenamiento
            gridOptions = gb.build()

            # Mostrar la tabla interactiva con AgGrid
            AgGrid(df, gridOptions=gridOptions, enable_enterprise_modules=False, update_mode="MODEL_CHANGED")

    except Exception as e:
        st.error(f"Ocurrió un error al obtener las estadísticas: {e}")