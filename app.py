import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import streamlit.components.v1 as components
import numpy as np

st.set_page_config(
    page_title="MLB Odds Dashboard",
    page_icon="⚾",  # or use a URL to a favicon
    layout="wide"
)

def draw_top_bets_plot_arguments_ets(df, title="", hover_columns=None):

    # Default hover columns
    base_hover = ['Price', 'ETS Score']
    if hover_columns:
        hover_cols = base_hover + hover_columns
    else:
        hover_cols = base_hover

    hover_cols = list(set(hover_cols))

    # Sort and mark Pareto-optimal
    df_sorted = df.sort_values(by='ETS Score', ascending=False).copy()

    df_sorted['is_pareto'] = False
    positive_roi = df_sorted[df_sorted['ETS Score'] > 0].sort_values(by='ETS Score', ascending=False)
    pareto_indices, max_price = [], None
    for idx, row in positive_roi.iterrows():
        if max_price is None or row['Price'] >= max_price:
            pareto_indices.append(idx)
            max_price = row['Price']
    df_sorted.loc[pareto_indices, 'is_pareto'] = True

    # Assign colors
    def assign_color(row):
        if row['ETS Score'] <= 0:
            return '#5A5A5A'
        elif row['is_pareto']:
            return '#FF6F91'
        else:
            return '#00B8D9'
    df_sorted['marker_color'] = df_sorted.apply(assign_color, axis=1)

    # Base scatter plot
    fig = px.scatter(
        df_sorted,
        x='Price',
        y='ETS Score',
        hover_data=hover_cols,
        title=title,
    )
    fig.update_traces(marker=dict(size=5), marker_color=df_sorted['marker_color'])
    fig.add_scatter(
        x=[None],
        y=[None],
        mode='markers',
        name=' ',
        marker=dict(opacity=0),
        showlegend=True
    )

    # Add dashed Pareto line with custom hover
    pareto_points = df_sorted[df_sorted['is_pareto']].sort_values(by='Price')
    if len(pareto_points) >= 2:
        fig.add_scatter(
            x=pareto_points['Price'],
            y=pareto_points['ETS Score'],
            mode='lines+markers',
            name='Top Bets',
            line=dict(color='#FF6F91', width=2, dash='dash'),
            marker=dict(color='#FF6F91', size=5),
            customdata=pareto_points[hover_cols],
            hovertemplate = '<br>'.join([f'{col}: %{{customdata[{i}]}}' for i, col in enumerate(hover_cols)]) + '<extra></extra>'
        )

    # Layout and interactivity lock
    fig.update_layout(
        width=600,
        height=400,
        plot_bgcolor='#121317',
        paper_bgcolor='#121317',
        font=dict(color='#FFFFFF'),
        title_font=dict(size=20, color='#00B8D9'),
        xaxis=dict(title_font=dict(color='#FFFFFF'), tickfont=dict(color='#FFFFFF')),
        yaxis=dict(title_font=dict(color='#FFFFFF'), tickfont=dict(color='#FFFFFF')),
        dragmode=False,
        hovermode='closest',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(
                size=14,           # or whatever matches your theme
                color='#FFFFFF',
                family='sans-serif'
            )
        ),
        margin=dict(l=100, r=40, t=110, b=40)
    )

    # Disable zoom/pan/select, allow hover
    html_str = fig.to_html(full_html=False, include_plotlyjs='cdn', config={
        'displayModeBar': False,
        'staticPlot': False,
        'scrollZoom': False,
        'editable': False,
        'doubleClick': False,
        'displaylogo': False
    })
    components.html(
        f"<div style='display: flex; justify-content: center; align-items: center;'>{html_str}</div>",
        height=450,
    )


