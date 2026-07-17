import streamlit as st
import pandas as pd
from itscalledsoccer.client import AmericanSoccerAnalysis
import pulp
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

# Set page config
st.set_page_config(
    page_title="MLS Data Analytics & Optimization",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# App Title & Header
st.title("⚽ MLS Player Analytics & Optimization")
st.markdown("Interactive dashboards for roster building and rookie playtime tracking.")

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

# --- Navigation ---
st.sidebar.title("Navigation")
app_mode = st.sidebar.radio("Choose Dashboard:", ["MLS Moneyball Optimizer", "Young Rookie Playtime Analysis"])

# --- Dashboard 1: MLS Moneyball Optimizer ---
if app_mode == "MLS Moneyball Optimizer":
    st.header("💵 MLS 'Moneyball' Salary Cap Optimizer")
    st.markdown(
        "Build the highest-performing starting XI (maximizing Goals Added - `g+`) that fits under a strict salary cap."
    )
    
    # Sidebar controls for Optimizer
    st.sidebar.markdown("---")
    st.sidebar.subheader("Optimizer Settings")
    opt_season = st.sidebar.selectbox("Season:", [2024, 2023], index=0)
    budget = st.sidebar.slider("Roster Budget Cap ($ USD):", 1_000_000, 15_000_000, 5_000_000, step=250_000)
    
    formation_name = st.sidebar.selectbox("Formation:", ["4-3-3", "4-4-2", "3-5-2", "5-3-2"], index=0)
    
    formation_mapping = {
        "4-3-3": {"GK": 1, "DF": 4, "MF": 3, "FW": 3},
        "4-4-2": {"GK": 1, "DF": 4, "MF": 4, "FW": 2},
        "3-5-2": {"GK": 1, "DF": 3, "MF": 5, "FW": 2},
        "5-3-2": {"GK": 1, "DF": 5, "MF": 3, "FW": 2}
    }
    formation = formation_mapping[formation_name]
    
    # Load and process data
    with st.spinner("Fetching and processing data..."):
        players_df = get_players()
        salaries_df = get_player_salaries(opt_season)
        outfield_gplus = get_outfield_gplus(opt_season)
        gk_gplus = get_gk_gplus(opt_season)
        
        # Process salaries
        clean_salaries = salaries_df.sort_values("mlspa_release").groupby("player_id").last().reset_index()
        # Deduplicate players
        clean_players = players_df.drop_duplicates(subset=["player_id"])
        
        # Concat GK and outfield gplus
        gk_gplus_copy = gk_gplus.copy()
        gk_gplus_copy['general_position'] = 'GK'
        all_gplus = pd.concat([outfield_gplus, gk_gplus_copy], ignore_index=True)
        
        # Sum total goals added raw
        all_gplus['total_gplus'] = all_gplus['data'].apply(lambda x: sum(item['goals_added_raw'] for item in x))
        
        # Merge
        merged = all_gplus.merge(clean_players, on="player_id", how="left")
        merged = merged.merge(clean_salaries[["player_id", "base_salary", "guaranteed_compensation"]], on="player_id", how="inner")
        
        # Clean NaNs and filter by playtime (> 450 minutes)
        df_clean = merged.dropna(subset=["primary_broad_position", "guaranteed_compensation", "total_gplus"])
        df_clean = df_clean[df_clean['minutes_played'] >= 450].copy()
        
    # Set up PuLP Optimization
    prob = pulp.LpProblem("MLS_Moneyball_XI", pulp.LpMaximize)
    indices = df_clean.index.tolist()
    x = pulp.LpVariable.dicts("player", indices, cat="Binary")
    
    # Objective
    prob += pulp.lpSum(df_clean.loc[i, "total_gplus"] * x[i] for i in indices)
    
    # Constraints
    prob += pulp.lpSum(df_clean.loc[i, "guaranteed_compensation"] * x[i] for i in indices) <= budget
    prob += pulp.lpSum(x[i] for i in indices) == 11
    
    for pos, count in formation.items():
        prob += pulp.lpSum(x[i] for i in indices if df_clean.loc[i, "primary_broad_position"] == pos) == count
        
    # Solve
    status = prob.solve(pulp.PULP_CBC_CMD(msg=False))
    
    if status == pulp.LpStatusOptimal:
        selected_indices = [i for i in indices if x[i].varValue == 1]
        squad = df_clean.loc[selected_indices].copy()
        
        # Metrics Display
        col1, col2, col3, col4 = st.columns(4)
        total_cost = squad['guaranteed_compensation'].sum()
        total_gplus = squad['total_gplus'].sum()
        avg_cost = total_cost / 11
        league_avg = df_clean['guaranteed_compensation'].mean()
        
        col1.metric("Total Squad Cost", f"${total_cost:,.0f}", f"{((total_cost/budget - 1) * 100):.1f}% of Cap")
        col2.metric("Total Goals Added (g+)", f"{total_gplus:.2f}")
        col3.metric("Avg Player Salary", f"${avg_cost:,.0f}")
        col4.metric("League Avg Salary", f"${league_avg:,.0f}")
        
        st.markdown("### 📋 Optimized Starting XI")
        display_cols = ["player_name", "primary_broad_position", "minutes_played", "guaranteed_compensation", "total_gplus"]
        st.dataframe(
            squad[display_cols].rename(columns={
                "player_name": "Name",
                "primary_broad_position": "Position",
                "minutes_played": "Minutes",
                "guaranteed_compensation": "Salary ($)",
                "total_gplus": "Goals Added (g+)"
            }).sort_values("Position"),
            use_container_width=True,
            hide_index=True
        )
        
        # Interactive Scatter Plot
        st.markdown("### 📈 Squad on League Landscape")
        df_clean['is_selected'] = df_clean.index.isin(selected_indices)
        df_clean['selected_label'] = df_clean['is_selected'].map({True: 'Starting XI', False: 'Other MLS Players'})
        
        fig = px.scatter(
            df_clean,
            x="guaranteed_compensation",
            y="total_gplus",
            color="selected_label",
            symbol="selected_label",
            color_discrete_map={'Starting XI': '#E74C3C', 'Other MLS Players': '#BDC3C7'},
            hover_name="player_name",
            hover_data=["primary_broad_position", "guaranteed_compensation", "total_gplus"],
            labels={
                "guaranteed_compensation": "Guaranteed Compensation ($ USD - Log Scale)",
                "total_gplus": "Total Goals Added (g+)",
                "selected_label": "Player Status"
            },
            log_x=True,
            title="Goals Added vs. Guaranteed Compensation (Selected Squad Highlighted)"
        )
        fig.update_traces(marker=dict(size=10, line=dict(width=1, color='DarkSlateGrey')))
        fig.update_layout(template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("No optimal solution could be found. Try raising the budget or changing the formation.")

# --- Dashboard 2: Young Rookie Playtime Analysis ---
elif app_mode == "Young Rookie Playtime Analysis":
    st.header("📈 Young Rookie & Signing Playtime Analysis")
    st.markdown(
        "Track young signings and rookies (under 23 at debut) and see how many minutes they logged during the **2025 season**."
    )
    
    # Sidebar controls for Rookie analysis
    st.sidebar.markdown("---")
    st.sidebar.subheader("Analysis Settings")
    debut_years = st.sidebar.multiselect("Debut Seasons (Signed In):", [2024, 2025], default=[2024, 2025])
    age_limit = st.sidebar.slider("Age Limit at Debut:", 16, 23, 23)
    target_playtime_season = 2025
    
    if not debut_years:
        st.warning("Please select at least one debut season in the sidebar.")
    else:
        # Load and process data
        with st.spinner("Fetching and processing rookie data..."):
            players_df = get_players()
            
            # Helper function to parse seasons list
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
            
            # Filter rookies
            rookies = players_df[
                (players_df['min_season'].isin(debut_years)) & 
                (players_df['age_at_debut'] < age_limit)
            ].copy()
            
            # Load 2025 playtime
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
            
            # Merge
            analysis_df = rookies.merge(total_minutes, on='player_id', how='left')
            analysis_df['minutes_played'] = analysis_df['minutes_played'].fillna(0).astype(int)
            analysis_df = analysis_df.sort_values('minutes_played', ascending=False)
            
        st.subheader(f"📊 Rookie Rankings: Playtime in {target_playtime_season} Season")
        
        # Display Top Rookies
        top_n = st.slider("Number of players to show in charts:", 10, 50, 20)
        top_df = analysis_df.head(top_n).copy()
        
        st.dataframe(
            top_df[['player_name', 'min_season', 'age_at_debut', 'age_in_2025', 'minutes_played', 'primary_broad_position', 'nationality']].rename(columns={
                'player_name': 'Name',
                'min_season': 'Debut Season',
                'age_at_debut': 'Age when Signed',
                'age_in_2025': 'Age in 2025',
                'minutes_played': '2025 Minutes',
                'primary_broad_position': 'Position',
                'nationality': 'Nationality'
            }),
            use_container_width=True,
            hide_index=True
        )
        
        # Tabs for different visualizations
        tab1, tab2, tab3 = st.tabs(["Playtime by Position", "Signing Cohorts & Age Details", "Interactive Distribution"])
        
        with tab1:
            st.markdown("### Playtime by Position")
            fig = px.bar(
                top_df,
                x="minutes_played",
                y="player_name",
                color="primary_broad_position",
                color_discrete_sequence=px.colors.qualitative.Set2,
                orientation='h',
                labels={'minutes_played': '2025 Minutes Played', 'player_name': 'Player Name', 'primary_broad_position': 'Position'},
                title=f"Top {top_n} Young Rookies by 2025 Playtime (By Position)"
            )
            fig.update_layout(yaxis={'categoryorder': 'total ascending'}, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
            
        with tab2:
            st.markdown("### Signing Cohort & Age Profile")
            top_df['min_season_str'] = top_df['min_season'].astype(int).astype(str)
            top_df['age_label'] = top_df.apply(
                lambda r: f"Signed: {int(r['min_season'])} (Age {int(r['age_at_debut'])}) | 2025 Age: {int(r['age_in_2025'])}", axis=1
            )
            
            fig = px.bar(
                top_df,
                x="minutes_played",
                y="player_name",
                color="min_season_str",
                color_discrete_map={'2024': '#1f77b4', '2025': '#ff7f0e'},
                orientation='h',
                text="age_label",
                labels={'minutes_played': '2025 Minutes Played', 'player_name': 'Player Name', 'min_season_str': 'Signing Cohort'},
                title=f"Top {top_n} Young Rookies: Signing Cohorts & Age Details"
            )
            fig.update_traces(textposition="inside")
            fig.update_layout(yaxis={'categoryorder': 'total ascending'}, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
            
        with tab3:
            st.markdown("### Playtime Distribution vs Age in 2025")
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
                    "age_in_2025": "Age in 2025 Season",
                    "minutes_played": "Minutes Played in 2025",
                    "primary_broad_position": "Position",
                    "min_season": "Signing Year",
                    "age_at_debut": "Age when Signed",
                    "nationality": "Nationality"
                },
                title="Rookie Distribution: 2025 Minutes Played vs. Age in 2025 (Interactive)"
            )
            fig.update_traces(marker=dict(size=12, line=dict(width=1, color='DarkSlateGrey')))
            fig.update_layout(template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
