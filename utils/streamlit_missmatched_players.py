import streamlit as st
from database.players import PlayerManager

@st.dialog("Resolver jugadores")
def identify_players(missmatched_players, pm: PlayerManager):
    all_players = pm.get_all_players()
    all_players_options = all_players[pm.PLAYER_NAME].to_list()
    # add nuevo_jugador at first option
    all_players_options.insert(0, "Nuevo jugador")
    all_players_options.insert(0, "Selecciona ...")

    st.write("Antes de continuar debes seleccionar quienes son estos jugadores")

    with st.form('missing_players'):
        for player in missmatched_players:
            position_selector = ''
            selected_maps = st.selectbox(
                label=f"Quién es {player}?",
                options=all_players_options,
                key=f"select_{player}")

            if selected_maps == 'Nuevo jugador':
                position_selector = st.selectbox(
                    label=f"Posición de {player}?",
                    options=['Selecciona posición', 'Defensa', 'Mediocampista', 'Delantero'],
                    key=f"position_{player}")

            st.session_state.new_players_match[player] = ('-new-' + position_selector) if position_selector else selected_maps

        if st.form_submit_button("Continuar.."):
            map_missplayers = {}
            for player, selection in st.session_state.new_players_match.items():
                map_missplayers[player] = selection
                if selection == 'Selecciona ...':
                    st.warning('Por favor seleccione una opción para cada jugador')
                    break
                if position_selector == 'Selecciona posición':
                    st.warning('Debes seleccionar las posiciones de los nuevos jugadores')
                    break
                # Si todos los jugadores han sido seleccionados. Cerramos el dialogo y devolvemos resultado
            else:
                st.session_state["excel_ok"] = True
                st.session_state['map_missplayers'] = map_missplayers
                st.rerun()


def add_or_map_players(pm: PlayerManager):
    for excel_name, name in st.session_state['map_missplayers'].items():
        if '-new-' in name:
            field_pos = name.split('-new-')[1]
            pm.add_player(excel_name, excel_name, field_pos)
        else:
            # Map player
            pass
