import streamlit as st
import os

from database.players import PlayerManager
from database.player_statistics import PlayerStatisticsManager
from database.team_results import TeamResultsManager
from database.team_stats import TeamStatsManager

from services.week_data_manager import WeekDataManager
from utils.get_data_from_excel import check_excel_players_names
from utils.streamlit_missmatched_players import identify_players


def initialize_session_state():
    keys_defaults = {
        "admin_logged": False,
        "excel_uploaded": False,
        "excel_ok": False,
        "form_ok": False,
        "file_path": None,
        "new_players_match": {},
        "week_uploaded": False,
    }

    for key, default in keys_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default


def reset_session_state():
    keys_defaults = {
        "admin_logged": False,
        "excel_uploaded": False,
        "excel_ok": False,
        "form_ok": False,
        "file_path": None,
        "new_players_match": {},
        "week_uploaded": False,
    }

    for key, default in keys_defaults.items():
        st.session_state[key] = default

    # reset managers
    st.cache_data.clear()
    st.cache_resource.clear()


@st.cache_resource
def get_managers():
    """
    Crea y cachea las instancias de las clases de base de datos.
    """
    pm = PlayerManager()
    psm = PlayerStatisticsManager()
    trm = TeamResultsManager()
    tsm = TeamStatsManager()
    return pm, psm, trm, tsm

def authenticate_admin() -> bool:
    """
    Realiza la autenticación del administrador.
    Devuelve True si la clave es correcta.
    """
    clave = st.text_input("Ingrese clave de administrador", type="password", value="")
    if clave:
        if clave == os.getenv("ADMIN_PASS"):
            st.session_state["admin_logged"] = True
            st.success("Administrador autenticado.")
            return True
        else:
            st.error("Clave de administrador incorrecta.")
            st.session_state["admin_logged"] = False
    return False


def upload_excel():
    """
    Permite al administrador cargar el archivo Excel y valida su contenido.
    """
    with st.expander("Cargar archivo Excel", expanded=True):
        st.info("Obteniendo los datos desde el Excel...")
        file_path = st.file_uploader("Subir archivo Excel", type=["xlsx"])
        if file_path:
            try:
                missing_players = check_excel_players_names(file_path, pm.excel_names)
                if missing_players:
                    identify_players(missing_players, pm)
                st.session_state["file_path"] = file_path
                st.session_state["excel_ok"] = True
                if not missing_players:
                    st.rerun()
            except Exception as e:
                st.error(f"Error al procesar el archivo Excel: {e}")


def process_week():
    """
    Procesa la carga de la semana, solicitando información adicional y actualizando datos.
    """
    st.success("Excel cargado correctamente.")
    st.subheader("Cargar datos de la semana")
    with st.form(key="upload_week"):
        col1, col2, col3 = st.columns(3)
        with col1:
            year = st.text_input("Año: ")
        with col2:
            season = st.text_input("Bimestre: ")
        with col3:
            match_week = st.text_input("Jornada: ")

        if st.form_submit_button("Subir semana"):
            if not all([year, season, match_week]):
                st.warning("Por favor, ingrese Año, Bimestre y Jornada.")
            else:
                st.session_state['form_ok'] = True
                try:
                    # Almacenar los valores en el estado de sesión
                    st.session_state["year"] = year
                    st.session_state["season"] = season
                    st.session_state["match_week"] = match_week

                    wdm = WeekDataManager(
                        year=year,
                        season=season,
                        match_week=match_week,
                        psm=psm,
                        trm=trm,
                        pm=pm,
                        tsm=tsm,
                        file=st.session_state["file_path"]
                    )
                    # Si existen selecciones de jugadores, se mapean
                    if st.session_state["new_players_match"]:
                        wdm.add_or_map_players(st.session_state["new_players_match"])
                    # --- Aquí se sube la semana ---
                    wdm.update_week()
                    st.session_state["week_uploaded"] = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al actualizar la semana: {e}")


def show_results():
    st.balloons()
    st.success("Semana subida correctamente.")
    try:
        year = st.session_state.get("year")
        season = st.session_state.get("season")
        match_week = st.session_state.get("match_week")

        df_actualizado = psm.get_week_statistics(year, season, match_week)
        st.dataframe(df_actualizado)
    except Exception as e:
        st.error(f"Error al obtener estadísticas: {e}")


# --- INICIO APP ---
initialize_session_state()
pm, psm, trm, tsm = get_managers()

# -- TITULO --
st.header("Carga de datos semanales")


st.write("""
         Aquí podrás subir el excel de la semana para que se actualicen las estadísticas de jugadores y equipos.
         """)
col1, col2 = st.columns(2)
with col1:
    st.write(
        """
        ### A tener en cuenta:
         - Si subes una semana que ya está en BD se soobrescribirá.
         - El nombre del excel es importante para recuperar la fecha, respetar el formato dfel nombre.
         - El excel debe estar guardado en xlsx.
         - El formato de los exceles actuales es el que funciona, si se cambia el formato puede que falle
         - Los nombres de los dos sheets que funcionan son Lista y Partido
        """)
with col2:
    st.write(
        """
         ### Funciones pendientes a implementar:
         - Mejorar Loging
         - Resolver Autogoles desde la web
         - Resolver Empates desde la web
         - Implementar función para modificar jugadores
         - Manejar posibles fallos
        """)


if authenticate_admin():
    if not st.session_state["excel_ok"]:
        upload_excel()
    elif not st.session_state["week_uploaded"]:
        process_week()
    else:
        show_results()
        reset_session_state()
        st.button("Cargar otra Jornada")
