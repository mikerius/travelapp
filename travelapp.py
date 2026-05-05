import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

# --- 1. APPLE NOTES / SAAS LOOK & FEEL (CSS) ---
st.set_page_config(page_title="Vibe Travel", layout="wide", page_icon="📍")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global styling */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background-color: #FFFFFF;
        color: #1d1d1f;
    }

    /* Ta bort Streamlits standard-padding för att maximera ytan på mobilen */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        max-width: 100% !important;
    }

    /* Stilrena Tabs (Notepad-stil) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f5f5f7;
        padding: 5px;
        border-radius: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 35px;
        border-radius: 8px;
        border: none;
        background-color: transparent;
        transition: 0.2s;
    }
    .stTabs [data-baseweb="tab"]:hover { background-color: #e8e8ed; }
    .stTabs [data-baseweb="tab--active"] {
        background-color: #ffffff !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important;
    }

    /* "Notepad" Matlista - Supertajt vertikalt */
    [data-testid="column"] {
        padding: 0px 4px !important;
        align-self: center;
    }
    
    [data-testid="stVerticalBlock"] > div {
        gap: 0rem !important;
        margin-bottom: -2px !important;
    }

    /* Checkboxar - runda och diskreta */
    [data-testid="stCheckbox"] {
        margin-bottom: -15px !important;
    }
    .stCheckbox label p {
        font-size: 0.85rem !important;
        font-weight: 600;
        color: #86868b;
    }

    /* Cards för platser */
    .place-card {
        padding: 12px;
        margin-bottom: 8px;
        border-radius: 12px;
        background: #fbfbfd;
        border: 1px solid #f2f2f7;
    }

    /* Knappar (Wanderlog/Apple stil) */
    .stButton>button {
        border-radius: 20px;
        border: 1px solid #d2d2d7;
        background-color: #ffffff;
        font-weight: 500;
        color: #1d1d1f;
        transition: 0.2s;
    }
    .stButton>button:hover {
        border-color: #007aff;
        color: #007aff;
    }

    hr { margin: 4px 0 !important; opacity: 0.05; }
    
    /* Dölj onödigt Streamlit-pynt */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. INITIALIZATION & DATA ---
if 'trips' not in st.session_state:
    st.session_state.trips = {}

geolocator = Nominatim(user_agent="vibe_travel_v16")

# Hämta Mapbox token om den finns i Secrets
MAPBOX_TOKEN = st.secrets.get("MAPBOX_TOKEN", None)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 🗺️ Mina Resor")
    trip_names = list(st.session_state.trips.keys())
    sel_trip = st.selectbox("Välj", options=trip_names, label_visibility="collapsed") if trip_names else None
    
    if st.button("+ Skapa ny resa", use_container_width=True):
        st.session_state.add_mode = True
    
    if st.session_state.get('add_mode'):
        with st.form("new_trip"):
            n = st.text_input("Destination")
            t = st.text_input("Vilka reser? (t.ex Micke, Tessan)")
            if st.form_submit_button("Spara"):
                st.session_state.trips[n] = {
                    "places":[], "schedule":[], "food":[], "photos":[], 
                    "travelers":[x.strip() for x in t.split(",")] if t else ["Micke"]
                }
                st.session_state.add_mode = False
                st.rerun()