def draw_top_bets_plot_arguments(df, title="", hover_columns=None):

    # Default hover columns
    base_hover = ['Price', 'Estimated ROI (%)']
    if hover_columns:
        hover_cols = base_hover + hover_columns
    else:
        hover_cols = base_hover

    hover_cols = list(set(hover_cols))

    # Sort and mark Pareto-optimal
    df_sorted = df.sort_values(by='Estimated ROI (%)', ascending=False).copy()
    df_sorted['is_pareto'] = False
    positive_roi = df_sorted[df_sorted['Estimated ROI (%)'] > 0].sort_values(by='Estimated ROI (%)', ascending=False)
    pareto_indices, max_price = [], None
    for idx, row in positive_roi.iterrows():
        if max_price is None or row['Price'] >= max_price:
            pareto_indices.append(idx)
            max_price = row['Price']
    df_sorted.loc[pareto_indices, 'is_pareto'] = True

    # Assign colors
    def assign_color(row):
        if row['Estimated ROI (%)'] < 0:
            return '#5A5A5A'
        elif row['is_pareto']:
            return '#FF6F91'
        else:
            return '#00B8D9'
    df_sorted['marker_color'] = df_sorted.apply(assign_color, axis=1)

    # Base scatter plot
    fig = px.scatter(
        df_sorted,
        x='Price',
        y='Estimated ROI (%)',
        hover_data=hover_cols,
        title=title,
    )
    fig.update_traces(marker=dict(size=8), marker_color=df_sorted['marker_color'])
    fig.add_scatter(
        x=[None],
        y=[None],
        mode='markers',
        name=' ',
        marker=dict(opacity=0),
        showlegend=True
    )

    # Add dashed Pareto line with custom hover
    pareto_points = df_sorted[df_sorted['is_pareto']].sort_values(by='Price')
    if len(pareto_points) >= 2:
        fig.add_scatter(
            x=pareto_points['Price'],
            y=pareto_points['Estimated ROI (%)'],
            mode='lines+markers',
            name='Top Bets',
            line=dict(color='#FF6F91', width=2, dash='dash'),
            marker=dict(color='#FF6F91', size=8),
            customdata=pareto_points[hover_cols],
            hovertemplate = '<br>'.join([f'{col}: %{{customdata[{i}]}}' for i, col in enumerate(hover_cols)]) + '<extra></extra>'
        )

    # Layout and interactivity lock
    fig.update_layout(
        width=600,
        height=400,
        plot_bgcolor='#121317',
        paper_bgcolor='#121317',
        font=dict(color='#FFFFFF'),
        title_font=dict(size=20, color='#00B8D9'),
        xaxis=dict(title_font=dict(color='#FFFFFF'), tickfont=dict(color='#FFFFFF')),
        yaxis=dict(title_font=dict(color='#FFFFFF'), tickfont=dict(color='#FFFFFF')),
        dragmode=False,
        hovermode='closest',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(
                size=14,           # or whatever matches your theme
                color='#FFFFFF',
                family='sans-serif'
            )
        ),
        margin=dict(l=40, r=40, t=110, b=40)
    )

    # Disable zoom/pan/select, allow hover
    html_str = fig.to_html(full_html=False, include_plotlyjs='cdn', config={
        'displayModeBar': False,
        'staticPlot': False,
        'scrollZoom': False,
        'editable': False,
        'doubleClick': False,
        'displaylogo': False
    })
    components.html(
        f"<div style='display: flex; justify-content: center; align-items: center;'>{html_str}</div>",
        height=450,
    )



def draw_top_bets_plot(df, title=""):
    # Sort by ROI descending
    df_sorted = df.sort_values(by='Estimated ROI (%)', ascending=False).copy()

    # Mark Pareto-optimal rows
    df_sorted['is_pareto'] = False
    positive_roi = df_sorted[df_sorted['Estimated ROI (%)'] > 0].sort_values(by='Estimated ROI (%)', ascending=False)
    
    pareto_indices = []
    max_price = None
    for idx, row in positive_roi.iterrows():
        price = row['Price']
        if max_price is None or price >= max_price:
            pareto_indices.append(idx)
            max_price = price
    df_sorted.loc[pareto_indices, 'is_pareto'] = True

    # Assign marker colors
    def assign_color(row):
        if row['Estimated ROI (%)'] < 0:
            return '#5A5A5A'
        elif row['is_pareto']:
            return '#FF6F91'
        else:
            return '#00B8D9'
    df_sorted['marker_color'] = df_sorted.apply(assign_color, axis=1)

    # Create scatter plot
    fig = px.scatter(
        df_sorted,
        x='Price',
        y='Estimated ROI (%)',
        hover_data=df_sorted.columns,
        title=title,
    )
    fig.update_traces(marker=dict(size=8), marker_color=df_sorted['marker_color'])

    # Add dashed "Top Bets" line
    pareto_points = df_sorted[df_sorted['is_pareto']].sort_values(by='Price')
    if len(pareto_points) >= 2:
        fig.add_scatter(
            x=pareto_points['Price'],
            y=pareto_points['Estimated ROI (%)'],
            mode='lines+markers',
            name='Top Bets',
            line=dict(color='#FF6F91', width=2, dash='dash'),
            marker=dict(color='#FF6F91', size=8),
        )

    # Style plot
    fig.update_layout(
        width=900,
        height=600,
        plot_bgcolor='#121317',
        paper_bgcolor='#121317',
        font=dict(color='#FFFFFF'),
        title_font=dict(size=20, color='#00B8D9'),
        xaxis=dict(title_font=dict(color='#FFFFFF'), tickfont=dict(color='#FFFFFF')),
        yaxis=dict(title_font=dict(color='#FFFFFF'), tickfont=dict(color='#FFFFFF')),
        margin=dict(l=40, r=40, t=60, b=40),
        dragmode=False,             # ⛔ disables click/drag interactions
        hovermode='closest',        # ✅ enables precise hover
    )

    # Disable zoom/select, keep hover
    html_str = fig.to_html(full_html=False, include_plotlyjs='cdn', config={
        'displayModeBar': False,
        'staticPlot': False,
        'scrollZoom': False,
        'editable': False,
        'doubleClick': False,
        'displaylogo': False
    })

    components.html(
        f"<div style='display: flex; justify-content: center; align-items: center;'>{html_str}</div>",
        height=700,
    )



