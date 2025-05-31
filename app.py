import streamlit as st
import pandas as pd

st.set_page_config(page_title="MLB Odds Dashboard", layout="wide")
st.title("MLB Web Odds Viewer")

# === Refresh Button ===
if st.sidebar.button("🔄 Refresh All Data"):
    st.cache_data.clear()

# === Helper: Numeric Slider ===
def numeric_slider(df, column, label):
    min_val = float(df[column].min())
    max_val = float(df[column].max())
    return st.sidebar.slider(
        label,
        min_value=min_val,
        max_value=max_val,
        value=(min_val, max_val),
        step=(max_val - min_val) / 100
    )

# === Load Game Odds ===
@st.cache_data
def load_game_details():
    url = st.secrets["GAMES_URL"]
    df = pd.read_csv(url,index_col=False)
    return df

# === SECTION 1: Game Odds ===
df_game = load_game_details()
st.header("All Games")

st.sidebar.header("Games Filters")
game_selected = st.sidebar.multiselect("Game Status", sorted(df_game["Game Status"].dropna().unique()), default=[])
away_team_selected = st.sidebar.multiselect("Away Team", sorted(df_game["Away Team"].dropna().unique()), default=[])
home_team_selected = st.sidebar.multiselect("Home Team", sorted(df_game["Home Team"].dropna().unique()), default=[])

# roi_range_game = numeric_slider(df_game, "ROI (%)", "ROI (%) Range (Game)")
# kelly_range_game = numeric_slider(df_game, "kelly", "Kelly Range (Game)")
# odds_range_game = numeric_slider(df_game, "americanOdds", "American Odds Range")

filtered_game = df_game.copy()
if game_selected:
    filtered_game = filtered_game[filtered_game["Game Status"].isin(game_selected)]
if away_team_selected:
    filtered_game = filtered_game[filtered_game["Away Team"].isin(away_team_selected)]
if home_team_selected:
    filtered_game = filtered_game[filtered_game["Home Team"].isin(home_team_selected)]

# filtered_game = filtered_game[
#     filtered_game["ROI (%)"].between(*roi_range_game) &
#     filtered_game["kelly"].between(*kelly_range_game) &
#     filtered_game["americanOdds"].between(*odds_range_game)
# ]

st.dataframe(filtered_game, use_container_width=True)
