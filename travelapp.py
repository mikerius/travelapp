import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

# --- 1. THE "NOTEPAD" ENGINE (CSS) ---
st.set_page_config(page_title="Travel Planner", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, sans-serif !important;
    }

    /* MATLISTAN - NOTEPAD STYLE */
    .notepad-container {
        width: 100%;
        margin-top: 10px;
    }
    
    .notepad-row {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 0.5px solid #e5e5e5;
    }

    .notepad-text {
        flex: 1;
        padding-right: 10px;
    }

    .notepad-title {
        font-weight: 600;
        font-size: 1.05rem;
        color: #1d1d1f;
        margin-bottom: 2px;
    }

    .notepad-desc {
        font-size: 0.85rem;
        color: #86868b;
        font-style: italic;
        line-height: 1.2;
    }

    .notepad-checks {
        display: flex;
        gap: 20px; /* Mellanrum mellan M och T */
        align-items: center;
        padding-top: 2px;
    }

    /* Tvingar Streamlits checkboxar att bli små och ligga horisontellt */
    [data-testid="column"] {
        min-width: 0px !important;
        flex-direction: row !important;
        display: flex !important;
    }
    
    div[data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important; /* Förhindrar radbrytning på mobil! */
    }

    .stCheckbox {
        margin-bottom: -15px !important;
    }

    /* Snyggare header för tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #f5f5f7;
        border-radius: 10px;
        padding: 4px;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ---
if 'trips' not in st.session_state:
    st.session_state.trips = {}
geolocator = Nominatim(user_agent="travel_app_v18")
MAPBOX_TOKEN = st.secrets.get("MAPBOX_TOKEN", None)

# --- SIDEBAR ---
with st.sidebar:
    st.header("Mina Resor")
    trip_names = list(st.session_state.trips.keys())
    sel_trip = st.selectbox("Välj resa", options=trip_names, label_visibility="collapsed") if trip_names else None
    if st.button("+ Ny resa", use_container_width=True):
        st.session_state.add_mode = True
    if st.session_state.get('add_mode'):
        with st.form("new"):
            n = st.text_input("Destination")
            t = st.text_input("Resenärer (t.ex. Micke, Tessan)")
            if st.form_submit_button("Skapa"):
                st.session_state.trips[n] = {"places":[], "schedule":[], "food":[], "travelers":[x.strip() for x in t.split(",")] if t else ["M", "T"]}
                st.session_state.add_mode = False
                st.rerun()

# --- MAIN ---
if sel_trip:
    trip = st.session_state.trips[sel_trip]
    st.title(sel_trip)
    tabs = st.tabs(["📍 Platser", "📅 Schema", "🍝 Bucket List"])

    # --- TAB 3: MATEN (DEN KRITISKA DELEN) ---
    with tabs[2]:
        with st.expander("➕ Lägg till i listan"):
            f_n = st.text_input("Vad?")
            f_d = st.text_input("Beskrivning")
            if st.button("Spara"):
                trip['food'].append({"item": f_n, "desc": f_d, "checks": {name: False for name in trip['travelers']}})
                st.rerun()

        st.write("") 

        for i, f in enumerate(trip['food']):
            # Här skapar vi en container som tvingar innehållet att vara horisontellt
            # Vi använder 3 kolumner: Info (70%), Checkboxar (25%), Radera (5%)
            row_cols = st.columns([0.65, 0.25, 0.1])
            
            with row_cols[0]:
                # Vi bygger texten med HTML för att få Notepad-looken
                st.markdown(f"""
                    <div style="line-height:1.2;">
                        <div style="font-weight:600; font-size:1rem;">{f['item']}</div>
                        <div style="color:gray; font-size:0.8rem; font-style:italic;">{f['desc']}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with row_cols[1]:
                # Här lägger vi person-checkboxar på RAD
                n_travelers = len(trip['travelers'])
                chk_cols = st.columns(n_travelers)
                for idx, name in enumerate(trip['travelers']):
                    label = name[0].upper() # Bara första bokstaven
                    trip['food'][i]['checks'][name] = chk_cols[idx].checkbox(label, value=f['checks'][name], key=f"c{i}{idx}")
            
            with row_cols[2]:
                if st.button("🗑", key=f"del{i}"):
                    trip['food'].pop(i)
                    st.rerun()
            
            st.markdown("<hr style='margin:2px 0; opacity:0.1'>", unsafe_allow_html=True)

    # --- TAB 1: KARTA ---
    with tabs[0]:
        c1, c2 = st.columns([1, 2])
        with c1:
            loc_q = st.text_input("Sök plats...")
            if st.button("Lägg till"):
                l = geolocator.geocode(loc_q)
                if l:
                    trip['places'].append({"name":loc_q, "lat":l.latitude, "lon":l.longitude})
                    st.rerun()
            for p in trip['places']:
                st.caption(f"📍 {p['name']}")
        with c2:
            center = [trip['places'][-1]['lat'], trip['places'][-1]['lon']] if trip['places'] else [48.2, 16.3]
            m = folium.Map(location=center, zoom_start=13)
            for p in trip['places']:
                folium.Marker([p['lat'], p['lon']], popup=p['name']).add_to(m)
            st_folium(m, width="100%", height=350)

else:
    st.info("Börja med att skapa en resa i menyn till vänster!")
