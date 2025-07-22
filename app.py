
import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import streamlit.components.v1 as components
import numpy as np

st.set_page_config(page_title="MLB Odds Dashboard", page_icon="⚾", layout="wide")

st.markdown("""
    <style>
    .custom-header {
        color: #00B8D9;
        font-size: 32px;
        font-weight: 600;
        margin-top: 2em;
        margin-bottom: 0.5em;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='color: #00B8D9; font-weight: bold;'>MLB AI Model Viewer</h1>", unsafe_allow_html=True)

if st.sidebar.button("🔄 Refresh All Data"):
    st.cache_data.clear()

@st.cache_data
def load_game_details():
    return pd.read_csv(st.secrets["GAMES_URL"], index_col=False)

@st.cache_data
def load_dfs():
    return pd.read_csv(st.secrets["DFS_URL"], index_col=False)

@st.cache_data
def load_moneyline():
    return pd.read_csv(st.secrets["H2H_URL"], index_col=False)

@st.cache_data
def load_totals():
    return pd.read_csv(st.secrets["TOTALS_URL"], index_col=False)

@st.cache_data
def load_corrected_totals():
    return pd.read_csv(st.secrets["CORRECTED_TOTALS_URL"], index_col=False)

@st.cache_data
def load_pitcher_props():
    return pd.read_csv(st.secrets["PITCHER_PROPS_URL"], index_col=False)

@st.cache_data
def load_batter_props():
    return pd.read_csv(st.secrets["BATTER_PROPS_URL"], index_col=False)

time_url = st.secrets["CURRENT_TIME_URL"]
try:
    response = requests.get(time_url)
    response.raise_for_status()
    current_time = response.text.strip()
except Exception as e:
    current_time = f"Error fetching time: {e}"
st.write(f"Last simulation start time: **{current_time}**")

def numeric_slider(df, column, label):
    min_val = float(df[column].min())
    max_val = float(df[column].max())
    return st.sidebar.slider(label, min_value=min_val, max_value=max_val, value=(min_val, max_val), step=(max_val - min_val) / 100)

def draw_top_bets_plot_arguments_ets(df, title="", hover_columns=None):
    base_hover = ['Price', 'ETS Score']
    hover_cols = list(set(base_hover + (hover_columns or [])))
    df_sorted = df.sort_values(by='ETS Score', ascending=False).copy()
    df_sorted['is_pareto'] = False
    positive_roi = df_sorted[df_sorted['ETS Score'] > 0]
    pareto_indices, max_price = [], None
    for idx, row in positive_roi.iterrows():
        if max_price is None or row['Price'] >= max_price:
            pareto_indices.append(idx)
            max_price = row['Price']
    df_sorted.loc[pareto_indices, 'is_pareto'] = True
    def assign_color(row):
        if row['ETS Score'] <= 0:
            return '#5A5A5A'
        elif row['is_pareto']:
            return '#FF6F91'
        else:
            return '#00B8D9'
    df_sorted['marker_color'] = df_sorted.apply(assign_color, axis=1)
    fig = px.scatter(df_sorted, x='Price', y='ETS Score', hover_data=hover_cols, title=title)
    fig.update_traces(marker=dict(size=5), marker_color=df_sorted['marker_color'])
    fig.add_scatter(x=[None], y=[None], mode='markers', name=' ', marker=dict(opacity=0), showlegend=True)
    pareto_points = df_sorted[df_sorted['is_pareto']].sort_values(by='Price')
    if len(pareto_points) >= 2:
        fig.add_scatter(
            x=pareto_points['Price'], y=pareto_points['ETS Score'],
            mode='lines+markers', name='Top Bets',
            line=dict(color='#FF6F91', width=2, dash='dash'),
            marker=dict(color='#FF6F91', size=5),
            customdata=pareto_points[hover_cols],
            hovertemplate='<br>'.join([f'{col}: %{{customdata[{i}]}}' for i, col in enumerate(hover_cols)]) + '<extra></extra>'
        )
    fig.update_layout(
        width=650, height=400, plot_bgcolor='#121317', paper_bgcolor='#121317',
        font=dict(color='#FFFFFF'), title_font=dict(size=20, color='#00B8D9'),
        xaxis=dict(title_font=dict(color='#FFFFFF'), tickfont=dict(color='#FFFFFF')),
        yaxis=dict(title_font=dict(color='#FFFFFF'), tickfont=dict(color='#FFFFFF')),
        dragmode=False, hovermode='closest',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5, font=dict(size=14, color='#FFFFFF'))
    )
    html_str = fig.to_html(full_html=False, include_plotlyjs='cdn', config={'displayModeBar': False, 'scrollZoom': False})
    components.html(f"<div style='display: flex; justify-content: center; align-items: center;'>{html_str}</div>", height=450)

df_game = load_game_details()
df_dfs = load_dfs()
df_moneyline = load_moneyline()
df_totals = load_totals()
df_corrected_totals = load_corrected_totals()
df_pitcher = load_pitcher_props()
df_batter = load_batter_props()

st.markdown("### <span class='custom-header'>All Games</span>", unsafe_allow_html=True)
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

st.markdown("### <span class='custom-header'>DFS Projections</span>", unsafe_allow_html=True)
st.dataframe(df_dfs, use_container_width=True)

st.markdown("### <span class='custom-header'>Moneyline Odds</span>", unsafe_allow_html=True)
st.dataframe(df_moneyline, use_container_width=True)

st.markdown("### <span class='custom-header'>Corrected Totals</span>", unsafe_allow_html=True)
st.dataframe(df_corrected_totals, use_container_width=True)
draw_top_bets_plot_arguments_ets(df_corrected_totals, title="Corrected Totals", hover_columns=["Team", "Line", "Opponent"])

st.markdown("### <span class='custom-header'>Totals Odds</span>", unsafe_allow_html=True)
st.dataframe(df_totals, use_container_width=True)
draw_top_bets_plot_arguments_ets(df_totals, title="Totals Odds", hover_columns=["Team", "Line", "Opponent"])

st.markdown("### <span class='custom-header'>Pitcher Props</span>", unsafe_allow_html=True)
st.dataframe(df_pitcher, use_container_width=True)
draw_top_bets_plot_arguments_ets(df_pitcher, title="Pitcher Props", hover_columns=["Player", "Prop"])

st.markdown("### <span class='custom-header'>Batter Props</span>", unsafe_allow_html=True)
st.dataframe(df_batter, use_container_width=True)
draw_top_bets_plot_arguments_ets(df_batter, title="Batter Props", hover_columns=["Player", "Prop"])
