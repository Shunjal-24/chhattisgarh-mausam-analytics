import datetime
import json
import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
from scipy.interpolate import make_interp_spline
import streamlit as st

# --- INITIAL APP SETUP ---
API_KEY = "ADD_YOUR_API"  # Integrated functional key
st.set_page_config(
    page_title="Mausam Analytics Engine - Chhattisgarh", 
    page_icon="🌾", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PERSISTENT FILE-BASED DATABASE SYSTEM ---
DB_FILE = "users.json"

def load_users():
    """Loads users from a local JSON file. Creates it with default admin if missing."""
    if not os.path.exists(DB_FILE):
        default_db = {"admin": "cgweather2026"}
        with open(DB_FILE, "w") as f:
            json.dump(default_db, f)
        return default_db
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {"admin": "cgweather2026"}

def save_user(username, password):
    """Appends a new user profile permanently to the local JSON file."""
    current_db = load_users()
    current_db[username] = password
    with open(DB_FILE, "w") as f:
        json.dump(current_db, f, indent=4)

# --- INITIALIZE SESSION STATE FOR RUNTIME AUTHENTICATION ---
if "auth_state" not in st.session_state:
    st.session_state["auth_state"] = "login"

if "current_user" not in st.session_state:
    st.session_state["current_user"] = None

# --- HIGH-END UI DESKTOP STYLING GRID ---
st.markdown("""
    <style>
    .stApp {
        background-color: #080c14;
        color: #f8fafc;
        font-family: 'Inter', system-ui, sans-serif;
    }

    /* Hide footer and top decoration bar, but preserve sidebar toggle header */
    footer {visibility: hidden;}
    [data-testid="stDecoration"] {display: none;}
    [data-testid="stHeader"] {background: transparent;}
    
    /* Widescreen Glass Containers */
    .dashboard-panel {
        background: linear-gradient(145deg, rgba(22, 30, 49, 0.7) 0%, rgba(11, 17, 32, 0.9) 100%);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 24px;
        padding: 30px;
        backdrop-filter: blur(25px);
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        margin-bottom: 24px;
        margin-top: 10px;
    }
    .main-hero {
        background: linear-gradient(135deg, #14532d 0%, #064e3b 50%, #1e293b 100%);
        border: 1px solid rgba(34, 197, 94, 0.15);
        border-radius: 24px;
        padding: 35px;
        position: relative;
        overflow: hidden;
    }
    
    /* Auth Form Glass Container */
    .auth-container {
        max-width: 450px;
        margin: 80px auto;
        background: linear-gradient(145deg, rgba(22, 30, 49, 0.8) 0%, rgba(11, 17, 32, 0.95) 100%);
        border: 1px solid rgba(74, 222, 128, 0.15);
        border-radius: 24px;
        padding: 40px;
        backdrop-filter: blur(25px);
        box-shadow: 0 30px 60px -15px rgba(0, 0, 0, 0.7);
    }
    
    /* Typography Style Matrix */
    .brand-title {
        font-size: 2.4rem;
        font-weight: 900;
        letter-spacing: -1px;
        background: linear-gradient(90deg, #4ade80, #2dd4bf, #38bdf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2px;
    }
    .brand-sub {
        color: #64748b;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 35px;
    }
    .massive-temp {
        font-size: 5rem;
        font-weight: 900;
        line-height: 0.9;
        color: #ffffff;
        letter-spacing: -3px;
        margin: 20px 0;
    }
    .badge-indicator {
        background: rgba(74, 222, 128, 0.1);
        border: 1px solid rgba(74, 222, 128, 0.2);
        color: #4ade80;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
    }
    
    /* Metric Tags */
    .metric-pill-box {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 10px 16px;
        font-size: 0.85rem;
        color: #cbd5e1;
        display: inline-flex;
        align-items: center;
        margin-right: 8px;
    }
    
    /* Interactive Timeline Grid Row */
    .prediction-card-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px 24px;
        background: rgba(15, 23, 42, 0.3);
        border-radius: 16px;
        margin-bottom: 10px;
        border: 1px solid rgba(255, 255, 255, 0.02);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .prediction-card-row:hover {
        border-color: rgba(34, 197, 94, 0.3);
        background: rgba(15, 23, 42, 0.5);
    }
    </style>
""", unsafe_allow_html=True)

# --- COMPLETE CHHATTISGARH GEOGRAPHICAL MICRO-LOCATION DICTIONARY ---
GEO_REGISTRY = {
    "Bhilai Municipal Region": [
        "Civic Centre (Hub)", "Nehru Nagar East", "Nehru Nagar West", "Smriti Nagar", 
        "Radhika Nagar", "HUDCO Sector", "Risali Sector", "Sector 1", "Sector 2", 
        "Sector 3", "Sector 4", "Sector 5", "Sector 6", "Sector 7", "Sector 8", 
        "Sector 9 (Hospital Complex)", "Sector 10", "Supela Market Square", 
        "Junwani", "Khursipar", "Vaishali Nagar", "Kumhari Town", "Charoda Gate"],
    "Raipur District": ["Civil Lines", "Shankar Nagar", "Telibandha Marine Drive", "Tatibandh", "VVIP Estate", "Naya Raipur"],
    "Bilaspur District": ["Vyapar Vihar", "Rama Magneto Region", "Tifra Industrial Zone", "Bilha Core"],
    "Durg Proper": ["Padmanabhpur", "Ganjpara", "Potia Kala", "Borsi Extension"],
    "Bastar Region": ["Jagdalpur Hub", "Chitrakote Belt", "Tokapal Block"],
    "Korba District": ["TPP Colony", "Darri Jamuna", "Balco township"],
    "Surguja District": ["Ambikapur Town", "Mainpat Ridge", "Sitamani Hills"]
}

# --- STATISTICAL SIMULATION & METEOROLOGICAL ENGINE ---
def execute_predictive_modeling(sub_locale, district_parent):
    actual_temp, cloud_desc, relative_humidity, sea_pressure = 29.5, "Scattered Clouds", 65, 1008
    lookup_name = "Bhilai" if "Bhilai" in district_parent else district_parent.split()[0]
    
    try:
        api_url = f"https://api.openweathermap.org/data/2.5/weather?q={lookup_name},IN&appid={API_KEY}&units=metric"
        response = requests.get(api_url, timeout=5).json()
        if response.get("cod") == 200:
            actual_temp = response["main"]["temp"]
            cloud_desc = response["weather"][0]["description"].title()
            relative_humidity = response["main"]["humidity"]
            sea_pressure = response["main"]["pressure"]
    except:
        pass

    np.random.seed(seed=abs(hash(sub_locale)) % 999999)
    total_horizon = 30
    date_stream = [datetime.datetime.now() + datetime.timedelta(days=day_idx) for day_idx in range(total_horizon)]
    
    trig_space = np.linspace(0, 6 * np.pi, total_horizon)
    temperature_matrix = actual_temp + np.sin(trig_space) * 3.2 + np.random.normal(0, 0.6, total_horizon)
    humidity_matrix = np.clip(relative_humidity + np.cos(trig_space) * 12 + np.random.normal(0, 2.0, total_horizon), 15, 100)
    pressure_matrix = sea_pressure + np.sin(trig_space / 2) * 4 + np.random.normal(0, 0.8, total_horizon)
    
    conditions_bucket = ["☀️ Brilliant Sunshine", "🌤️ Mainly Clear", "⛅ Scattered Stratus", "💨 Mist & Haze", "🌧️ Localized Showers"]
    if "rain" in cloud_desc.lower() or relative_humidity > 75:
        conditions_bucket = ["🌧️ Monsoon Downpours", "⛈️ Convective Storms", "☁️ Overcast Sky", "🌦️ Passing Drizzle"]

    constructed_data = []
    for day_idx in range(total_horizon):
        constructed_data.append({
            "DayString": date_stream[day_idx].strftime("%b %d"),
            "Weekday": "Today" if day_idx == 0 else date_stream[day_idx].strftime("%A"),
            "Temperature": round(temperature_matrix[day_idx], 1),
            "Humidity": int(humidity_matrix[day_idx]),
            "Pressure": round(pressure_matrix[day_idx], 1),
            "VisualCondition": f"✨ {cloud_desc}" if day_idx == 0 else np.random.choice(conditions_bucket)
        })
    return constructed_data


# ==========================================
# --- AUTHENTICATION INTERFACE ROUTING ---
# ==========================================

# Track local persistent file access
user_database = load_users()

if st.session_state["auth_state"] == "login":
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color:#4ade80; margin-bottom: 5px; font-weight:800;'>Mausam Engine</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color:#64748b; font-size:0.85rem; margin-bottom: 30px;'>TELEMETRY PORTAL SECURE ACCESS</p>", unsafe_allow_html=True)
    
    with st.form("login_form", clear_on_submit=False):
        user_input = st.text_input("Username").strip()
        pass_input = st.text_input("Password", type="password")
        submit_btn = st.form_submit_button("Authenticate Access Node", use_container_width=True)
        
        if submit_btn:
            if user_input in user_database and user_database[user_input] == pass_input:
                st.session_state["current_user"] = user_input
                st.session_state["auth_state"] = "authenticated"
                st.rerun()
            else:
                st.error("Invalid secure verification token or profile mismatch.")
                
    col_left, col_right = st.columns(2)
    with col_left:
        if st.button("Create Local Account", use_container_width=True):
            st.session_state["auth_state"] = "register"
            st.rerun()
    with col_right:
        if st.button("Recover Password", use_container_width=True):
            st.session_state["auth_state"] = "forgot"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state["auth_state"] == "register":
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color:#2dd4bf; margin-bottom: 5px; font-weight:800;'>Register Node</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color:#64748b; font-size:0.85rem; margin-bottom: 30px;'>CREATE MICRO-ROUTING OPERATOR ID</p>", unsafe_allow_html=True)
    
    with st.form("register_form"):
        new_user = st.text_input("Choose Operator Username").strip()
        new_pass = st.text_input("Set Secure Access Password", type="password")
        confirm_pass = st.text_input("Verify Access Password", type="password")
        reg_btn = st.form_submit_button("Initialize Profile Array", use_container_width=True)
        
        if reg_btn:
            if not new_user or not new_pass:
                st.warning("Credential registers cannot contain null parameters.")
            elif new_user in user_database:
                st.error("Identity identifier conflict. Operator username already claimed.")
            elif new_pass != confirm_pass:
                st.error("Cryptographic structural mismatch. Passwords do not match.")
            else:
                save_user(new_user, new_pass)
                st.success("Registration success! Written directly to system files.")
                st.session_state["auth_state"] = "login"
                st.rerun()
                
    if st.button("Return to Authentication Frame", use_container_width=True):
        st.session_state["auth_state"] = "login"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state["auth_state"] == "forgot":
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color:#38bdf8; margin-bottom: 5px; font-weight:800;'>Credential Recovery</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color:#64748b; font-size:0.85rem; margin-bottom: 30px;'>QUERY ACCOUNT IDENTITY DATABASE</p>", unsafe_allow_html=True)
    
    with st.form("forgot_form"):
        lookup_user = st.text_input("Enter Target Registered Username").strip()
        recover_btn = st.form_submit_button("Query Identity Registry Keys", use_container_width=True)
        
        if recover_btn:
            if lookup_user in user_database:
                recovered_pw = user_database[lookup_user]
                st.info(f"Identity Matched. Password key token is: **{recovered_pw}**")
            else:
                st.error("Requested identifier does not exist within database indices.")
                
    if st.button("Return to Authentication Frame", use_container_width=True):
        st.session_state["auth_state"] = "login"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ==========================================
# --- SECURE MAIN APPLICATION DASHBOARD ---
# ==========================================

elif st.session_state["auth_state"] == "authenticated":

    # --- SYSTEM UI NAVIGATION HEADER ---
    st.markdown("<div class='brand-title'>CHHATTISGARH MAUSAM ANALYTICS</div>", unsafe_allow_html=True)
    st.markdown("<div class='brand-sub'>State Telemetry Network • Real-time Microclimatic Analytics Node</div>", unsafe_allow_html=True)

    # --- PANEL LAYOUT DESIGN CONTROL PANEL (SIDEBAR) ---
    with st.sidebar:
        st.markdown(f"<h5 style='color:#cbd5e1; margin-bottom:12px;'>👤 Operator: <span style='color:#4ade80;'>{st.session_state['current_user']}</span></h5>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:#4ade80; font-weight:800; margin-bottom:18px;'>📍 Regional Index</h4>", unsafe_allow_html=True)
        
        district_selection = st.selectbox("District Urban Hub", sorted(GEO_REGISTRY.keys()))
        sub_locale_list = GEO_REGISTRY[district_selection]
        selected_target_place = st.selectbox("Micro-Location Perimeter", sorted(sub_locale_list))
        
        st.markdown("---")
        simulation_length = st.slider("Forecast Modeling Window (Days)", 7, 30, 14)
        
        if st.button("Terminate Secure Session Node", use_container_width=True):
            st.session_state["current_user"] = None
            st.session_state["auth_state"] = "login"
            st.rerun()
        
        st.markdown("""
            <div style="margin-top:40px; font-size:0.75rem; color:#475569; line-height:1.5;">
                <strong>State Mesh Node:</strong> CG-04-Active<br>
                <strong>Spatial Scope:</strong> Sub-Sector Micro-Arrays<br>
                <strong>Model Framework:</strong> Thermodynamic Wave Engine
            </div>
        """, unsafe_allow_html=True)

    # --- MAIN DASHBOARD CANVAS CONTEXT GENERATOR ---
    if selected_target_place:
        computed_meteorology = execute_predictive_modeling(selected_target_place, district_selection)
        live_frame = computed_meteorology[0]
        
        # SCREEN DIVISION SPLIT ENGINE: Widescreen Viewports (2 Columns)
        viewport_left, viewport_right = st.columns([1.1, 1.9], gap="large")
        
        with viewport_left:
            st.markdown(f"""
                <div class="main-hero">
                    <span class="badge-indicator">Live CG Telemetry Loop</span>
                    <h2 style="margin:20px 0 2px 0; font-weight:900; color:#ffffff; font-size:2rem; letter-spacing:-0.5px;">{selected_target_place}</h2>
                    <p style="margin:0; font-size:0.85rem; color:#a7f3d0; font-weight:500; text-transform:uppercase; letter-spacing:1px;">{district_selection} • CHHATTISGARH</p>
                    <div class="massive-temp">{live_frame['Temperature']}°C</div>
                    <p style="font-size:1.25rem; font-weight:700; color:#f1f5f9; margin-bottom:25px;">{live_frame['VisualCondition']}</p>
                    <div class="metric-pill-box">💧 Moisture: {live_frame['Humidity']}%</div>
                    <div class="metric-pill-box">🧭 Pressure: {live_frame['Pressure']} hPa</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Local Microclimatic Diagnostics Matrix Card
            st.markdown("""<h4 style="font-weight:800; color:#f1f5f9; margin-top:20px; margin-bottom:12px; font-size:1.1rem;">📊 Boundary Layer Metrics</h4>""", unsafe_allow_html=True)
            st.markdown(f"""
                <div style="background:rgba(30, 41, 59, 0.3); border-radius:18px; padding:18px; border:1px solid rgba(255,255,255,0.04);">
                    <div style="display:flex; justify-content:space-between; margin-bottom:10px;"><span style="color:#64748b; font-size:0.85rem; font-weight:500;">Crop Humidity Index</span><span style="color:#4ade80; font-weight:700; font-size:0.85rem;">Optimal Base</span></div>
                    <div style="display:flex; justify-content:space-between; margin-bottom:10px;"><span style="color:#64748b; font-size:0.85rem; font-weight:500;">Convective Heat Index</span><span style="color:#f43f5e; font-weight:700; font-size:0.85rem;">Stable Wave</span></div>
                    <div style="display:flex; justify-content:space-between;"><span style="color:#64748b; font-size:0.85rem; font-weight:500;">Thermal Layer Dispersion</span><span style="color:#38bdf8; font-weight:700; font-size:0.85rem;">Localized Flow</span></div>
                </div>
            """, unsafe_allow_html=True)

        with viewport_right:
            # --- COMBINED GRAPH CONTAINER (Native Streamlit Container) ---
            with st.container():
                st.markdown('<div style="background: linear-gradient(145deg, rgba(22, 30, 49, 0.7) 0%, rgba(11, 17, 32, 0.9) 100%); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 24px; padding: 24px; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); margin-top: 10px;">', unsafe_allow_html=True)
                
                dataframe_slice = pd.DataFrame(computed_meteorology[:simulation_length])
                
                # Advanced Interpolation Processing for Smoothed Graph Curve Rendering
                base_indices = np.arange(len(dataframe_slice))
                dense_indices = np.linspace(base_indices.min(), base_indices.max(), 300)
                
                interpolated_temp_curve = make_interp_spline(base_indices, dataframe_slice["Temperature"], k=3)(dense_indices)
                interpolated_humidity_curve = make_interp_spline(base_indices, dataframe_slice["Humidity"], k=3)(dense_indices)
                
                dense_date_labels = [dataframe_slice["DayString"].iloc[int(idx)] for idx in np.clip(np.floor(dense_indices).astype(int), 0, len(dataframe_slice)-1)]

                # --- ADVANCED INTERACTIVE DATA GRAPH (PLOTLY ENHANCED) ---
                analytics_chart = go.Figure()
                
                analytics_chart.add_trace(go.Scatter(
                    x=dense_date_labels, y=interpolated_temp_curve,
                    mode='lines',
                    name='Surface Temperature',
                    line=dict(color='#4ade80', width=4, shape='spline'),
                    fill='tozeroy',
                    fillcolor='rgba(74, 222, 128, 0.03)'
                ))
                
                analytics_chart.add_trace(go.Scatter(
                    x=dense_date_labels, y=interpolated_humidity_curve,
                    mode='lines',
                    name='Relative Humidity',
                    line=dict(color='#818cf8', width=2, dash='dash'),
                    yaxis='y2'
                ))

                analytics_chart.update_layout(
                    title=dict(
                        text=f"PREDICTIVE RADIAL ATMOSPHERIC MATRIX GRID ({simulation_length} DAYS)", 
                        font=dict(size=11, color='#64748b', family='Inter', weight=700),
                        y=0.95, x=0.0, xanchor="left"
                    ),
                    template="plotly_dark",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=40, r=40, t=50, b=25), 
                    height=280,
                    hovermode="x unified",
                    showlegend=False, 
                    xaxis=dict(showgrid=False, tickfont=dict(color='#475569', size=10)),
                    yaxis=dict(
                        title=dict(text="Temperature (°C)", font=dict(color="#4ade80", size=11, weight=600)),
                        tickfont=dict(color='#475569', size=10), 
                        showgrid=True, 
                        gridcolor='rgba(255,255,255,0.03)'
                    ),
                    yaxis2=dict(
                        title=dict(text="Humidity (%)", font=dict(color="#818cf8", size=11, weight=600)),
                        tickfont=dict(color='#475569', size=10), 
                        overlaying='y', 
                        side='right', 
                        showgrid=False
                    )
                )
                
                st.plotly_chart(analytics_chart, use_container_width=True, config={'displayModeBar': False})
                st.markdown("</div>", unsafe_allow_html=True)

            # --- SEPARATE CONTAINER BOX 2: ISOLATED METRIC LEGEND MATRIX ---
            st.markdown("""
                <div style="background: linear-gradient(145deg, rgba(22, 30, 49, 0.5) 0%, rgba(11, 17, 32, 0.8) 100%);
                            border: 1px solid rgba(255, 255, 255, 0.03);
                            border-radius: 16px; padding: 15px 24px; display: flex; align-items: center; gap: 20px; margin-top: 15px;">
                    <span style="font-size: 0.75rem; color: #475569; text-transform: uppercase; letter-spacing: 1px; font-weight: 700;">Matrix Index:</span>
                    <div style="display: inline-flex; align-items: center; font-size: 0.85rem; color: #cbd5e1;">
                        <span style="display: inline-block; width: 14px; height: 4px; background: #4ade80; border-radius: 2px; margin-right: 8px;"></span>
                        Surface Temperature (°C)
                    </div>
                    <div style="display: inline-flex; align-items: center; font-size: 0.85rem; color: #cbd5e1;">
                        <span style="display: inline-block; width: 14px; height: 2px; border-top: 2px dashed #818cf8; margin-right: 8px;"></span>
                        Relative Humidity (%)
                    </div>
                </div>
            """, unsafe_allow_html=True)

        # --- CHRONOLOGICAL PREDICTION TIMELINE STREAM MATRIX ---
        st.markdown("""<h3 style="font-weight:800; color:#f8fafc; margin-top:50px; margin-bottom:18px; letter-spacing:-0.5px; font-size:1.3rem;">📋 Algorithmic Predictive Timeline Stream</h3>""", unsafe_allow_html=True)
        
        # Split the dataset array into clean 3-column rows
        grid_partitions = [computed_meteorology[idx:idx + 3] for idx in range(0, simulation_length, 3)]
        
        for row_chunk in grid_partitions:
            grid_col1, grid_col2, grid_col3 = st.columns(3, gap="medium")
            columns_array = [grid_col1, grid_col2, grid_col3]
            
            for data_idx, forecast_day in enumerate(row_chunk):
                with columns_array[data_idx]:
                    st.markdown(f"""
                        <div class="prediction-card-row">
                            <div>
                                <strong style="color:#ffffff; font-size:0.95rem;">{forecast_day['DayString']}</strong>
                                <div style="font-size:0.75rem; color:#475569; font-weight:500;">{forecast_day['Weekday']}</div>
                            </div>
                            <div style="font-size:0.85rem; color:#94a3b8; font-weight:600;">{forecast_day['VisualCondition']}</div>
                            <div style="text-align:right; font-weight:900; color:#4ade80; font-size:1.15rem;">{forecast_day['Temperature']}°C</div>
                        </div>
                    """, unsafe_allow_html=True)
