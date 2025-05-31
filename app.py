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

# === Load Data ===
@st.cache_data
def load_game_details():
    return pd.read_csv(st.secrets["GAMES_URL"], index_col=False)

@st.cache_data
def load_moneyline():
    return pd.read_csv(st.secrets["H2H_URL"], index_col=False)

@st.cache_data
def load_totals():
    return pd.read_csv(st.secrets["TOTALS_URL"], index_col=False)

# === SECTION 1: Game Summary ===
df_game = load_game_details()
st.header("All Games")

st.sidebar.header("Games Filters")
game_selected = st.sidebar.multiselect("Game Status", sorted(df_game["Game Status"].dropna().unique()), default=[])
away_team_selected = st.sidebar.multiselect("Away Team", sorted(df_game["Away Team"].dropna().unique()), default=[])
home_team_selected = st.sidebar.multiselect("Home Team", sorted(df_game["Home Team"].dropna().unique()), default=[])

filtered_game = df_game.copy()
if game_selected:
    filtered_game = filtered_game[filtered_game["Game Status"].isin(game_selected)]
if away_team_selected:
    filtered_game = filtered_game[filtered_game["Away Team"].isin(away_team_selected)]
if home_team_selected:
    filtered_game = filtered_game[filtered_game["Home Team"].isin(home_team_selected)]

st.dataframe(filtered_game, use_container_width=True)

@st.cache_data
def load_dfs():
    return pd.read_csv(st.secrets["DFS_URL"], index_col=False)

# === SECTION 2: DFS Projections ===
st.header("DFS Projections")

df_dfs = load_dfs()
df_dfs.sort_values(by='DFS Mean',ascending=False,inplace=True)

st.sidebar.header("DFS Filters")
dfs_role = st.sidebar.multiselect(
    "Pitcher or Batter",
    sorted(df_dfs["Pitcher of Batter"].dropna().unique()),
    default=[]
)
dfs_teams = st.sidebar.multiselect(
    "Team (DFS)",
    sorted(df_dfs["Team"].dropna().unique()),
    default=[]
)
dfs_lineup_confirmed = st.sidebar.multiselect(
    "Lineup Confirmed",
    sorted(df_dfs["Lineup Confirmed"].dropna().unique()),
    default=[]
)
dfs_mean_range = numeric_slider(df_dfs, "DFS Mean", "DFS Mean Range")
dfs_conf_range = numeric_slider(df_dfs, "Model Confidence", "Model Confidence Range")

filtered_dfs = df_dfs.copy()
if dfs_role:
    filtered_dfs = filtered_dfs[filtered_dfs["Pitcher of Batter"].isin(dfs_role)]
if dfs_teams:
    filtered_dfs = filtered_dfs[filtered_dfs["Team"].isin(dfs_teams)]
if dfs_lineup_confirmed:
    filtered_dfs = filtered_dfs[filtered_dfs["Lineup Confirmed"].isin(dfs_lineup_confirmed)]

filtered_dfs = filtered_dfs[
    filtered_dfs["DFS Mean"].between(*dfs_mean_range) &
    filtered_dfs["Model Confidence"].between(*dfs_conf_range)
]

st.dataframe(filtered_dfs, use_container_width=True)

# === SECTION 2: Moneyline Odds ===
st.header("Moneyline Odds")

df_moneyline = load_moneyline()

st.sidebar.header("Moneyline Filters")
mlb_game_ids_moneyline = st.sidebar.multiselect(
    "MLB Game ID (Moneyline)", 
    sorted(df_moneyline["MLB Game ID"].dropna().unique()), 
    default=[]
)
bookmakers_moneyline = st.sidebar.multiselect(
    "Bookmaker (Moneyline)", 
    sorted(df_moneyline["Bookmaker"].dropna().unique()), 
    default=[]
)
teams_moneyline = st.sidebar.multiselect(
    "Team", 
    sorted(df_moneyline["Team"].dropna().unique()), 
    default=[]
)
roi_range_moneyline = numeric_slider(df_moneyline, "Estimated ROI (%)", "ROI (%) Range (Moneyline)")

filtered_moneyline = df_moneyline.copy()
if mlb_game_ids_moneyline:
    filtered_moneyline = filtered_moneyline[filtered_moneyline["MLB Game ID"].isin(mlb_game_ids_moneyline)]
if bookmakers_moneyline:
    filtered_moneyline = filtered_moneyline[filtered_moneyline["Bookmaker"].isin(bookmakers_moneyline)]
if teams_moneyline:
    filtered_moneyline = filtered_moneyline[filtered_moneyline["Team"].isin(teams_moneyline)]

filtered_moneyline = filtered_moneyline[
    filtered_moneyline["Estimated ROI (%)"].between(*roi_range_moneyline)
]

st.dataframe(filtered_moneyline, use_container_width=True)

# === SECTION 3: Totals Odds ===
st.header("Totals Odds")

df_totals = load_totals()

st.sidebar.header("Totals Filters")
mlb_game_ids_totals = st.sidebar.multiselect(
    "MLB Game ID (Totals)", 
    sorted(df_totals["MLB Game ID"].dropna().unique()), 
    default=[]
)
away_teams_totals = st.sidebar.multiselect(
    "Away Team (Totals)", 
    sorted(df_totals["Away Team"].dropna().unique()), 
    default=[]
)
home_teams_totals = st.sidebar.multiselect(
    "Home Team (Totals)", 
    sorted(df_totals["Home Team"].dropna().unique()), 
    default=[]
)
bookmakers_totals = st.sidebar.multiselect(
    "Bookmaker (Totals)", 
    sorted(df_totals["Bookmaker"].dropna().unique()), 
    default=[]
)
price_range_totals = numeric_slider(df_totals, "Price", "Price Range (Totals)")
roi_range_totals = numeric_slider(df_totals, "Estimated ROI (%)", "ROI (%) Range (Totals)")

filtered_totals = df_totals.copy()
if mlb_game_ids_totals:
    filtered_totals = filtered_totals[filtered_totals["MLB Game ID"].isin(mlb_game_ids_totals)]
if away_teams_totals:
    filtered_totals = filtered_totals[filtered_totals["Away Team"].isin(away_teams_totals)]
if home_teams_totals:
    filtered_totals = filtered_totals[filtered_totals["Home Team"].isin(home_teams_totals)]
if bookmakers_totals:
    filtered_totals = filtered_totals[filtered_totals["Bookmaker"].isin(bookmakers_totals)]

filtered_totals = filtered_totals[
    filtered_totals["Price"].between(*price_range_totals) &
    filtered_totals["Estimated ROI (%)"].between(*roi_range_totals)
]

st.dataframe(filtered_totals, use_container_width=True)
