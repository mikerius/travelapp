import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

# --- 1. PORTRAIT OPTIMIZED UI (CSS) ---
st.set_page_config(page_title="Vibe Travel", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, sans-serif !important;
    }

    /* Tvingar stående läge-vänlighet */
    div[data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important;
        gap: 0px !important;
    }

    [data-testid="column"] {
        min-width: 0px !important;
        flex: 1 1 auto !important;
    }

    /* MATLISTAN - EXTRA TAJT FÖR STÅENDE MOBIL */
    .notepad-text {
        line-height: 1.1;
        overflow: hidden;
    }

    .stCheckbox {
        margin-bottom: -20px !important;
    }

    /* Gör papperskorg-knappen minimal */
    .stButton>button {
        padding: 2px 5px !important;
        height: auto !important;
        border: none !important;
        background: transparent !important;
    }

    /* Tabs design */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: #f0f0f2;
        border-radius: 10px;
        padding: 3px;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-size: 12px !important; /* Mindre text på tabs för att alla ska få plats stående */
        padding: 5px 8px !important;
    }

    /* Karta - anpassad för stående skärm */
    iframe {
        border-radius: 12px;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA & SESSION STATE ---
if 'trips' not in st.session_state:
    st.session_state.trips = {}
geolocator = Nominatim(user_agent="vibe_travel_v19")
MAPBOX_TOKEN = st.secrets.get("MAPBOX_TOKEN", None)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 🗺️ Mina Resor")
    trip_names = list(st.session_state.trips.keys())
    sel_trip = st.selectbox("Välj resa", options=trip_names, label_visibility="collapsed") if trip_names else None
    if st.button("+ Ny resa", use_container_width=True):
        st.session_state.add_mode = True
    if st.session_state.get('add_mode'):
        with st.form("new_trip_form"):
            n = st.text_input("Destination")
            t = st.text_input("Vilka reser? (t.ex Micke, Tessan)")
            if st.form_submit_button("Spara"):
                st.session_state.trips[n] = {
                    "places":[], "schedule":[], "food":[], "photos":[], 
                    "travelers":[x.strip() for x in t.split(",")] if t else ["M", "T"]
                }
                st.session_state.add_mode = False
                st.rerun()

# --- MAIN APP ---
if sel_trip:
    trip = st.session_state.trips[sel_trip]
    st.markdown(f"### {sel_trip}")
    
    # Nu med Galleri tillbaka!
    tabs = st.tabs(["📍 Platser", "📅 Schema", "🍝 Mat", "📸 Galleri"])

    # --- TAB: MAT (BUCKET LIST) ---
    with tabs[2]:
        with st.expander("➕ Lägg till mat"):
            f_n = st.text_input("Rätt")
            f_d = st.text_input("Info")
            if st.button("Spara rätt"):
                trip['food'].append({"item": f_n, "desc": f_d, "checks": {name: False for name in trip['travelers']}})
                st.rerun()

        for i, f in enumerate(trip['food']):
            # Extremt tajta kolumner för stående läge: 60% text, 30% checks, 10% del
            c_txt, c_chk1, c_chk2, c_del = st.columns([0.55, 0.17, 0.17, 0.11])
            
            with c_txt:
                st.markdown(f"**{f['item']}**<br><small style='color:gray;'>{f['desc']}</small>", unsafe_allow_html=True)
            
            # Vi förutsätter max 2 resenärer för den här tajta layouten
            for idx, name in enumerate(trip['travelers'][:2]):
                target_col = c_chk1 if idx == 0 else c_chk2
                with target_col:
                    initial = name[0].upper()
                    trip['food'][i]['checks'][name] = st.checkbox(initial, value=f['checks'][name], key=f"f_{sel_trip}_{i}_{name}")
            
            with c_del:
                if st.button("🗑️", key=f"del_f_{i}"):
                    trip['food'].pop(i); st.rerun()
            
            st.markdown("<hr style='margin:2px 0; opacity:0.1'>", unsafe_allow_html=True)

    # --- TAB: PLATSER ---
    with tabs[0]:
        with st.expander("🔍 Sök plats"):
            q = st.text_input("Namn...")
            if st.button("Lägg till plats"):
                loc = geolocator.geocode(q)
                if loc:
                    trip['places'].append({"name":q, "lat":loc.latitude, "lon":loc.longitude})
                    st.rerun()
        
        # Kartan stående - vi gör den lite mindre vertikalt för att se listan under
        center = [trip['places'][-1]['lat'], trip['places'][-1]['lon']] if trip['places'] else [48.208, 16.373]
        m = folium.Map(location=center, zoom_start=13, tiles="CartoDB Positron")
        for p in trip['places']:
            folium.Marker([p['lat'], p['lon']], popup=p['name']).add_to(m)
        st_folium(m, width="100%", height=300, use_container_width=True)
        
        for p in trip['places']:
            st.markdown(f"📍 {p['name']}")

    # --- TAB: SCHEMA ---
    with tabs[1]:
        st.write("Planera dagarna här...")
        # (Samma logik som tidigare för schema kan läggas här)

    # --- TAB: GALLERI (TILLBAKA!) ---
    with tabs[3]:
        st.markdown("### 📸 Resebilder")
        up_file = st.file_uploader("Ladda upp", type=['jpg', 'png'], label_visibility="collapsed")
        if up_file:
            trip['photos'].append(up_file)
            st.success("Bild sparad!")
        
        if trip['photos']:
            cols = st.columns(2) # 2 bilder i bredd på mobil
            for idx, img in enumerate(trip['photos']):
                cols[idx % 2].image(img, use_container_width=True)

else:
    st.info("Skapa en resa i menyn till vänster!")