# === Inject Custom CSS for Section Headers ===
st.markdown(
    """
    <style>
    .custom-header {
        color: #00B8D9;
        font-size: 32px;
        font-weight: 600;
        margin-top: 2em;
        margin-bottom: 0.5em;
    }
    </style>
    """,
    unsafe_allow_html=True
)
#FF2EB6
#00FFC2
st.markdown(
    "<h1 style='color: #00B8D9; font-weight: bold;'>MLB AI Model Viewer</h1>",
    unsafe_allow_html=True
)

st.title("DFS Champion")

# Replace with your desired YouTube URL
youtube_url = "https://www.google.com/search?q=david+bergman+draftkings+youtbue&sca_esv=43bdce033f74f264&rlz=1C5CHFA_enUS1043US1043&ei=3iZUaJPJK7yiptQP06yl0As&ved=0ahUKEwiTsO_w4P2NAxU8kYkEHVNWCboQ4dUDCBI&uact=5&oq=david+bergman+draftkings+youtbue&gs_lp=Egxnd3Mtd2l6LXNlcnAiIGRhdmlkIGJlcmdtYW4gZHJhZnRraW5ncyB5b3V0YnVlMgcQIRigARgKMgcQIRigARgKMgcQIRigARgKMgcQIRigARgKSLQTUNgNWLkScAJ4AJABAJgBcKAB9gWqAQM2LjK4AQPIAQD4AQGYAgqgAo8GwgIHEAAYsAMYHsICCxAAGLADGKIEGIkFwgIIEAAYsAMY7wXCAgYQABgWGB7CAggQABiiBBiJBcICBRAAGO8FwgIFECEYoAGYAwCIBgGQBgWSBwM4LjKgB8kjsgcDNi4yuAeJBsIHAzEuOcgHEA&sclient=gws-wiz-serp#fpstate=ive&vld=cid:489a3f80,vid:GP-YpFRHK1U,st:0"
st.video(youtube_url)

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

time_url = st.secrets["CURRENT_TIME_URL"]

# Fetch the time from the URL
try:
    response = requests.get(time_url)
    response.raise_for_status()  # Raise error for bad responses
    current_time = response.text.strip()
except Exception as e:
    current_time = f"Error fetching time: {e}"

# Display in the app
#st.title("Last Simulation Start")
st.write(f"Last simulation start time: **{current_time}**")

# === SECTION 1: Game Summary ===
st.markdown("### <span class='custom-header'>All Games</span>", unsafe_allow_html=True)
df_game = load_game_details()

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
    
with st.expander("🗓️ Expand to View Daily MLB Games", expanded=False):
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

with st.expander("🎯 Expand to View DFS Projections for Every Starting Player", expanded=False):
    st.dataframe(filtered_dfs, use_container_width=True,height=200)

# === SECTION 2: Moneyline Odds ===
st.markdown("### <span class='custom-header'>Moneyline Odds</span>", unsafe_allow_html=True)
#st.header("Moneyline Odds")

df_moneyline = load_moneyline()
df_moneyline['ETS Score'] = np.where(df_moneyline['ETS Score'] == 0, 0, np.sign(df_moneyline['ETS Score']) * np.log1p(np.abs(df_moneyline['ETS Score'])))
df_moneyline.sort_values(by='ETS Score',ascending=False,inplace=True)

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

ets_range_moneyline = numeric_slider(df_moneyline, "ETS Score", "ETS Range (Moneyline)")
roi_range_moneyline = numeric_slider(df_moneyline, "Estimated ROI (%)", "ROI (%) Range (Moneyline)")
price_range_moneyline = numeric_slider(df_moneyline, "Price", "Price Range (Moneyline)")
conf_range_moneyline = numeric_slider(df_moneyline, "Game Confidence", "Game Confidence (Moneyline)")

