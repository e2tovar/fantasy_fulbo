import streamlit as st
from database.player_statistics import PlayerStatisticsManager

psm = PlayerStatisticsManager()

st.header("Estadísticas Generales")
psm = PlayerStatisticsManager()
last_year_season = psm.fetch_last_year_season()
print(last_year_season)
last_year = last_year_season[0][0]
last_season = last_year_season[0][1]
df_gen = psm.fetch_general_statistics(year=last_year, season=last_season)
st.dataframe(df_gen)
