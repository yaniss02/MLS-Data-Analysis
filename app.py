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

# Helper function to draw Plotly FM24 Tactical Pitch (Clean typography, no emojis)
def draw_fm24_pitch_plotly(squad_df, formation_name="4-3-3"):
    fig = go.Figure()
    
    # 1. Pitch Background & Lines with layer="below" so shapes stay in background!
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

# --- Navigation ---
st.sidebar.markdown("<h2 style='color:#10b981;'>TACTICAL VIEWS</h2>", unsafe_allow_html=True)
app_mode = st.sidebar.radio("Select View:", ["Moneyball Roster Planner", "Scouting & Rookie Hub"])

# --- Dashboard 1: MLS Moneyball Optimizer ---
if app_mode == "Moneyball Roster Planner":
    st.markdown("## TACTICAL PLANNER // MONEYBALL OPTIMIZER")
    st.markdown("Construct an optimal cap-compliant XI maximizing **Goals Added (g+)**.")
    
    # Sidebar controls
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
    
    # Load and process data
    with st.spinner("Analyzing player database..."):
        players_df = get_players()
        salaries_df = get_player_salaries(opt_season)
        outfield_gplus = get_outfield_gplus(opt_season)
        gk_gplus = get_gk_gplus(opt_season)
        
        # Process salaries
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
        
    # Solve PuLP ILP
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
        
        # Metrics Display (FM24 Cards with White Text)
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
        
        # Two Column Layout: Tactical Pitch on Left, Data Table / Scatter on Right
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
            
            # FM24 Dark Theme Scatter Plot (With styled ModeBar options)
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

# --- Dashboard 2: Scouting & Rookie Hub ---
elif app_mode == "Scouting & Rookie Hub":
    st.markdown("## SCOUTING HUB // RECENT SIGNINGS")
    st.markdown("Track young players (under 23 at debut) and rank them by their **2025 minutes played**.")
    
    # Sidebar controls
    st.sidebar.markdown("---")
    st.sidebar.markdown("<h3 style='color:#10b981;'>SCOUTING FILTERS</h3>", unsafe_allow_html=True)
    debut_years = st.sidebar.multiselect("Debut Seasons:", [2024, 2025], default=[2024, 2025])
    age_limit = st.sidebar.slider("Max Age at Debut:", 16, 23, 23)
    target_playtime_season = 2025
    
    if not debut_years:
        st.warning("Please select at least one debut season in the sidebar.")
    else:
        with st.spinner("Querying scouting database..."):
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
            
            minutes_list = []
            try:
                xf = get_xgoals_season(target_playtime_season)
                minutes_list.append(xf[['player_id', 'minutes_played']])
            except:
                pass
            try:
                xgk = get_gk_xgoals_season(target_playtime_season)
                minutes_list.append(xgk[['player_id', 'minutes_played']])
            except:
                pass
                
            df_minutes = pd.concat(minutes_list, ignore_index=True)
            total_minutes = df_minutes.groupby('player_id')['minutes_played'].sum().reset_index()
            
            analysis_df = rookies.merge(total_minutes, on='player_id', how='left')
            analysis_df['minutes_played'] = analysis_df['minutes_played'].fillna(0).astype(int)
            analysis_df = analysis_df.sort_values('minutes_played', ascending=False)
            
        top_n = st.sidebar.slider("Top Players to Display:", 10, 50, 20)
        top_df = analysis_df.head(top_n).copy()
        
        # Table
        st.dataframe(
            top_df[['player_name', 'min_season', 'age_at_debut', 'age_in_2025', 'minutes_played', 'primary_broad_position', 'nationality']].rename(columns={
                'player_name': 'Name',
                'min_season': 'Debut Year',
                'age_at_debut': 'Age Signed',
                'age_in_2025': '2025 Age',
                'minutes_played': '2025 Minutes',
                'primary_broad_position': 'Pos',
                'nationality': 'Nation'
            }),
            width="stretch",
            hide_index=True
        )
        
        # Tabs for Plots
        tab1, tab2, tab3 = st.tabs(["Playtime by Position", "Signing Cohorts & Age Profiles", "Interactive Distribution"])
        
        with tab1:
            fig = px.bar(
                top_df,
                x="minutes_played",
                y="player_name",
                color="primary_broad_position",
                color_discrete_sequence=px.colors.qualitative.Set2,
                orientation='h',
                labels={'minutes_played': '2025 Minutes', 'player_name': 'Player', 'primary_broad_position': 'Pos'},
                title=f"Top {top_n} Young Signings by 2025 Playtime (By Position)",
                template="plotly_dark"
            )
            fig.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                paper_bgcolor='#120e1e',
                plot_bgcolor='#0b0813',
                font=dict(color='#ffffff', family="Rajdhani"),
                title_font_color='#10b981'
            )
            st.plotly_chart(fig, width="stretch", config={'displayModeBar': True, 'displaylogo': False})
            
        with tab2:
            top_df['min_season_str'] = top_df['min_season'].astype(int).astype(str)
            top_df['age_label'] = top_df.apply(
                lambda r: f"Signed: {int(r['min_season'])} (Age {int(r['age_at_debut'])}) | 2025 Age: {int(r['age_in_2025'])}", axis=1
            )
            
            fig = px.bar(
                top_df,
                x="minutes_played",
                y="player_name",
                color="min_season_str",
                color_discrete_map={'2024': '#10b981', '2025': '#00e5ff'},
                orientation='h',
                text="age_label",
                labels={'minutes_played': '2025 Minutes', 'player_name': 'Player', 'min_season_str': 'Signing Cohort'},
                title=f"Top {top_n} Young Signings: Cohorts & Age Details",
                template="plotly_dark"
            )
            fig.update_traces(textposition="inside")
            fig.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                paper_bgcolor='#120e1e',
                plot_bgcolor='#0b0813',
                font=dict(color='#ffffff', family="Rajdhani"),
                title_font_color='#10b981'
            )
            st.plotly_chart(fig, width="stretch", config={'displayModeBar': True, 'displaylogo': False})
            
        with tab3:
            df_plot = analysis_df[analysis_df['minutes_played'] > 0].copy()
            df_plot['min_season'] = df_plot['min_season'].astype(int).astype(str)
            df_plot['age_in_2025'] = df_plot['age_in_2025'].astype(int)
            df_plot['age_at_debut'] = df_plot['age_at_debut'].astype(int)
            
            fig = px.scatter(
                df_plot,
                x="age_in_2025",
                y="minutes_played",
                color="primary_broad_position",
                symbol="min_season",
                hover_name="player_name",
                hover_data=["age_in_2025", "minutes_played", "min_season", "age_at_debut", "nationality"],
                labels={
                    "age_in_2025": "Age in 2025",
                    "minutes_played": "Minutes Played",
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