# --- MAIN APP ---
if sel_trip:
    trip = st.session_state.trips[sel_trip]
    st.markdown(f"<h2 style='margin-bottom: 0px;'>{sel_trip}</h2>", unsafe_allow_html=True)
    st.caption(f"👥 {', '.join(trip['travelers'])}")
    
    tabs = st.tabs(["📍 Platser", "📅 Itinerary", "🍝 Bucket List", "📸 Galleri"])

    # --- TAB 1: PLATSER & KARTA ---
    with tabs[0]:
        col1, col2 = st.columns([1, 2.2])
        with col1:
            with st.expander("➕ Lägg till plats", expanded=False):
                q = st.text_input("Sök...", key="search_place")
                cat = st.selectbox("Typ", ["Sevärdhet", "Restaurang", "Bostad", "Annat"])
                note = st.text_input("Notis")
                if st.button("Spara i Itinerary", use_container_width=True):
                    loc = geolocator.geocode(q)
                    if loc:
                        colors = {"Sevärdhet":"#007aff", "Restaurang":"#ff9500", "Bostad":"#34c759", "Annat":"#8e8e93"}
                        icons = {"Sevärdhet":"camera", "Restaurang":"cutlery", "Bostad":"home", "Annat":"info"}
                        trip['places'].append({"name":q, "lat":loc.latitude, "lon":loc.longitude, "note":note, "cat":cat, "color":colors[cat], "icon":icons[cat]})
                        st.rerun()
            
            for i, p in enumerate(trip['places']):
                st.markdown(f"""
                <div class="place-card">
                    <small style="color:{p['color']}; font-weight:bold;">{p['cat'].upper()}</small><br>
                    <b>{p['name']}</b><br>
                    <span style="color:#636366; font-size:0.8rem;">{p['note']}</span>
                </div>
                """, unsafe_allow_html=True)
                if st.button("Radera", key=f"del_p_{i}"):
                    trip['places'].pop(i); st.rerun()

        with col2:
            center = [trip['places'][-1]['lat'], trip['places'][-1]['lon']] if trip['places'] else [48.2082, 16.3738]
            tiles = f"https://api.mapbox.com/styles/v1/mapbox/streets-v12/tiles/{{z}}/{{x}}/{{y}}?access_token={MAPBOX_TOKEN}" if MAPBOX_TOKEN else "CartoDB Positron"
            m = folium.Map(location=center, zoom_start=13, tiles=tiles, attr="Mapbox" if MAPBOX_TOKEN else "Carto")
            for p in trip['places']:
                folium.Marker([p['lat'], p['lon']], popup=p['name'], icon=folium.Icon(color="white", icon_color=p['color'], icon=p['icon'], prefix='fa')).add_to(m)
            st_folium(m, width="100%", height=450, use_container_width=True)

    # --- TAB 2: ITINERARY ---
    with tabs[1]:
        with st.expander("➕ Ny händelse"):
            d = st.date_input("Dag")
            t = st.time_input("Tid")
            act = st.text_input("Aktivitet")
            if st.button("Lägg till i schema"):
                trip['schedule'].append({"date": str(d), "time": str(t), "activity": act})
                st.rerun()
        
        if trip['schedule']:
            df = pd.DataFrame(trip['schedule']).sort_values(["date", "time"])
            for day, group in df.groupby("date"):
                st.markdown(f"<h4 style='margin-top:15px; color:#007aff;'>{day}</h4>", unsafe_allow_html=True)
                for _, row in group.iterrows():
                    st.markdown(f"**{row['time'][:5]}**: {row['activity']}")
                    st.markdown("<hr>", unsafe_allow_html=True)

    # --- TAB 3: BUCKET LIST (APPLE NOTES STYLE) ---
    with tabs[2]:
        st.markdown("### 🍴 Mat-check")
        with st.expander("➕ Ny godsak"):
            f_n = st.text_input("Namn på rätt")
            f_d = st.text_input("Beskrivning (kursiv)")
            if st.button("Lägg till mat", use_container_width=True):
                if f_n:
                    trip['food'].append({"item": f_n, "desc": f_d, "checks": {name: False for name in trip['travelers']}})
                    st.rerun()
        
        st.write("") # Mellanrum
        for i, f in enumerate(trip['food']):
            # Nuclear Compact Row
            c_txt, c_chk, c_del = st.columns([0.6, 0.3, 0.1])
            
            with c_txt:
                st.markdown(f"<div style='line-height:1.1;'><b>{f['item']}</b><br><small style='color:#86868b; font-style:italic;'>{f.get('desc','')}</small></div>", unsafe_allow_html=True)
            
            with c_chk:
                sub_cols = st.columns(len(trip['travelers']))
                for idx, name in enumerate(trip['travelers']):
                    initial = name[0].upper()
                    trip['food'][i]['checks'][name] = sub_cols[idx].checkbox(initial, value=f['checks'][name], key=f"chk_{i}_{name}")
            
            with c_del:
                if st.button("🗑", key=f"del_f_{i}"):
                    trip['food'].pop(i); st.rerun()
            
            st.markdown("<hr>", unsafe_allow_html=True)

    # --- TAB 4: GALLERI ---
    with tabs[3]:
        up = st.file_uploader("Ladda upp bild", type=['jpg', 'png'], label_visibility="collapsed")
        if up:
            trip['photos'].append(up)
            st.success("Bild tillagd!")
        
        if trip['photos']:
            cols = st.columns(3)
            for idx, img in enumerate(trip['photos']):
                cols[idx % 3].image(img, use_container_width=True)

else:
    st.info("👋 Välkommen! Skapa en resa i menyn till vänster för att börja planera.")
