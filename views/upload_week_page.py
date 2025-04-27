import streamlit as st
import os
from datetime import datetime as dt

from database.players import PlayerManager
from database.player_statistics import PlayerStatisticsManager
from database.team_results import TeamResultsManager
from database.team_stats import TeamStatsManager

from services.excel_manager import ExcelManager
from services.week_data_manager import WeekDataManager
from utils.streamlit_notifications import identify_players_dialog, autogol_dialog
from utils.vars import meses_a_bimentre
from utils.utils_functions import contar_sabados_en_bimestre


def initialize_session_state():
    keys_defaults = {
        "admin_logged": False,
        "excel_uploaded": False,
        "excel_ok": False,
        "form_ok": False,
        "file_path": None,
        "unmatched_names_resolved": {},
        "autogol_players": {},
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
        "autogol_players": {},
        "week_uploaded": False,
    }

    for key, default in keys_defaults.items():
        st.session_state[key] = default

    # reset managers
    st.cache_data.clear()
    st.cache_resource.clear()


@st.cache_resource
def get_data_managers() -> tuple[PlayerManager, PlayerStatisticsManager, TeamResultsManager, TeamStatsManager, ExcelManager]:
    """
    Crea y cachea las instancias de las clases de base de datos.
    """
    plm = PlayerManager()
    psm = PlayerStatisticsManager()
    trm = TeamResultsManager()
    tsm = TeamStatsManager()
    exm = ExcelManager()
    return plm, psm, trm, tsm, exm


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
        excel_file = st.file_uploader("Subir archivo Excel", type=["xlsx"], on_change=set_uploaded_state())
        if excel_file:  # Cuando se sube con streamlit
            exm.read_excel(excel_file)

    if exm.excel_file:  # el excel se queda cacheado en clase
        try:
            excel_names_db = plm.excel_names

            # Mapea todos los nombres
            missing_players = exm.check_missing_excel_players_names(excel_names_db)

            if missing_players and not st.session_state.unmatched_names_resolved:
                identify_players_dialog(missing_players, plm)
            else:
                st.session_state.unmatched_names_resolved = True

                # Resolvemos autogoles
                team_own_goal_list = exm.check_teams_own_goals()
                if team_own_goal_list:
                    autogol_dialog(team_own_goal_list, exm.df_week_names)

            if not missing_players and not team_own_goal_list:
                st.rerun()
        except Exception as e:
            st.error(f"Error al procesar el archivo Excel: {e}")


def process_week():
    """
    Procesa la carga de la semana, solicitando información adicional y actualizando datos.
    """
    st.success(f"Excel cargado correctamente: {exm.excel_file.name}")
    st.subheader("Cargar datos de la semana")
    with st.form(key="date"):
        anio_col, mes_col, dia_col = st.columns(3)
        with anio_col:
            today_year = dt.now().year
            match_year = st.text_input("Año: ", today_year)
        with mes_col:
            today_month = dt.now().month
            match_month = st.selectbox("Mes: ", [i for i in range(1, 13)], today_month-1)
        with dia_col:
            today_day = dt.now().day
            match_day = st.selectbox("Día: ", [i for i in range(1, 32)], today_day-1)

        bimestre_col, jornada_col = st.columns(2)
        with bimestre_col:
            pre_sel_bimestre = meses_a_bimentre.get(match_month, 0)
            season = st.selectbox("Bimestre: ", [i for i in range(1, 7)], pre_sel_bimestre-1)
        with jornada_col:
            # Get the last saturday index of the month. Example, it is july 20 has passed 3 saturday in july 2025. So
            match_week = st.selectbox("Jornada: ", [i for i in range(1, 11)], contar_sabados_en_bimestre(season)-1)

        if st.form_submit_button("Subir semana"):
            if not all([match_year, match_week, match_day, match_month]):
                st.warning("Por favor, ingrese datos de jornada.")
            else:
                st.session_state['form_ok'] = True
                try:
                    # Almacenar los valores en el estado de sesión
                    st.session_state["year"] = match_year
                    st.session_state["season"] = season
                    st.session_state["match_week"] = match_week

                    wdm = WeekDataManager(
                        year=match_year,
                        season=season,
                        match_week=match_week,
                        match_date=f"{str(match_day).zfill(2)}/{str(match_month).zfill(2)}/{match_year}",
                        psm=psm,
                        trm=trm,
                        pm=plm,
                        tsm=tsm,
                        file=exm.excel_file,
                        autogol_players=st.session_state["autogol_players"]
                    )
                    # Si existen selecciones de jugadores, se mapean
                    wdm.excel_names_map = st.session_state.unmatched_names_dict if st.session_state.unmatched_names_dict else {}
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


def set_uploaded_state():
    st.session_state.excel_uploaded = True


# --- INICIO APP ---
initialize_session_state()
plm, psm, trm, tsm, exm = get_data_managers()

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
         - Si subes una semana que ya está en BD se sobrescribirá.
         - El nombre del excel es importante para recuperar la fecha, respetar el formato del nombre. (22-febrero.xlsx)
         - El excel debe estar guardado en xlsx.
         - El formato de los exceles actuales es el que funciona, si se cambia el formato puede que falle.
         - Los nombres de los dos sheets que funcionan son Lista y Partido
        """)
with col2:
    st.write(
        """
         ### Funciones pendientes a implementar:
         - Mejorar Logging
         - Resolver Autogoles desde la web
         - Resolver Empates desde la web
         - Posibilidad de agregar MVP y mejor GOL manualmente desde el BAR (antes el MVP era por la app pero se elimina)
         - Implementar función para modificar jugadores.
         - Leer los excels directamente de la web.
        """)

st.markdown('---')

if authenticate_admin():
    if not st.session_state["excel_ok"]:
        upload_excel()
    elif not st.session_state["week_uploaded"]:
        process_week()
    else:
        show_results()
        reset_session_state()
        st.button("Cargar otra Jornada")
