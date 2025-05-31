import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="MLB Odds Dashboard",
    page_icon="⚾",  # or use a URL to a favicon
    layout="wide"
)

# === Inject Custom CSS for Section Headers ===
st.markdown(
    """
    <style>
    .custom-header {
        color: #00FFC2;
        font-size: 32px;
        font-weight: 600;
        margin-top: 2em;
        margin-bottom: 0.5em;
    }
    </style>
    """,
    unsafe_allow_html=True
)

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
st.markdown("### <span class='custom-header'>All Games</span>", unsafe_allow_html=True)
#st.header("All Games")

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
st.markdown("### <span class='custom-header'>DFS Projections</span>", unsafe_allow_html=True)

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
st.markdown("### <span class='custom-header'>Moneyline Odds</span>", unsafe_allow_html=True)
#st.header("Moneyline Odds")

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
#st.header("Totals Odds")
st.markdown("### <span class='custom-header'>Totals Odds</span>", unsafe_allow_html=True)

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


@st.cache_data
def load_pitcher_props():
    return pd.read_csv(st.secrets["PITCHER_PROPS_URL"], index_col=False)

# === SECTION 3: Pitcher Props ===
st.markdown("### <span class='custom-header'>Pitcher Props</span>", unsafe_allow_html=True)
#st.header("Pitcher Props")

df_pitcher = load_pitcher_props()

st.sidebar.header("Pitcher Prop Filters")
pitcher_names = st.sidebar.multiselect("Pitcher Name", sorted(df_pitcher["Normalized Name"].dropna().unique()), default=[])
pitcher_teams = st.sidebar.multiselect("Team (Pitchers)", sorted(df_pitcher["Team"].dropna().unique()), default=[])
pitcher_books = st.sidebar.multiselect("Bookmaker (Pitchers)", sorted(df_pitcher["Bookmaker"].dropna().unique()), default=[])
pitcher_markets = st.sidebar.multiselect("Market (Pitchers)", sorted(df_pitcher["Market"].dropna().unique()), default=[])
pitcher_lineup = st.sidebar.multiselect("Lineup Confirmed (Pitchers)", sorted(df_pitcher["Lineup Confirmed"].dropna().unique()), default=[])

pitcher_point_range = numeric_slider(df_pitcher, "Point", "Point Range (Pitchers)")
pitcher_price_range = numeric_slider(df_pitcher, "Price", "Price Range (Pitchers)")
pitcher_roi_range = numeric_slider(df_pitcher, "Estimated ROI (%)", "ROI (%) Range (Pitchers)")
pitcher_conf_range = numeric_slider(df_pitcher, "Model Confidence", "Model Confidence Range (Pitchers)")

filtered_pitcher = df_pitcher.copy()
if pitcher_names:
    filtered_pitcher = filtered_pitcher[filtered_pitcher["Normalized Name"].isin(pitcher_names)]
if pitcher_teams:
    filtered_pitcher = filtered_pitcher[filtered_pitcher["Team"].isin(pitcher_teams)]
if pitcher_books:
    filtered_pitcher = filtered_pitcher[filtered_pitcher["Bookmaker"].isin(pitcher_books)]
if pitcher_markets:
    filtered_pitcher = filtered_pitcher[filtered_pitcher["Market"].isin(pitcher_markets)]
if pitcher_lineup:
    filtered_pitcher = filtered_pitcher[filtered_pitcher["Lineup Confirmed"].isin(pitcher_lineup)]

filtered_pitcher = filtered_pitcher[
    filtered_pitcher["Point"].between(*pitcher_point_range) &
    filtered_pitcher["Price"].between(*pitcher_price_range) &
    filtered_pitcher["Estimated ROI (%)"].between(*pitcher_roi_range) &
    filtered_pitcher["Model Confidence"].between(*pitcher_conf_range)
]

st.dataframe(filtered_pitcher, use_container_width=True)

@st.cache_data
def load_batter_props():
    return pd.read_csv(st.secrets["BATTER_PROPS_URL"], index_col=False)

# === SECTION 4: Batter Props ===
st.markdown("### <span class='custom-header'>Batter Props</span>", unsafe_allow_html=True)


df_batter = load_batter_props()

st.sidebar.header("Batter Prop Filters")
batter_names = st.sidebar.multiselect("Batter Name", sorted(df_batter["Normalized Name"].dropna().unique()), default=[])
batter_teams = st.sidebar.multiselect("Team (Batters)", sorted(df_batter["Team"].dropna().unique()), default=[])
batter_books = st.sidebar.multiselect("Bookmaker (Batters)", sorted(df_batter["Bookmaker"].dropna().unique()), default=[])
batter_markets = st.sidebar.multiselect("Market (Batters)", sorted(df_batter["Market"].dropna().unique()), default=[])
batter_lineup = st.sidebar.multiselect("Lineup Confirmed (Batters)", sorted(df_batter["Lineup Confirmed"].dropna().unique()), default=[])

batter_point_range = numeric_slider(df_batter, "Point", "Point Range (Batters)")
batter_price_range = numeric_slider(df_batter, "Price", "Price Range (Batters)")
batter_roi_range = numeric_slider(df_batter, "Estimated ROI (%)", "ROI (%) Range (Batters)")
batter_conf_range = numeric_slider(df_batter, "Model Confidence", "Model Confidence Range (Batters)")

filtered_batter = df_batter.copy()
if batter_names:
    filtered_batter = filtered_batter[filtered_batter["Normalized Name"].isin(batter_names)]
if batter_teams:
    filtered_batter = filtered_batter[filtered_batter["Team"].isin(batter_teams)]
if batter_books:
    filtered_batter = filtered_batter[filtered_batter["Bookmaker"].isin(batter_books)]
if batter_markets:
    filtered_batter = filtered_batter[filtered_batter["Market"].isin(batter_markets)]
if batter_lineup:
    filtered_batter = filtered_batter[filtered_batter["Lineup Confirmed"].isin(batter_lineup)]

filtered_batter = filtered_batter[
    filtered_batter["Point"].between(*batter_point_range) &
    filtered_batter["Price"].between(*batter_price_range) &
    filtered_batter["Estimated ROI (%)"].between(*batter_roi_range) &
    filtered_batter["Model Confidence"].between(*batter_conf_range)
]

st.dataframe(filtered_batter, use_container_width=True)