filtered_moneyline = df_moneyline.copy()
if mlb_game_ids_moneyline:
    filtered_moneyline = filtered_moneyline[filtered_moneyline["MLB Game ID"].isin(mlb_game_ids_moneyline)]
if bookmakers_moneyline:
    filtered_moneyline = filtered_moneyline[filtered_moneyline["Bookmaker"].isin(bookmakers_moneyline)]
if teams_moneyline:
    filtered_moneyline = filtered_moneyline[filtered_moneyline["Team"].isin(teams_moneyline)]

filtered_moneyline = filtered_moneyline[
    filtered_moneyline["ETS Score"].between(*ets_range_moneyline)
]
filtered_moneyline = filtered_moneyline[
    filtered_moneyline["Game Confidence"].between(*conf_range_moneyline)
]
filtered_moneyline = filtered_moneyline[
    filtered_moneyline["Price"].between(*price_range_moneyline)
]
filtered_moneyline = filtered_moneyline[
    filtered_moneyline["Estimated ROI (%)"].between(*roi_range_moneyline)
]
with st.expander("💸 Expand to View Moneyline Bets", expanded=False):
    st.dataframe(filtered_moneyline, use_container_width=True,height=200)

    #draw_top_bets_plot_arguments(filtered_moneyline,"💸 Moneyline: Price vs ROI",list(filtered_moneyline.columns))
    draw_top_bets_plot_arguments_ets(filtered_moneyline,"💸 Moneyline: Price vs ETS Score",list(filtered_moneyline.columns))



# === SECTION 3: Totals Odds ===
#st.header("Totals Odds")
st.markdown("### <span class='custom-header'>Totals Odds</span>", unsafe_allow_html=True)

df_totals = load_totals()
df_totals['ETS Score'] = np.where(df_totals['ETS Score'] == 0, 0, np.sign(df_totals['ETS Score']) * np.log1p(np.abs(df_totals['ETS Score'])))
df_totals.sort_values(by=['ETS Score'],ascending=False, inplace=True)

# df_totals['Kelly'] = np.where(
#     df_totals['Estimated ROI (%)'] > 0,
#     (df_totals['Estimated ROI (%)']/100.0)/(df_totals['Price']-1),
#     0
# )
    
# df_totals.sort_values(by='Estimated ROI (%)',ascending=False,inplace=True)

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
ets_range_totals = numeric_slider(df_totals, "ETS Score", "ETS Range (Totals)")
roi_range_totals = numeric_slider(df_totals, "Estimated ROI (%)", "ROI (%) Range (Totals)")
price_range_totals = numeric_slider(df_totals, "Price", "Price Range (Totals)")
conf_range_totals = numeric_slider(df_totals, "Game Confidence", "Price Range (Totals)")

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
    filtered_totals["ETS Score"].between(*ets_range_totals) &
    filtered_totals["Game Confidence"].between(*conf_range_totals) &
    filtered_totals["Price"].between(*price_range_totals) &
    filtered_totals["Estimated ROI (%)"].between(*roi_range_totals)
]
with st.expander("🔢 Expand to View Totals", expanded=False):
    st.dataframe(filtered_totals, use_container_width=True,height=200)
    #draw_top_bets_plot_arguments(filtered_totals,"🔢 Totals: Price vs ROI",list(filtered_totals.columns))
    draw_top_bets_plot_arguments_ets(filtered_totals,"🔢 Totals: Price vs ETS Score",list(filtered_totals.columns))




@st.cache_data
def load_pitcher_props():
    return pd.read_csv(st.secrets["PITCHER_PROPS_URL"], index_col=False)

# === SECTION 3: Pitcher Props ===
st.markdown("### <span class='custom-header'>Pitcher Props</span>", unsafe_allow_html=True)
#st.header("Pitcher Props")

df_pitcher = load_pitcher_props()
df_pitcher['ETS Score'] = np.where(df_pitcher['ETS Score'] == 0, 0, np.sign(df_pitcher['ETS Score']) * np.log1p(np.abs(df_pitcher['ETS Score'])))

# df_pitcher['Kelly'] = (df_pitcher['Estimated ROI (%)']/100.0)/(df_pitcher['Price']-1)
# df_pitcher['ETS Score'] = df_pitcher['Kelly']*df_pitcher['Model Confidence']
df_pitcher.sort_values(by='ETS Score',ascending=False,inplace=True)

