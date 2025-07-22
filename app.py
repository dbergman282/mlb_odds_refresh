# mlb_dashboard.py

import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import streamlit.components.v1 as components
import numpy as np

st.set_page_config(page_title="MLB Odds Dashboard", page_icon="⚾", layout="wide")

# === Header Styling ===
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

# === Load Data ===
@st.cache_data
def load_totals():
    return pd.read_csv(st.secrets["TOTALS_URL"], index_col=False)

@st.cache_data
def load_corrected_totals():
    return pd.read_csv(st.secrets["CORRECTED_TOTALS_URL"], index_col=False)

df_totals = load_totals()
df_corrected_totals = load_corrected_totals()

for df in [df_totals, df_corrected_totals]:
    df['ETS Score'] = np.where(df['ETS Score'] == 0, 0, np.sign(df['ETS Score']) * np.log1p(np.abs(df['ETS Score'])))
    df.sort_values(by='ETS Score', ascending=False, inplace=True)

# === Shared Sidebar Filters ===
st.sidebar.header("Totals Filters")

combined_df = pd.concat([df_totals, df_corrected_totals])
mlb_game_ids = st.sidebar.multiselect("MLB Game ID", sorted(combined_df["MLB Game ID"].dropna().unique()))
away_teams = st.sidebar.multiselect("Away Team", sorted(combined_df["Away Team"].dropna().unique()))
home_teams = st.sidebar.multiselect("Home Team", sorted(combined_df["Home Team"].dropna().unique()))
bookmakers = st.sidebar.multiselect("Bookmaker", sorted(combined_df["Bookmaker"].dropna().unique()))
ets_range = st.sidebar.slider("ETS Score Range", float(combined_df["ETS Score"].min()), float(combined_df["ETS Score"].max()), value=(float(combined_df["ETS Score"].min()), float(combined_df["ETS Score"].max())))
roi_range = st.sidebar.slider("ROI (%) Range", float(combined_df["Estimated ROI (%)"].min()), float(combined_df["Estimated ROI (%)"].max()), value=(float(combined_df["Estimated ROI (%)"].min()), float(combined_df["Estimated ROI (%)"].max())))
price_range = st.sidebar.slider("Price Range", float(combined_df["Price"].min()), float(combined_df["Price"].max()), value=(float(combined_df["Price"].min()), float(combined_df["Price"].max())))
conf_range = st.sidebar.slider("Game Confidence Range", float(combined_df["Game Confidence"].min()), float(combined_df["Game Confidence"].max()), value=(float(combined_df["Game Confidence"].min()), float(combined_df["Game Confidence"].max())))

def apply_filters(df):
    df = df.copy()
    if mlb_game_ids:
        df = df[df["MLB Game ID"].isin(mlb_game_ids)]
    if away_teams:
        df = df[df["Away Team"].isin(away_teams)]
    if home_teams:
        df = df[df["Home Team"].isin(home_teams)]
    if bookmakers:
        df = df[df["Bookmaker"].isin(bookmakers)]
    df = df[
        df["ETS Score"].between(*ets_range) &
        df["Estimated ROI (%)"].between(*roi_range) &
        df["Price"].between(*price_range) &
        df["Game Confidence"].between(*conf_range)
    ]
    return df

# === Plotting Function ===
def draw_top_bets_plot_arguments_ets(df, title="", hover_columns=None):
    hover_cols = list(set(['Price', 'ETS Score'] + (hover_columns or [])))
    df_sorted = df.sort_values(by='ETS Score', ascending=False).copy()
    df_sorted['is_pareto'] = False
    pareto_indices, max_price = [], None
    for idx, row in df_sorted[df_sorted['ETS Score'] > 0].iterrows():
        if max_price is None or row['Price'] >= max_price:
            pareto_indices.append(idx)
            max_price = row['Price']
    df_sorted.loc[pareto_indices, 'is_pareto'] = True
    df_sorted['marker_color'] = df_sorted.apply(lambda r: '#5A5A5A' if r['ETS Score'] <= 0 else '#FF6F91' if r['is_pareto'] else '#00B8D9', axis=1)

    fig = px.scatter(df_sorted, x='Price', y='ETS Score', hover_data=hover_cols, title=title)
    fig.update_traces(marker=dict(size=6), marker_color=df_sorted['marker_color'])
    fig.add_scatter(x=[None], y=[None], mode='markers', name=' ', marker=dict(opacity=0), showlegend=True)

    pareto = df_sorted[df_sorted['is_pareto']].sort_values(by='Price')
    if len(pareto) >= 2:
        fig.add_scatter(
            x=pareto['Price'],
            y=pareto['ETS Score'],
            mode='lines+markers',
            name='Top Bets',
            line=dict(color='#FF6F91', width=2, dash='dash'),
            marker=dict(color='#FF6F91', size=6),
            customdata=pareto[hover_cols],
            hovertemplate='<br>'.join([f'{col}: %{{customdata[{i}]}}' for i, col in enumerate(hover_cols)]) + '<extra></extra>'
        )

    fig.update_layout(
        width=650, height=400,
        plot_bgcolor='#121317', paper_bgcolor='#121317',
        font=dict(color='#FFFFFF'),
        title_font=dict(size=20, color='#00B8D9'),
        xaxis=dict(title_font=dict(color='#FFFFFF'), tickfont=dict(color='#FFFFFF')),
        yaxis=dict(title_font=dict(color='#FFFFFF'), tickfont=dict(color='#FFFFFF')),
        dragmode=False, hovermode='closest',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5, font=dict(size=14, color='#FFFFFF'))
    )

    html_str = fig.to_html(full_html=False, include_plotlyjs='cdn', config={'displayModeBar': False, 'scrollZoom': False})
    components.html(f"<div style='display: flex; justify-content: center; align-items: center;'>{html_str}</div>", height=450)

# === Section: Corrected Totals ===
st.markdown("### <span class='custom-header'>Corrected Totals</span>", unsafe_allow_html=True)
filtered_corrected = apply_filters(df_corrected_totals)
with st.expander("🛠️ Expand to View Corrected Totals", expanded=False):
    st.dataframe(filtered_corrected, use_container_width=True, height=200)
    draw_top_bets_plot_arguments_ets(filtered_corrected, "🛠️ Corrected Totals: Price vs ETS Score", list(filtered_corrected.columns))

# === Section: Totals Odds ===
st.markdown("### <span class='custom-header'>Totals Odds</span>", unsafe_allow_html=True)
filtered_totals = apply_filters(df_totals)
with st.expander("🔢 Expand to View Totals", expanded=False):
    st.dataframe(filtered_totals, use_container_width=True, height=200)
    draw_top_bets_plot_arguments_ets(filtered_totals, "🔢 Totals: Price vs ETS Score", list(filtered_totals.columns))
