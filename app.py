import streamlit as st
import pandas as pd
from itscalledsoccer.client import AmericanSoccerAnalysis
import pulp
import plotly.express as px
import plotly.graph_objects as go

# Set page config
st.set_page_config(
    page_title="FM24 DATA HUB // MLS ANALYTICS",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS STYLING (FM24 DARK THEME WITH RAJDHANI FONT) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700&family=Inter:wght@400;500;600;700&display=swap');
    
    /* Hide top Streamlit header decoration color line only */
    div[data-testid="stDecoration"] {
        display: none !important;
    }
    
    header[data-testid="stHeader"] {
        background-color: transparent !important;
        background: transparent !important;
        height: 0px !important;
        z-index: 99999 !important;
    }
    
    /* Keep Sidebar expand/collapse button visible and styled cleanly in FM24 Dark Theme */
    [data-testid="collapsedControl"], button[data-testid="stSidebarCollapseButton"] {
        display: flex !important;
        visibility: visible !important;
        background-color: #1a1528 !important;
        border: 1px solid rgba(16, 185, 129, 0.4) !important;
        border-radius: 6px !important;
        color: #ffffff !important;
    }
    
    [data-testid="collapsedControl"] svg, button[data-testid="stSidebarCollapseButton"] svg {
        fill: #10b981 !important;
        color: #10b981 !important;
        stroke: #10b981 !important;
    }
    
    /* Style Plotly ModeBar toolbar cleanly with dark background and white/green icons across ALL graphs */
    .js-plotly-plot .plotly .modebar {
        background-color: #1a1528 !important;
        border: 1px solid rgba(16, 185, 129, 0.4) !important;
        border-radius: 4px !important;
        padding: 2px !important;
    }
    
    .js-plotly-plot .plotly .modebar-btn path {
        fill: #ffffff !important;
    }
    
    .js-plotly-plot .plotly .modebar-btn:hover path {
        fill: #10b981 !important;
    }
    
    /* Adjust top padding of the page */
    .main .block-container {
        padding-top: 2.5rem !important;
        padding-bottom: 2rem !important;
    }
    
    /* Main background - Deep Dark Purple/Charcoal */
    .stApp {
        background-color: #120e1e;
        color: #ffffff !important;
        font-family: 'Rajdhani', 'Inter', sans-serif !important;
    }
    
    /* Base typography rules */
    p, span, label, div, button, input, textarea {
        color: #ffffff;
        font-family: 'Rajdhani', 'Inter', sans-serif;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #0b0813 !important;
        border-right: 1px solid rgba(16, 185, 129, 0.3);
    }
    
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] span, 
    section[data-testid="stSidebar"] label {
        color: #ffffff !important;
    }
    
    /* Tactical Emerald Green (#10b981) Accent Headers */
    h1, h2, h3, h4 {
        color: #10b981 !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    
    /* Streamlit Slider Customization - Emerald Green (#10b981) Sliders */
    div[data-baseweb="slider"] div[role="slider"] {
        background-color: #10b981 !important;
        border-color: #10b981 !important;
    }
    div[data-baseweb="slider"] div {
        background-color: #10b981 !important;
    }
    div[data-baseweb="slider"] [data-testid="stTickBar"] {
        background-color: #10b981 !important;
    }
    
    /* Custom FM24 Card Containers */
    .fm-card {
        background-color: #1a1528;
        border: 1px solid rgba(16, 185, 129, 0.35);
        border-radius: 8px;
        padding: 18px;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
    }
    
    /* Metric badges */
    .fm-badge-green {
        background-color: rgba(16, 185, 129, 0.2);
        color: #10b981 !important;
        border: 1px solid #10b981;
        padding: 4px 10px;
        border-radius: 4px;
        font-weight: 700;
        font-size: 0.9rem;
    }
    
    .fm-badge-cyan {
        background-color: rgba(0, 229, 255, 0.15);
        color: #00e5ff !important;
        border: 1px solid #00e5ff;
        padding: 4px 10px;
        border-radius: 4px;
        font-weight: 700;
        font-size: 0.9rem;
    }

    /* Table & Dataframe styling - Dark background matching page with white text */
    div[data-testid="stDataFrame"], div[data-testid="stTable"] {
        background-color: #0b0813 !important;
        border: 1px solid rgba(16, 185, 129, 0.3) !important;
        border-radius: 6px !important;
    }
    
    div[data-testid="stDataFrame"] *, div[data-testid="stTable"] * {
        color: #ffffff !important;
    }

    .stDataFrame [role="gridcell"], .stDataFrame [role="columnheader"] {
        background-color: #0b0813 !important;
        color: #ffffff !important;
    }
    
    /* Selectbox and Multiselect dark styling */
    div[data-baseweb="select"] > div {
        background-color: #1a1528 !important;
        border-color: rgba(16, 185, 129, 0.4) !important;
        color: #ffffff !important;
    }
    
    /* Custom button styling */
    .stButton > button {
        background-color: #1a1528 !important;
        color: #ffffff !important;
        border: 1px solid #10b981 !important;
        border-radius: 6px !important;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background-color: #10b981 !important;
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# App Title & Header (Clean Tactical Style - No Emojis)
st.markdown("""
<div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 2px solid #10b981; padding-bottom: 10px; margin-bottom: 25px;">
    <div>
        <span class="fm-badge-green">FM24 DATA HUB V2.5</span>
        <h1 style="margin: 5px 0 0 0; font-size: 2.3rem;">DATA HUB // MLS ANALYTICS & RECRUITMENT</h1>
    </div>
    <div style="text-align: right;">
        <span class="fm-badge-cyan">LIVE API CONNECTED</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Initialize ASA client
@st.cache_resource
def get_asa_client():
    return AmericanSoccerAnalysis()

asa = get_asa_client()

# --- Caching Data Fetching Functions ---
@st.cache_data
def get_players():
    return asa.get_players(leagues="mls")

@st.cache_data
def get_player_salaries(season):
    return asa.get_player_salaries(leagues="mls", season_name=int(season))

@st.cache_data
def get_outfield_gplus(season):
    return asa.get_player_goals_added(leagues="mls", season_name=int(season))

@st.cache_data
def get_gk_gplus(season):
    return asa.get_goalkeeper_goals_added(leagues="mls", season_name=int(season))

@st.cache_data
def get_xgoals_season(season):
    return asa.get_player_xgoals(leagues="mls", season_name=int(season))

@st.cache_data
def get_gk_xgoals_season(season):
    return asa.get_goalkeeper_xgoals(leagues="mls", season_name=int(season))

@st.cache_data
def get_player_game_goals(season):
    outfield_games = asa.get_player_xgoals(leagues="mls", season_name=int(season), split_by_games=True)
    gk_games = asa.get_goalkeeper_xgoals(leagues="mls", season_name=int(season), split_by_games=True)
    
    df_pg = pd.concat([
        outfield_games[['player_id', 'game_id', 'team_id', 'minutes_played']],
        gk_games[['player_id', 'game_id', 'team_id', 'minutes_played']]
    ], ignore_index=True)
    
    df_pg = df_pg[df_pg['minutes_played'] > 0].copy()
    games_df = asa.get_games(leagues="mls", season_name=int(season))
    
    pg_merged = df_pg.merge(games_df[['game_id', 'home_team_id', 'away_team_id', 'home_score', 'away_score']], on='game_id', how='inner')
    
    pg_merged['goals_for'] = pg_merged.apply(lambda r: r['home_score'] if r['team_id'] == r['home_team_id'] else (r['away_score'] if r['team_id'] == r['away_team_id'] else 0), axis=1)
    pg_merged['goals_against'] = pg_merged.apply(lambda r: r['away_score'] if r['team_id'] == r['home_team_id'] else (r['home_score'] if r['team_id'] == r['away_team_id'] else 0), axis=1)
    
    player_stats = pg_merged.groupby('player_id').agg(
        total_minutes=('minutes_played', 'sum'),
        games_played=('game_id', 'nunique'),
        goals_for=('goals_for', 'sum'),
        goals_against=('goals_against', 'sum')
    ).reset_index()
    
    player_stats['goal_difference'] = player_stats['goals_for'] - player_stats['goals_against']
    return player_stats

@st.cache_data
def get_winger_passing_creation(season):
    xp_def = asa.get_player_xpass(leagues="mls", season_name=int(season), pass_origin_third="Defensive")
    xp_mid = asa.get_player_xpass(leagues="mls", season_name=int(season), pass_origin_third="Middle")
    xp_att = asa.get_player_xpass(leagues="mls", season_name=int(season), pass_origin_third="Attacking")
    xf = asa.get_player_xgoals(leagues="mls", season_name=int(season))
    
    wingers = xf[xf['general_position'] == 'W'].copy()
    
    merged = wingers.merge(xp_def[['player_id', 'attempted_passes']], on='player_id', how='left').rename(columns={'attempted_passes': 'def_passes'})
    merged = merged.merge(xp_mid[['player_id', 'attempted_passes']], on='player_id', how='left').rename(columns={'attempted_passes': 'mid_passes'})
    merged = merged.merge(xp_att[['player_id', 'attempted_passes']], on='player_id', how='left').rename(columns={'attempted_passes': 'att_third_passes'})
    
    merged['def_passes'] = merged['def_passes'].fillna(0)
    merged['mid_passes'] = merged['mid_passes'].fillna(0)
    merged['att_third_passes'] = merged['att_third_passes'].fillna(0)
    merged['total_passes_all_thirds'] = merged['def_passes'] + merged['mid_passes'] + merged['att_third_passes']
    
    merged['def_share_pct'] = (merged['def_passes'] / merged['total_passes_all_thirds'].replace(0, 1) * 100).round(1)
    merged['mid_share_pct'] = (merged['mid_passes'] / merged['total_passes_all_thirds'].replace(0, 1) * 100).round(1)
    merged['att_third_share'] = (merged['att_third_passes'] / merged['total_passes_all_thirds'].replace(0, 1)).clip(0, 1)
    merged['att_third_share_pct'] = (merged['att_third_share'] * 100).round(1)
    
    merged['est_att_key_passes'] = (merged['key_passes'] * merged['att_third_share']).round(1)
    merged['est_att_assists'] = (merged['primary_assists'] * merged['att_third_share']).round(1)
    
    return merged

# Helper function to draw Plotly FM24 Tactical Pitch
def draw_fm24_pitch_plotly(squad_df, formation_name="4-3-3"):
    fig = go.Figure()
    
    fig.add_shape(type="rect", x0=0, y0=0, x1=100, y1=130, fillcolor="#0a1d27", line=dict(color="#10b981", width=2), layer="below")
    fig.add_shape(type="line", x0=0, y0=65, x1=100, y1=65, line=dict(color="#10b981", width=1.5, dash="dash"), layer="below")
    fig.add_shape(type="circle", x0=38, y0=53, x1=62, y1=77, line=dict(color="#10b981", width=1.5), layer="below")
    fig.add_shape(type="rect", x0=25, y0=0, x1=75, y1=20, line=dict(color="#10b981", width=1.5), layer="below")
    fig.add_shape(type="rect", x0=25, y0=110, x1=75, y1=130, line=dict(color="#10b981", width=1.5), layer="below")
    
    coords_map = {
        "4-3-3": {
            "GK": [(50, 10)],
            "DF": [(18, 35), (39, 32), (61, 32), (82, 35)],
            "MF": [(25, 65), (50, 60), (75, 65)],
            "FW": [(20, 100), (50, 105), (80, 100)]
        },
        "4-4-2": {
            "GK": [(50, 10)],
            "DF": [(18, 35), (39, 32), (61, 32), (82, 35)],
            "MF": [(18, 65), (39, 65), (61, 65), (82, 65)],
            "FW": [(35, 105), (65, 105)]
        },
        "3-5-2": {
            "GK": [(50, 10)],
            "DF": [(25, 32), (50, 30), (75, 32)],
            "MF": [(15, 65), (32, 60), (50, 65), (68, 60), (85, 65)],
            "FW": [(35, 105), (65, 105)]
        },
        "5-3-2": {
            "GK": [(50, 10)],
            "DF": [(12, 35), (31, 30), (50, 28), (69, 30), (88, 35)],
            "MF": [(25, 65), (50, 60), (75, 65)],
            "FW": [(35, 105), (65, 105)]
        }
    }
    
    position_coords = coords_map.get(formation_name, coords_map["4-3-3"])
    pos_counts = {"GK": 0, "DF": 0, "MF": 0, "FW": 0}
    
    x_coords, y_coords, text_labels, hover_texts = [], [], [], []
    
    for _, row in squad_df.iterrows():
        pos = row['primary_broad_position']
        idx = pos_counts[pos]
        if idx < len(position_coords[pos]):
            x, y = position_coords[pos][idx]
            pos_counts[pos] += 1
            
            x_coords.append(x)
            y_coords.append(y)
            
            name_parts = row['player_name'].split()
            name = name_parts[-1] if name_parts else row['player_name']
            gplus = row['total_gplus']
            salary_k = row['guaranteed_compensation'] / 1000
            
            text_labels.append(f"<b>{name}</b><br>${salary_k:.0f}k | {gplus:.1f} g+")
            hover_texts.append(f"<b>{row['player_name']}</b><br>Position: {pos}<br>Salary: ${row['guaranteed_compensation']:,.0f}<br>Goals Added: {gplus:.2f}")

    fig.add_trace(go.Scatter(
        x=x_coords,
        y=y_coords,
        mode="markers+text",
        marker=dict(size=36, color="#10b981", line=dict(color="#ffffff", width=2)),
        text=text_labels,
        textposition="bottom center",
        textfont=dict(color="#ffffff", size=12, family="Rajdhani"),
        hoverinfo="text",
        hovertext=hover_texts
    ))
    
    fig.update_xaxes(visible=False, range=[-5, 105])
    fig.update_yaxes(visible=False, range=[-10, 140])
    fig.update_layout(
        margin=dict(l=0, r=0, t=30, b=0),
        paper_bgcolor="#120e1e",
        plot_bgcolor="#0a1d27",
        height=650,
        showlegend=False
    )
    return fig

# --- Navigation (Scouting & Rookie Hub set as FIRST DEFAULT PAGE!) ---
st.sidebar.markdown("<h2 style='color:#10b981;'>TACTICAL VIEWS</h2>", unsafe_allow_html=True)
app_mode = st.sidebar.radio("Select View:", ["Scouting & Rookie Hub", "Moneyball Roster Planner"], index=0)

# --- Dashboard 1: Scouting & Rookie Hub (DEFAULT FIRST PAGE) ---
if app_mode == "Scouting & Rookie Hub":
    st.markdown("## SCOUTING HUB // RECENT SIGNINGS")
    st.markdown("Comprehensive evaluation of under-23 rookies debuting in 2024–2025 across **Playtime**, **On-Pitch Goal Impact**, and **Attacking Winger Creation**.")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("<h3 style='color:#10b981;'>SCOUTING FILTERS</h3>", unsafe_allow_html=True)
    debut_years = st.sidebar.multiselect("Debut Seasons:", [2024, 2025], default=[2024, 2025])
    age_limit = st.sidebar.slider("Max Age at Debut:", 16, 23, 23)
    top_n = st.sidebar.slider("Top Players to Display:", 10, 50, 20)
    target_playtime_season = 2025
    
    if not debut_years:
        st.warning("Please select at least one debut season in the sidebar.")
    else:
        with st.spinner("Querying scouting database, game logs & winger creation metrics..."):
            players_df = get_players()
            
            def parse_seasons(val):
                if isinstance(val, list):
                    return [int(x) for x in val]
                elif isinstance(val, (int, float)):
                    return [int(val)]
                elif isinstance(val, str):
                    try:
                        return [int(val)]
                    except ValueError:
                        return []
                return []
            
            players_df['parsed_seasons'] = players_df['season_name'].apply(parse_seasons)
            players_df['min_season'] = players_df['parsed_seasons'].apply(lambda x: min(x) if x else None)
            
            players_df['birth_year'] = pd.to_datetime(players_df['birth_date'], errors='coerce').dt.year
            players_df['age_at_debut'] = (players_df['min_season'] - players_df['birth_year']).astype('Int64')
            players_df['age_in_2025'] = (2025 - players_df['birth_year']).astype('Int64')
            
            rookies = players_df[
                (players_df['min_season'].isin(debut_years)) & 
                (players_df['age_at_debut'] < age_limit)
            ].copy()
            
            # Fetch on-pitch goal differential & playtimes
            game_goals_df = get_player_game_goals(target_playtime_season)
            
            analysis_df = rookies.merge(game_goals_df, on='player_id', how='left')
            analysis_df['total_minutes'] = analysis_df['total_minutes'].fillna(0).astype(int)
            analysis_df['games_played'] = analysis_df['games_played'].fillna(0).astype(int)
            analysis_df['goals_for'] = analysis_df['goals_for'].fillna(0).astype(int)
            analysis_df['goals_against'] = analysis_df['goals_against'].fillna(0).astype(int)
            analysis_df['goal_difference'] = analysis_df['goal_difference'].fillna(0).astype(int)
            
            # Fetch winger creation data
            winger_creation_df = get_winger_passing_creation(target_playtime_season)
            
            winger_analysis_df = rookies.merge(winger_creation_df, on='player_id', how='inner')
            
        # Three Main Subsections using clean tabs
        section_tab1, section_tab2, section_tab3 = st.tabs([
            "PLAYTIME & MINUTES ANALYSIS",
            "ON-PITCH GOAL DIFFERENTIAL ANALYSIS",
            "ATTACKING CREATION & WINGER PROFILING"
        ])
        
        calc_height = max(500, top_n * 32)
        
        # --- SUBSECTION 1: PLAYTIME & MINUTES ANALYSIS ---
        with section_tab1:
            st.markdown("### SUBSECTION 1 // PLAYTIME & MINUTES PROFILE")
            df_mins_sorted = analysis_df.sort_values('total_minutes', ascending=False)
            top_mins_df = df_mins_sorted.head(top_n).copy()
            
            st.dataframe(
                top_mins_df[['player_name', 'min_season', 'age_at_debut', 'age_in_2025', 'total_minutes', 'games_played', 'primary_broad_position', 'nationality']].rename(columns={
                    'player_name': 'Name',
                    'min_season': 'Debut Year',
                    'age_at_debut': 'Age Signed',
                    'age_in_2025': '2025 Age',
                    'total_minutes': '2025 Mins',
                    'games_played': 'Games',
                    'primary_broad_position': 'Pos',
                    'nationality': 'Nation'
                }),
                width="stretch",
                hide_index=True
            )
            
            tab_m1, tab_m2, tab_m3 = st.tabs([
                "Playtime by Position",
                "Signing Cohorts & Age Profiles",
                "Interactive Distribution"
            ])
            
            with tab_m1:
                fig = px.bar(
                    top_mins_df,
                    x="total_minutes",
                    y="player_name",
                    color="primary_broad_position",
                    color_discrete_sequence=px.colors.qualitative.Set2,
                    orientation='h',
                    labels={'total_minutes': '2025 Minutes', 'player_name': 'Player', 'primary_broad_position': 'Pos'},
                    title=f"Top {top_n} Young Signings by 2025 Playtime (By Position)",
                    template="plotly_dark"
                )
                fig.update_layout(
                    yaxis=dict(categoryorder='total ascending', dtick=1),
                    height=calc_height,
                    paper_bgcolor='#120e1e',
                    plot_bgcolor='#0b0813',
                    font=dict(color='#ffffff', family="Rajdhani"),
                    title_font_color='#10b981'
                )
                st.plotly_chart(fig, width="stretch", config={'displayModeBar': True, 'displaylogo': False})
                
            with tab_m2:
                top_mins_df['min_season_str'] = top_mins_df['min_season'].astype(int).astype(str)
                top_mins_df['age_label'] = top_mins_df.apply(
                    lambda r: f"Signed: {int(r['min_season'])} (Age {int(r['age_at_debut'])}) | 2025 Age: {int(r['age_in_2025'])}", axis=1
                )
                
                fig = px.bar(
                    top_mins_df,
                    x="total_minutes",
                    y="player_name",
                    color="min_season_str",
                    color_discrete_map={'2024': '#10b981', '2025': '#00e5ff'},
                    orientation='h',
                    text="age_label",
                    labels={'total_minutes': '2025 Minutes', 'player_name': 'Player', 'min_season_str': 'Signing Cohort'},
                    title=f"Top {top_n} Young Signings: Cohorts & Age Details",
                    template="plotly_dark"
                )
                fig.update_traces(textposition="inside")
                fig.update_layout(
                    yaxis=dict(categoryorder='total ascending', dtick=1),
                    height=calc_height,
                    paper_bgcolor='#120e1e',
                    plot_bgcolor='#0b0813',
                    font=dict(color='#ffffff', family="Rajdhani"),
                    title_font_color='#10b981'
                )
                st.plotly_chart(fig, width="stretch", config={'displayModeBar': True, 'displaylogo': False})
                
            with tab_m3:
                df_plot = analysis_df[analysis_df['total_minutes'] > 0].copy()
                df_plot['min_season'] = df_plot['min_season'].astype(int).astype(str)
                df_plot['age_in_2025'] = df_plot['age_in_2025'].astype(int)
                df_plot['age_at_debut'] = df_plot['age_at_debut'].astype(int)
                
                fig = px.scatter(
                    df_plot,
                    x="age_in_2025",
                    y="total_minutes",
                    color="primary_broad_position",
                    symbol="min_season",
                    hover_name="player_name",
                    hover_data=["age_in_2025", "total_minutes", "min_season", "age_at_debut", "nationality"],
                    labels={
                        "age_in_2025": "Age in 2025",
                        "total_minutes": "Minutes Played",
                        "primary_broad_position": "Pos",
                        "min_season": "Signed Year",
                        "age_at_debut": "Signed Age",
                        "nationality": "Nation"
                    },
                    title="Playtime Distribution vs Age in 2025 (Interactive)",
                    template="plotly_dark"
                )
                fig.update_traces(marker=dict(size=12, line=dict(width=1, color='DarkSlateGrey')))
                fig.update_layout(
                    paper_bgcolor='#120e1e',
                    plot_bgcolor='#0b0813',
                    font=dict(color='#ffffff', family="Rajdhani"),
                    title_font_color='#10b981'
                )
                st.plotly_chart(fig, width="stretch", config={'displayModeBar': True, 'displaylogo': False})

        # --- SUBSECTION 2: ON-PITCH GOAL DIFFERENTIAL ANALYSIS ---
        with section_tab2:
            st.markdown("### SUBSECTION 2 // ON-PITCH GOAL DIFFERENTIAL")
            df_gd_sorted = analysis_df.sort_values('goal_difference', ascending=False)
            top_gd_df = df_gd_sorted.head(top_n).copy()
            
            st.dataframe(
                top_gd_df[['player_name', 'min_season', 'age_at_debut', 'age_in_2025', 'total_minutes', 'games_played', 'goals_for', 'goals_against', 'goal_difference', 'primary_broad_position', 'nationality']].rename(columns={
                    'player_name': 'Name',
                    'min_season': 'Debut Year',
                    'age_at_debut': 'Age Signed',
                    'age_in_2025': '2025 Age',
                    'total_minutes': '2025 Mins',
                    'games_played': 'Games',
                    'goals_for': 'Goals For (GF)',
                    'goals_against': 'Goals Against (GA)',
                    'goal_difference': 'Net (+/-)',
                    'primary_broad_position': 'Pos',
                    'nationality': 'Nation'
                }),
                width="stretch",
                hide_index=True
            )
            
            tab_g1, tab_g2 = st.tabs([
                "Net On-Pitch Goal Difference (+/-)",
                "Goals For vs. Goals Against Scatter"
            ])
            
            with tab_g1:
                top_gd_df['gd_color'] = top_gd_df['goal_difference'].apply(lambda x: 'Positive (+)' if x >= 0 else 'Negative (-)')
                
                fig = px.bar(
                    top_gd_df,
                    x="goal_difference",
                    y="player_name",
                    color="gd_color",
                    color_discrete_map={'Positive (+)': '#10b981', 'Negative (-)': '#ef4444'},
                    orientation='h',
                    text="goal_difference",
                    labels={'goal_difference': 'Net On-Pitch Goal Difference (+/-)', 'player_name': 'Player Name', 'gd_color': 'Status'},
                    title=f"Top {top_n} Young Signings: Net On-Pitch Goal Differential in 2025",
                    template="plotly_dark"
                )
                fig.update_traces(textposition="outside")
                fig.update_layout(
                    yaxis=dict(categoryorder='total ascending', dtick=1),
                    height=calc_height,
                    paper_bgcolor='#120e1e',
                    plot_bgcolor='#0b0813',
                    font=dict(color='#ffffff', family="Rajdhani"),
                    title_font_color='#10b981'
                )
                st.plotly_chart(fig, width="stretch", config={'displayModeBar': True, 'displaylogo': False})
                
            with tab_g2:
                df_scatter = analysis_df[analysis_df['total_minutes'] > 0].copy()
                df_scatter['min_season_str'] = df_scatter['min_season'].astype(int).astype(str)
                
                fig = px.scatter(
                    df_scatter,
                    x="goals_for",
                    y="goals_against",
                    color="primary_broad_position",
                    symbol="min_season_str",
                    hover_name="player_name",
                    hover_data=["age_in_2025", "total_minutes", "goals_for", "goals_against", "goal_difference", "nationality"],
                    labels={
                        "goals_for": "Goals Scored FOR Team While On Pitch (GF)",
                        "goals_against": "Goals Conceded AGAINST Team While On Pitch (GA)",
                        "primary_broad_position": "Pos",
                        "min_season_str": "Signed Year"
                    },
                    title="On-Pitch Goals For vs. Goals Against (Diagonal Line = Parity)",
                    template="plotly_dark"
                )
                max_val = max(df_scatter['goals_for'].max(), df_scatter['goals_against'].max()) + 5
                fig.add_shape(type="line", x0=0, y0=0, x1=max_val, y1=max_val, line=dict(color="#64748b", dash="dash"))
                
                fig.update_traces(marker=dict(size=12, line=dict(width=1, color='DarkSlateGrey')))
                fig.update_layout(
                    paper_bgcolor='#120e1e',
                    plot_bgcolor='#0b0813',
                    font=dict(color='#ffffff', family="Rajdhani"),
                    title_font_color='#10b981'
                )
                st.plotly_chart(fig, width="stretch", config={'displayModeBar': True, 'displaylogo': False})

        # --- SUBSECTION 3: ATTACKING CREATION & WINGER PROFILING ---
        with section_tab3:
            st.markdown("### SUBSECTION 3 // ATTACKING CREATION & WINGER PROFILING")
            st.markdown("Evaluates U23 wingers across **Attacking Third Pass Volume**, **Full 3-Third Territory Distribution**, and **Estimated Attacking 3rd Key Passes**.")
            
            winger_sorted = winger_analysis_df.sort_values('est_att_key_passes', ascending=False)
            top_winger_df = winger_sorted.head(top_n).copy()
            
            # Solution 3: Transparent Data Table (With Def, Mid, Att % breakdown)
            st.dataframe(
                top_winger_df[[
                    'player_name', 'min_season', 'age_at_debut', 'age_in_2025', 'minutes_played', 
                    'total_passes_all_thirds', 'def_passes', 'mid_passes', 'att_third_passes', 
                    'def_share_pct', 'mid_share_pct', 'att_third_share_pct', 
                    'key_passes', 'est_att_key_passes', 'primary_assists', 'est_att_assists', 'xassists', 'nationality'
                ]].rename(columns={
                    'player_name': 'Name',
                    'min_season': 'Debut Year',
                    'age_at_debut': 'Age Signed',
                    'age_in_2025': '2025 Age',
                    'minutes_played': 'Mins',
                    'total_passes_all_thirds': 'Total Passes',
                    'def_passes': 'Def 3rd Passes',
                    'mid_passes': 'Mid 3rd Passes',
                    'att_third_passes': 'Att 3rd Passes',
                    'def_share_pct': 'Def %',
                    'mid_share_pct': 'Mid %',
                    'att_third_share_pct': 'Att %',
                    'key_passes': 'Total Key Passes',
                    'est_att_key_passes': 'Est Att Key Passes',
                    'primary_assists': 'Total Assists',
                    'est_att_assists': 'Est Att Assists',
                    'xassists': 'xAssists (xA)',
                    'nationality': 'Nation'
                }),
                width="stretch",
                hide_index=True
            )
            
            tab_w1, tab_w2, tab_w3 = st.tabs([
                "Full 3-Third Territory Stacked Profile",
                "Est. Attacking 3rd Key Passes Ranking",
                "Attacking 3rd Share vs Chance Creation Scatter"
            ])
            
            # Tab 1: Full 3-Third Territory Breakdown (Sorted by Attacking 3rd Share % Descending!)
            with tab_w1:
                top_att_share_df = winger_analysis_df.sort_values('att_third_share_pct', ascending=True).tail(top_n).copy()
                
                df_stacked_list = []
                for _, row in top_att_share_df.iterrows():
                    df_stacked_list.append({'Player': row['player_name'], 'Third': 'Attacking Third', 'Percentage': row['att_third_share_pct'], 'Passes': row['att_third_passes']})
                    df_stacked_list.append({'Player': row['player_name'], 'Third': 'Middle Third', 'Percentage': row['mid_share_pct'], 'Passes': row['mid_passes']})
                    df_stacked_list.append({'Player': row['player_name'], 'Third': 'Defensive Third', 'Percentage': row['def_share_pct'], 'Passes': row['def_passes']})
                
                df_stacked = pd.DataFrame(df_stacked_list)
                
                fig = px.bar(
                    df_stacked,
                    x="Percentage",
                    y="Player",
                    color="Third",
                    color_discrete_map={
                        'Attacking Third': '#10b981',
                        'Middle Third': '#00e5ff',
                        'Defensive Third': '#475569'
                    },
                    orientation='h',
                    hover_data=["Passes"],
                    labels={'Percentage': 'Pass Territory Share (%)', 'Player': 'Player Name', 'Third': 'Field Zone'},
                    title="Winger Territory Profile: Full 3-Third Pass Distribution (%) (Sorted by Attacking 3rd Share %)",
                    template="plotly_dark"
                )
                fig.update_layout(
                    barmode="stack",
                    height=max(450, len(top_att_share_df) * 32),
                    paper_bgcolor='#120e1e',
                    plot_bgcolor='#0b0813',
                    font=dict(color='#ffffff', family="Rajdhani"),
                    title_font_color='#10b981'
                )
                st.plotly_chart(fig, width="stretch", config={'displayModeBar': True, 'displaylogo': False})
                
            # Tab 2: Single clean metric & solid Emerald Green color (#10b981) - Sorted by Est Att Key Passes!
            with tab_w2:
                top_key_df = winger_analysis_df.sort_values('est_att_key_passes', ascending=True).tail(top_n).copy()
                fig = px.bar(
                    top_key_df,
                    x="est_att_key_passes",
                    y="player_name",
                    orientation='h',
                    text="est_att_key_passes",
                    color_discrete_sequence=['#10b981'],
                    labels={
                        'est_att_key_passes': 'Estimated Count of Key Passes from Attacking 3rd', 
                        'player_name': 'Player Name'
                    },
                    title=f"Top U23 Wingers by Estimated Key Passes from Attacking 3rd (Ranked Highest to Lowest)",
                    template="plotly_dark"
                )
                fig.update_traces(textposition="outside", texttemplate="%{text:.1f}")
                fig.update_layout(
                    height=max(450, len(top_key_df) * 32),
                    paper_bgcolor='#120e1e',
                    plot_bgcolor='#0b0813',
                    font=dict(color='#ffffff', family="Rajdhani"),
                    title_font_color='#10b981'
                )
                st.plotly_chart(fig, width="stretch", config={'displayModeBar': True, 'displaylogo': False})
                
            with tab_w3:
                fig = px.scatter(
                    winger_analysis_df[winger_analysis_df['minutes_played'] > 200],
                    x="att_third_share_pct",
                    y="est_att_key_passes",
                    size="xassists",
                    color="primary_assists",
                    color_continuous_scale="Viridis",
                    hover_name="player_name",
                    hover_data=["age_in_2025", "minutes_played", "att_third_passes", "key_passes", "est_att_key_passes", "primary_assists", "xassists"],
                    labels={
                        "att_third_share_pct": "Attacking 3rd Pass Share (%)",
                        "est_att_key_passes": "Estimated Attacking 3rd Key Passes",
                        "primary_assists": "Direct Assists",
                        "xassists": "Expected Assists (xA)"
                    },
                    title="Winger Profiling: Attacking 3rd Share % vs. Estimated Attacking 3rd Key Passes",
                    template="plotly_dark"
                )
                fig.update_traces(marker=dict(line=dict(width=1, color='White')))
                fig.update_layout(
                    paper_bgcolor='#120e1e',
                    plot_bgcolor='#0b0813',
                    font=dict(color='#ffffff', family="Rajdhani"),
                    title_font_color='#10b981'
                )
                st.plotly_chart(fig, width="stretch", config={'displayModeBar': True, 'displaylogo': False})

# --- Dashboard 2: MLS Moneyball Optimizer ---
elif app_mode == "Moneyball Roster Planner":
    st.markdown("## TACTICAL PLANNER // MONEYBALL OPTIMIZER")
    st.markdown("Construct an optimal cap-compliant XI maximizing **Goals Added (g+)**.")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("<h3 style='color:#10b981;'>ROSTER CONSTRAINTS</h3>", unsafe_allow_html=True)
    opt_season = st.sidebar.selectbox("Target Season:", [2024, 2023], index=0)
    budget = st.sidebar.slider("Salary Cap Budget ($ USD):", 1_000_000, 15_000_000, 5_000_000, step=250_000)
    formation_name = st.sidebar.selectbox("Tactical Formation:", ["4-3-3", "4-4-2", "3-5-2", "5-3-2"], index=0)
    
    formation_mapping = {
        "4-3-3": {"GK": 1, "DF": 4, "MF": 3, "FW": 3},
        "4-4-2": {"GK": 1, "DF": 4, "MF": 4, "FW": 2},
        "3-5-2": {"GK": 1, "DF": 3, "MF": 5, "FW": 2},
        "5-3-2": {"GK": 1, "DF": 5, "MF": 3, "FW": 2}
    }
    formation = formation_mapping[formation_name]
    
    with st.spinner("Analyzing player database..."):
        players_df = get_players()
        salaries_df = get_player_salaries(opt_season)
        outfield_gplus = get_outfield_gplus(opt_season)
        gk_gplus = get_gk_gplus(opt_season)
        
        clean_salaries = salaries_df.sort_values("mlspa_release").groupby("player_id").last().reset_index()
        clean_players = players_df.drop_duplicates(subset=["player_id"])
        
        gk_gplus_copy = gk_gplus.copy()
        gk_gplus_copy['general_position'] = 'GK'
        all_gplus = pd.concat([outfield_gplus, gk_gplus_copy], ignore_index=True)
        
        all_gplus['total_gplus'] = all_gplus['data'].apply(lambda x: sum(item['goals_added_raw'] for item in x))
        
        merged = all_gplus.merge(clean_players, on="player_id", how="left")
        merged = merged.merge(clean_salaries[["player_id", "base_salary", "guaranteed_compensation"]], on="player_id", how="inner")
        
        df_clean = merged.dropna(subset=["primary_broad_position", "guaranteed_compensation", "total_gplus"])
        df_clean = df_clean[df_clean['minutes_played'] >= 450].copy()
        
    prob = pulp.LpProblem("MLS_Moneyball_XI", pulp.LpMaximize)
    indices = df_clean.index.tolist()
    x = pulp.LpVariable.dicts("player", indices, cat="Binary")
    
    prob += pulp.lpSum(df_clean.loc[i, "total_gplus"] * x[i] for i in indices)
    prob += pulp.lpSum(df_clean.loc[i, "guaranteed_compensation"] * x[i] for i in indices) <= budget
    prob += pulp.lpSum(x[i] for i in indices) == 11
    
    for pos, count in formation.items():
        prob += pulp.lpSum(x[i] for i in indices if df_clean.loc[i, "primary_broad_position"] == pos) == count
        
    status = prob.solve(pulp.PULP_CBC_CMD(msg=False))
    
    if status == pulp.LpStatusOptimal:
        selected_indices = [i for i in indices if x[i].varValue == 1]
        squad = df_clean.loc[selected_indices].copy()
        
        total_cost = squad['guaranteed_compensation'].sum()
        total_gplus = squad['total_gplus'].sum()
        avg_cost = total_cost / 11
        league_avg = df_clean['guaranteed_compensation'].mean()
        
        mcol1, mcol2, mcol3, mcol4 = st.columns(4)
        mcol1.markdown(f"""
        <div class="fm-card">
            <span class="fm-badge-green">TOTAL PAYROLL</span>
            <h2 style="margin: 10px 0 0 0; color: #ffffff !important;">${total_cost:,.0f}</h2>
            <span style="color:#ffffff; font-size:0.9rem;">{((total_cost/budget)*100):.1f}% of ${budget/1e6:.1f}M Cap</span>
        </div>
        """, unsafe_allow_html=True)
        
        mcol2.markdown(f"""
        <div class="fm-card">
            <span class="fm-badge-green">TOTAL GOALS ADDED</span>
            <h2 style="margin: 10px 0 0 0; color: #ffffff !important;">{total_gplus:.2f} g+</h2>
            <span style="color:#ffffff; font-size:0.9rem;">Combined Squad Impact</span>
        </div>
        """, unsafe_allow_html=True)
        
        mcol3.markdown(f"""
        <div class="fm-card">
            <span class="fm-badge-cyan">SQUAD AVG SALARY</span>
            <h2 style="margin: 10px 0 0 0; color: #ffffff !important;">${avg_cost:,.0f}</h2>
            <span style="color:#ffffff; font-size:0.9rem;">Per Starter</span>
        </div>
        """, unsafe_allow_html=True)
        
        mcol4.markdown(f"""
        <div class="fm-card">
            <span class="fm-badge-cyan">LEAGUE AVG SALARY</span>
            <h2 style="margin: 10px 0 0 0; color: #ffffff !important;">${league_avg:,.0f}</h2>
            <span style="color:#ffffff; font-size:0.9rem;">Full League Baseline</span>
        </div>
        """, unsafe_allow_html=True)
        
        col_pitch, col_details = st.columns([1.1, 1])
        
        with col_pitch:
            st.markdown("### TACTICAL FORMATION PITCH")
            pitch_fig = draw_fm24_pitch_plotly(squad, formation_name)
            st.plotly_chart(pitch_fig, width="stretch", config={'displayModeBar': True, 'displaylogo': False})
            
        with col_details:
            st.markdown("### ROSTER // STARTING XI DETAILS")
            display_cols = ["player_name", "primary_broad_position", "minutes_played", "guaranteed_compensation", "total_gplus"]
            st.dataframe(
                squad[display_cols].rename(columns={
                    "player_name": "Name",
                    "primary_broad_position": "Pos",
                    "minutes_played": "Mins",
                    "guaranteed_compensation": "Salary ($)",
                    "total_gplus": "Goals Added (g+)"
                }).sort_values("Pos"),
                width="stretch",
                hide_index=True
            )
            
            st.markdown("### ANALYSIS // VALUE MATRIX")
            df_clean['is_selected'] = df_clean.index.isin(selected_indices)
            df_clean['selected_label'] = df_clean['is_selected'].map({True: 'Starting XI', False: 'Other MLS Players'})
            
            fig = px.scatter(
                df_clean,
                x="guaranteed_compensation",
                y="total_gplus",
                color="selected_label",
                symbol="selected_label",
                color_discrete_map={'Starting XI': '#10b981', 'Other MLS Players': '#475569'},
                hover_name="player_name",
                hover_data=["primary_broad_position", "guaranteed_compensation", "total_gplus"],
                labels={
                    "guaranteed_compensation": "Guaranteed Compensation ($ - Log Scale)",
                    "total_gplus": "Goals Added (g+)",
                    "selected_label": "Status"
                },
                log_x=True,
                title="Goals Added vs Salary (Log Scale)",
                template="plotly_dark"
            )
            fig.update_layout(
                paper_bgcolor='#120e1e',
                plot_bgcolor='#0b0813',
                font=dict(color='#ffffff', family="Rajdhani"),
                title_font_color='#10b981'
            )
            st.plotly_chart(fig, width="stretch", config={'displayModeBar': True, 'displaylogo': False})
