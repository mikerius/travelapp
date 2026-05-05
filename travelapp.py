import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

# --- 1. APPLE NOTES / COMPACT UI ---
st.set_page_config(page_title="Vibe Travel", layout="wide", page_icon="📍")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, sans-serif !important;
        background-color: #FFFFFF;
    }

    /* Tabell-design för att tvinga horisontell layout på mobil */
    .food-table {
        width: 100%;
        border-collapse: collapse;
    }
    .food-table td {
        padding: 4px 0;
        border-bottom: 1px solid #f2f2f7;
        vertical-align: middle;
    }
    .food-name-cell { width: 50%; }
    .food-check-cell { width: 15%; text-align: center; }
    .food-del-cell { width: 10%; text-align: right; }

    /* Fixa radavståndet i Streamlit */
    [data-testid="stVerticalBlock"] > div {
        gap: 0.2rem !important;
        margin-bottom: 0px !important;
    }
    
    /* Göm labels på checkboxar i matlistan för att de ska sitta tajt */
    .compact-check label {
        display: flex;
        flex-direction: column;
        align-items: center;
        font-size: 0.7rem !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    .stTabs [data-baseweb="tab-list"] { background-color: #f5f5f7; border-radius: 12px; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIC ---
if 'trips' not in st.session_state:
    st.session_state.trips = {}
geolocator = Nominatim(user_agent="vibe_travel_v17")
MAPBOX_TOKEN = st.secrets.get("MAPBOX_TOKEN", None)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 🗺️ Resor")
    trip_names = list(st.session_state.trips.keys())
    sel_trip = st.selectbox("Välj", options=trip_names, label_visibility="collapsed") if trip_names else None
    if st.button("+ Ny resa", use_container_width=True):
        st.session_state.add_mode = True
    if st.session_state.get('add_mode'):
        with st.form("new"):
            n = st.text_input("Vart?")
            t = st.text_input("Vem? (komma-separerat)")
            if st.form_submit_button("Spara"):
                st.session_state.trips[n] = {"places":[], "schedule":[], "food":[], "photos":[], "travelers":[x.strip() for x in t.split(",")] if t else ["Micke", "Tessan"]}
                st.session_state.add_mode = False
                st.rerun()

# --- MAIN ---
if sel_trip:
    trip = st.session_state.trips[sel_trip]
    st.title(sel_trip)
    tabs = st.tabs(["📍 Platser", "📅 Schema", "🍝 Mat", "📸 Bilder"])

    # --- TAB 3: MAT (DEN VI FIXAR NU) ---
    with tabs[2]:
        with st.expander("➕ Lägg till ny rätt"):
            f_n = st.text_input("Rätt")
            f_d = st.text_input("Beskrivning")
            if st.button("Spara mat"):
                trip['food'].append({"item": f_n, "desc": f_d, "checks": {name: False for name in trip['travelers']}})
                st.rerun()

        st.write("")
        
        # Nu skapar vi rader manuellt men med Streamlit-objekt inuti 
        # för att garantera att de hamnar på samma horisontella rad.
        for i, f in enumerate(trip['food']):
            # Vi använder en container med fasta kolumner och stänger av responsivitet 
            # genom att hålla dem extremt enkla.
            c1, c2, c3, c4 = st.columns([0.4, 0.2, 0.2, 0.1])
            
            with c1:
                st.markdown(f"**{f['item']}**<br><small style='color:gray; font-style:italic;'>{f['desc']}</small>", unsafe_allow_html=True)
            
            # Här tvingar vi in personernas checkboxar
            for idx, name in enumerate(trip['travelers']):
                target_col = c2 if idx == 0 else c3
                with target_col:
                    initial = name[0].upper()
                    trip['food'][i]['checks'][name] = st.checkbox(initial, value=f['checks'][name], key=f"chk_{sel_trip}_{i}_{name}")
            
            with c4:
                if st.button("🗑", key=f"del_{i}"):
                    trip['food'].pop(i)
                    st.rerun()
            
            st.markdown("---")

    # --- TAB 1: KARTA ---
    with tabs[0]:
        c1, c2 = st.columns([1, 2.5])
        with c1:
            with st.expander("➕ Lägg till"):
                q = st.text_input("Sök...")
                if st.button("Spara plats"):
                    loc = geolocator.geocode(q)
                    if loc:
                        trip['places'].append({"name":q, "lat":loc.latitude, "lon":loc.longitude, "note":"", "cat":"Sevärdhet", "color":"#007aff", "icon":"camera"})
                        st.rerun()
            for i, p in enumerate(trip['places']):
                st.info(f"📍 {p['name']}")
        with c2:
            center = [trip['places'][-1]['lat'], trip['places'][-1]['lon']] if trip['places'] else [48.2082, 16.3738]
            m = folium.Map(location=center, zoom_start=13, tiles="CartoDB Positron")
            for p in trip['places']:
                folium.Marker([p['lat'], p['lon']], icon=folium.Icon(color="blue")).add_to(m)
            st_folium(m, width="100%", height=400)

    # --- TAB 2 & 4 ---
    with tabs[1]:
        st.write("Schema kommer här...")
    with tabs[3]:
        st.write("Bilder kommer här...")

else:
    st.info("Skapa en resa i menyn!")
