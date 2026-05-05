import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

# --- 1. THE "PORTRAIT-LOCKED" TABLE ENGINE (CSS) ---
st.set_page_config(page_title="Vibe Travel", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, sans-serif !important;
    }

    /* FIXA TABELLEN - DETTA TVINGAR RADEN ATT VARA HORISONTELL */
    .compact-table {
        width: 100%;
        border-collapse: collapse;
    }
    
    /* Justera Streamlits checkboxar så de inte tar plats */
    .stCheckbox {
        margin-bottom: -15px !important;
    }
    
    /* Göm labels (M, T) men låt dem finnas för skärmläsare */
    .stCheckbox label p {
        font-size: 0.7rem !important;
        margin-top: 2px !important;
    }

    /* Tabs för mobil */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0px;
        background-color: #f0f0f2;
        border-radius: 10px;
        padding: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 11px !important;
        padding: 5px 6px !important;
    }

    /* Dra ihop avståndet mellan element */
    [data-testid="stVerticalBlock"] > div {
        gap: 0rem !important;
        margin-bottom: -5px !important;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA INITIALIZATION ---
if 'trips' not in st.session_state:
    st.session_state.trips = {}
geolocator = Nominatim(user_agent="vibe_travel_v20")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Mina Resor")
    trip_names = list(st.session_state.trips.keys())
    sel_trip = st.selectbox("Välj resa", options=trip_names, label_visibility="collapsed") if trip_names else None
    if st.button("+ Ny resa", use_container_width=True):
        st.session_state.add_mode = True
    if st.session_state.get('add_mode'):
        with st.form("new_trip"):
            n = st.text_input("Destination")
            t = st.text_input("Vilka reser? (t.ex Micke, Tessan)")
            if st.form_submit_button("Skapa"):
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
    
    tabs = st.tabs(["📍 Platser", "📅 Schema", "🍝 Mat", "📸 Galleri"])

    # --- TAB: MAT (BUCKET LIST) ---
    with tabs[2]:
        with st.expander("➕ Lägg till mat"):
            f_n = st.text_input("Vad?")
            f_d = st.text_input("Info (valfritt)")
            if st.button("Spara i listan"):
                if f_n:
                    trip['food'].append({"item": f_n, "desc": f_d, "checks": {name: False for name in trip['travelers']}})
                    st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # HÄR ÄR MAGIN: Vi använder st.columns men med extremt tajta proportioner 
        # och vi lägger allt på EN rad per maträtt.
        for i, f in enumerate(trip['food']):
            # 60% till text, 15% per person (max 2), 10% till radera
            cols = st.columns([0.55, 0.17, 0.17, 0.11])
            
            with cols[0]:
                # Vi använder en fallback f.get() ifall gammal data saknar nycklar
                name = f.get('item', 'Okänd')
                desc = f.get('desc', '')
                st.markdown(f"**{name}**<br><small style='color:gray;'>{desc}</small>", unsafe_allow_html=True)
            
            # Checkboxar
            for idx, name in enumerate(trip['travelers'][:2]):
                with cols[idx+1]:
                    initial = name[0].upper()
                    # Vi hämtar värdet säkert
                    current_val = f.get('checks', {}).get(name, False)
                    f['checks'][name] = st.checkbox(initial, value=current_val, key=f"chk_{i}_{name}")
            
            with cols[3]:
                if st.button("🗑", key=f"del_{i}"):
                    trip['food'].pop(i)
                    st.rerun()
            
            st.markdown("<hr style='margin: 0px; opacity: 0.1;'>", unsafe_allow_html=True)

    # --- TAB: PLATSER ---
    with tabs[0]:
        with st.expander("🔍 Sök plats"):
            q = st.text_input("Sök...")
            if st.button("Lägg till"):
                loc = geolocator.geocode(q)
                if loc:
                    trip['places'].append({"name":q, "lat":loc.latitude, "lon":loc.longitude})
                    st.rerun()
        
        if trip['places']:
            center = [trip['places'][-1]['lat'], trip['places'][-1]['lon']]
            m = folium.Map(location=center, zoom_start=13, tiles="CartoDB Positron")
            for p in trip['places']:
                folium.Marker([p['lat'], p['lon']], popup=p.get('name')).add_to(m)
            st_folium(m, width="100%", height=300, use_container_width=True)
            
            for p in trip['places']:
                st.caption(f"📍 {p.get('name')}")

    # --- TAB: SCHEMA & GALLERI (Enkel version) ---
    with tabs[1]:
        st.info("Schema-funktion aktiveras i nästa steg.")
    with tabs[3]:
        up = st.file_uploader("Ladda upp bild", type=['jpg', 'png'])
        if up:
            trip.setdefault('photos', []).append(up)
            st.success("Uppladdad!")
        if trip.get('photos'):
            c = st.columns(2)
            for idx, img in enumerate(trip['photos']):
                c[idx%2].image(img, use_container_width=True)

else:
    st.info("Skapa en resa i menyn!")
