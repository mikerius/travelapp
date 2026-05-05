import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

# --- 1. THE "PORTRAIT-LOCKED" ENGINE (CSS) ---
st.set_page_config(page_title="Vibe Travel", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, sans-serif !important;
    }

    /* Tvinga bort Streamlits marginaler */
    .block-container { padding-top: 1rem !important; }
    
    /* DESIGN FÖR MAT-TABELLEN (FÖRHINDRAR STAPLING) */
    .food-table {
        width: 100%;
        border-collapse: collapse;
        table-layout: fixed; /* Detta låser bredden! */
    }
    .food-table td {
        padding: 8px 0;
        border-bottom: 0.5px solid #eee;
        vertical-align: middle;
    }
    
    /* Göm Streamlits labels för checkboxar helt för att spara plats */
    div[data-testid="stCheckbox"] label span {
        display: none;
    }
    div[data-testid="stCheckbox"] {
        margin-bottom: -15px !important;
        display: flex;
        justify-content: center;
    }

    /* Tabs-styling för att rymmas på bredden */
    .stTabs [data-baseweb="tab-list"] { gap: 0px; background-color: #f0f0f2; border-radius: 10px; }
    .stTabs [data-baseweb="tab"] { font-size: 11px !important; padding: 5px 6px !important; }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ---
if 'trips' not in st.session_state:
    st.session_state.trips = {}
geolocator = Nominatim(user_agent="vibe_travel_final_v1")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Mina Resor")
    trip_names = list(st.session_state.trips.keys())
    sel_trip = st.selectbox("Välj resa", options=trip_names, label_visibility="collapsed") if trip_names else None
    if st.button("+ Ny resa", use_container_width=True):
        st.session_state.add_mode = True
    if st.session_state.get('add_mode'):
        with st.form("new_trip_form"):
            n = st.text_input("Destination")
            t = st.text_input("Vilka reser? (t.ex. M, T)")
            if st.form_submit_button("Skapa"):
                st.session_state.trips[n] = {
                    "places":[], "schedule":[], "food":[], "photos":[], 
                    "travelers":[x.strip()[:1].upper() for x in t.split(",")] if t else ["M", "T"]
                }
                st.session_state.add_mode = False
                st.rerun()

# --- MAIN APP ---
if sel_trip:
    trip = st.session_state.trips[sel_trip]
    st.subheader(sel_trip)
    
    tabs = st.tabs(["📍 Platser", "📅 Schema", "🍝 Mat", "📸 Galleri"])

    # --- TAB: MAT (HÄR FIXAR VI TABELLEN) ---
    with tabs[2]:
        with st.expander("➕ Lägg till mat"):
            f_n = st.text_input("Vad?")
            f_d = st.text_input("Info")
            if st.button("Spara"):
                if f_n:
                    trip['food'].append({"item": f_n, "desc": f_d, "checks": {name: False for name in trip['travelers']}})
                    st.rerun()

        # Vi använder en kombination av HTML för layout och Streamlit för funktionalitet
        # Genom att sätta kolumnerna EXTREMT tajt här och dölja labels vinner vi
        for i, f in enumerate(trip['food']):
            # c1=Text(55%), c2=Pers1(15%), c3=Pers2(15%), c4=Radera(15%)
            cols = st.columns([0.55, 0.15, 0.15, 0.15])
            
            with cols[0]:
                item_name = f.get('item', 'Inget namn')
                item_desc = f.get('desc', '')
                st.markdown(f"**{item_name}**<br><small style='color:gray;'>{item_desc}</small>", unsafe_allow_html=True)
            
            # Checkboxar utan labels (vi döljer M/T i CSS men de finns i koden)
            for idx, name in enumerate(trip['travelers'][:2]):
                with cols[idx+1]:
                    # Vi använder en tom sträng som label för att inte trigga vertikal stapling
                    f['checks'][name] = st.checkbox("", value=f['checks'].get(name, False), key=f"c_{i}_{name}")
                    st.markdown(f"<div style='text-align:center; font-size:10px; color:gray; margin-top:-5px;'>{name}</div>", unsafe_allow_html=True)
            
            with cols[3]:
                if st.button("🗑️", key=f"del_{i}"):
                    trip['food'].pop(i)
                    st.rerun()
            
            st.markdown("<hr style='margin:2px 0; opacity:0.1'>", unsafe_allow_html=True)

    # --- TAB: PLATSER (STÅENDE OPTIMERAD) ---
    with tabs[0]:
        q = st.text_input("Sök plats...", key="loc_search")
        if st.button("Lägg till plats"):
            loc = geolocator.geocode(q)
            if loc:
                trip['places'].append({"name":q, "lat":loc.latitude, "lon":loc.longitude})
                st.rerun()
        
        if trip['places']:
            center = [trip['places'][-1]['lat'], trip['places'][-1]['lon']]
            m = folium.Map(location=center, zoom_start=13, tiles="CartoDB Positron")
            for p in trip['places']:
                folium.Marker([p['lat'], p['lon']], popup=p['name']).add_to(m)
            st_folium(m, width="100%", height=250, use_container_width=True)

    # --- TAB: SCHEMA & GALLERI ---
    with tabs[1]:
        st.write("Schema kommer här...")
    with tabs[3]:
        up = st.file_uploader("Bild", type=['jpg', 'png'])
        if up:
            trip.setdefault('photos', []).append(up)
        if trip.get('photos'):
            c = st.columns(2)
            for idx, img in enumerate(trip['photos']):
                c[idx%2].image(img, use_container_width=True)

else:
    st.info("Börja med att skapa en resa!")
