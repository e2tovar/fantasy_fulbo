import streamlit as st
import os

from database.players import PlayerManager
from database.player_statistics import PlayerStatisticsManager
from database.team_results import TeamResultsManager
from database.team_stats import TeamStatsManager


from services.week_data_manager import WeekDataManager

from utils.get_data_from_excel import check_excel_players_names
from utils.streamlit_missmatched_players import identify_players

st.header("Carga de datos semanales")

# ---Create states for every databases classes---
if "PlayerManager" not in st.session_state:
    st.session_state["PlayerManager"] = PlayerManager()
pm = st.session_state["PlayerManager"]

if "PlayerStatisticsManager" not in st.session_state:
    st.session_state["PlayerStatisticsManager"] = PlayerStatisticsManager()
psm = st.session_state["PlayerStatisticsManager"]

if "TeamResultsManager" not in st.session_state:
    st.session_state["TeamResultsManager"] = TeamResultsManager()
trm = st.session_state["TeamResultsManager"]

if "TeamStatsManager" not in st.session_state:
    st.session_state["TeamStatsManager"] = TeamStatsManager()
tsm = st.session_state["TeamStatsManager"]


if "admin_logged" not in st.session_state:
    st.session_state["admin_logged"] = False
if "week_uploaded" not in st.session_state:
    st.session_state["week_uploaded"] = False
if "missmatched_players" not in st.session_state:
    st.session_state["missmatched_players"] = []
if "excel_uploaded" not in st.session_state:
    st.session_state["excel_uploaded"] = False
if "excel_ok" not in st.session_state:
    st.session_state["excel_ok"] = False
if "uploaded_file" not in st.session_state:
    st.session_state["uploaded_file"] = None


def uploaded_excel():
    st.session_state["excel_uploaded"] = True


clave_admin = st.text_input("Ingrese clave de administrador", type="password", value="")
uploaded_file = None

if clave_admin:
    if clave_admin == os.getenv("ADMIN_PASS"):
        # --- UPLOAD EXCEL ---
        if not st.session_state.excel_ok:
            st.write("Obteniendo los datos desde el excel ...")
            uploaded_file = st.file_uploader(
                "Subir archivo Excel",
                type=["xlsx"],
                on_change=uploaded_excel())
            if uploaded_file:
                missing_players = check_excel_players_names(uploaded_file, pm.excel_names)
                if len(missing_players) > 0:
                    identify_players(missing_players, pm)
                st.session_state.uploaded_file = uploaded_file
                st.session_state.excel_ok = True
        else:
            st.success("Excel cargado correcatmente")
            with st.form(key="upload_week"):
                # Option to upload an Excel file
                # Selecciona Año, Bimestre y Jornada
                year = st.text_input("Año: ")
                season = st.text_input("Bimestre: ")
                match_week = st.text_input("Jornada: ")
                if st.form_submit_button("Subir semana"):
                    if not all([year, season, match_week]):
                        st.warning("Por favor, ingrese Año, Bimestre y Jornada.")
                    else:
                        wdm = WeekDataManager(
                            year=year, season=season, match_week=match_week,
                            psm=psm, trm=trm, pm=pm, tsm=tsm,
                            file=st.session_state.uploaded_file,
                            )
                        if len(st.session_state.player_selections) > 0:
                            wdm.add_or_map_players(st.session_state.player_selections)
                        missing_players = wdm.update_week()
                        if len(missing_players) > 0:
                            st.session_state["missmatched_players"] = missing_players
                        else:
                            st.session_state["week_uploaded"] = True
    else:
        st.error("Clave de administrador incorrecta.")
        st.session_state["admin_logged"] = False


if st.session_state["week_uploaded"]:
    st.balloons()
    st.success("Se subió la semana correctamente")
    df_actualizado = psm.get_week_statistics(year, season, match_week)
    st.dataframe(df_actualizado)
