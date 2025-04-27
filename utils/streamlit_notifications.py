import streamlit as st
import pandas as pd
from collections import Counter
from database.players import PlayerManager


@st.dialog("Resolver jugadores")
def identify_players_dialog(missmatched_players, pm: PlayerManager):
    all_players = pm.get_all_players()
    all_players_options = all_players[pm.PLAYER_NAME].to_list()
    # add nuevo_jugador at first option
    all_players_options.insert(0, "Selecciona ...")

    st.write(
        "Antes de continuar debes seleccionar quienes son estos jugadores. Si se trata de un Nuevo Jugador "
        "asegúrate de agregarlo a la lista de jugadores (no implementado aún, agregar manualmente en BD)"
        )

    with st.form('missing_players'):
        unmatched_names_dict = {}
        for player in missmatched_players:
            selected_map = st.selectbox(
                label=f"Quién es {player}?",
                options=all_players_options,
                key=f"select_{player}")

            unmatched_names_dict[player] = selected_map
            print(unmatched_names_dict)

        if st.form_submit_button("Continuar.."):
            if 'Selecciona ...' in unmatched_names_dict.values():
                st.warning('Por favor seleccione una opción para cada jugador')
                # Si todos los jugadores han sido seleccionados. Cerramos el dialogo y devolvemos resultado
            else:
                st.session_state.unmatched_names_dict = unmatched_names_dict
                st.session_state.unmatched_names_resolved = True
                st.rerun()


@st.dialog("Quién anotó el autogol")
def autogol_dialog(teams_owngoal_list, df_names):
    all_players_options = df_names['name'].to_list()
    # add nuevo_jugador at first option
    all_players_options.insert(0, "Selecciona ...")

    with st.form('autogol'):
        autogol_players = []
        for key, team in enumerate(teams_owngoal_list):
            selected_player = st.selectbox(
                label=f"Quién anotó el autogol {team}?",
                options=all_players_options,
                key=f"select_autogol_{key}")

            autogol_players += [selected_player]

        if st.form_submit_button("Continuar.."):
            if 'Selecciona ...' in autogol_players:
                st.warning('Por favor seleccione una opción para el autogol')
            else:
                conteo_nombres = Counter(autogol_players)
                st.session_state['autogol_players'] = dict(conteo_nombres)
                st.session_state["excel_ok"] = True
                st.rerun()