st.sidebar.header("Pitcher Prop Filters")
pitcher_names = st.sidebar.multiselect("Pitcher Name", sorted(df_pitcher["Normalized Name"].dropna().unique()), default=[])
pitcher_teams = st.sidebar.multiselect("Team (Pitchers)", sorted(df_pitcher["Team"].dropna().unique()), default=[])
pitcher_books = st.sidebar.multiselect("Bookmaker (Pitchers)", sorted(df_pitcher["Bookmaker"].dropna().unique()), default=[])
pitcher_markets = st.sidebar.multiselect("Market (Pitchers)", sorted(df_pitcher["Market"].dropna().unique()), default=[])
pitcher_lineup = st.sidebar.multiselect("Lineup Confirmed (Pitchers)", sorted(df_pitcher["Lineup Confirmed"].dropna().unique()), default=[])


pitcher_ets_range = numeric_slider(df_pitcher, "ETS Score", "ETS Range (Pitchers)")
pitcher_roi_range = numeric_slider(df_pitcher, "Estimated ROI (%)", "ROI (%) Range (Pitchers)")
pitcher_price_range = numeric_slider(df_pitcher, "Price", "Price Range (Pitchers)")
#pitcher_point_range = numeric_slider(df_pitcher, "Point", "Point Range (Pitchers)")
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
    filtered_pitcher["ETS Score"].between(*pitcher_ets_range) &
    filtered_pitcher["Price"].between(*pitcher_price_range) &
    filtered_pitcher["Estimated ROI (%)"].between(*pitcher_roi_range) &
    filtered_pitcher["Model Confidence"].between(*pitcher_conf_range)
]
with st.expander("🤾‍♂️⚾ Expand to View Pitcher Props", expanded=False):
    st.dataframe(filtered_pitcher, use_container_width=True,height=200)
    #draw_top_bets_plot_arguments(filtered_pitcher,"🤾‍♂️⚾ Pitcher Props: Price vs ROI",list(filtered_pitcher.columns))
    draw_top_bets_plot_arguments_ets(filtered_pitcher,"🤾‍♂️⚾ Pitcher Props: Price vs ETS Score",list(filtered_pitcher.columns))


@st.cache_data
def load_batter_props():
    return pd.read_csv(st.secrets["BATTER_PROPS_URL"], index_col=False)

# === SECTION 4: Batter Props ===
st.markdown("### <span class='custom-header'>Batter Props</span>", unsafe_allow_html=True)


df_batter = load_batter_props()
df_batter['ETS Score'] = np.where(df_batter['ETS Score'] == 0, 0, np.sign(df_batter['ETS Score']) * np.log1p(np.abs(df_batter['ETS Score'])))

df_batter.sort_values(by='ETS Score',ascending=False,inplace=True)

st.sidebar.header("Batter Prop Filters")
batter_names = st.sidebar.multiselect("Batter Name", sorted(df_batter["Normalized Name"].dropna().unique()), default=[])
batter_teams = st.sidebar.multiselect("Team (Batters)", sorted(df_batter["Team"].dropna().unique()), default=[])
batter_books = st.sidebar.multiselect("Bookmaker (Batters)", sorted(df_batter["Bookmaker"].dropna().unique()), default=[])
batter_markets = st.sidebar.multiselect("Market (Batters)", sorted(df_batter["Market"].dropna().unique()), default=[])
batter_lineup = st.sidebar.multiselect("Lineup Confirmed (Batters)", sorted(df_batter["Lineup Confirmed"].dropna().unique()), default=[])

batter_ets_range = numeric_slider(df_batter, "ETS Score", "ETS Range (Batters)")
batter_roi_range = numeric_slider(df_batter, "Estimated ROI (%)", "ROI (%) Range (Batters)")
batter_price_range = numeric_slider(df_batter, "Price", "Price Range (Batters)")
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
    filtered_batter["ETS Score"].between(*batter_ets_range) &
    filtered_batter["Estimated ROI (%)"].between(*batter_roi_range) &
    filtered_batter["Price"].between(*batter_price_range) &
    filtered_batter["Model Confidence"].between(*batter_conf_range)
]

with st.expander("🥎🔨 Expand to View Batter Props", expanded=False):
    st.dataframe(filtered_batter, use_container_width=True,height=200)
    
    #draw_top_bets_plot_arguments(filtered_batter,"🥎🔨 Batter Props: Price vs ROI",list(filtered_batter.columns))
    draw_top_bets_plot_arguments_ets(filtered_batter,"🥎🔨 Batter Props: Price vs ETS Score",list(filtered_pitcher.columns))


