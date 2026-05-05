import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

# --- 1. THE "PORTRAIT-FIX" ENGINE (CSS) ---
st.set_page_config(page_title="Vibe Travel", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, sans-serif !important;
    }

    /* NOTEPAD LISTA - TVINGAR HORISONTELLT */
    .notepad-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 10px 0;
        border-bottom: 0.5px solid #eee;
        width: 100%;
    }
    .notepad-info {
        flex: 1;
        line-height: 1.2;
    }
    .notepad-title {
        font-weight: 600;
        font-size: 1rem;
        color: #1d1d1f;
    }
    .notepad-desc {
        font-size: 0.8rem;
        color: #86868b;
        font-style: italic;
    }

    /* Göm Streamlits fula labels och gör dem runda */
    div[data-testid="stCheckbox"] label span { display: none; }
    div[data-testid="stCheckbox"] { margin-bottom: -15px !important; }
    
    /* Justera knappar */
    .stButton>button { border: none; background: transparent; padding: 0; }

    /* Tabs för mobil */
    .stTabs [data-baseweb="tab-list"] { gap: 0px; background-color: #f0f0f2; border-radius: 10px; }
    .stTabs [data-baseweb="tab"] { font-size: 11px !important; padding: 5px 8px !important; }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ---
if 'trips' not in st.session_state:
    st.session_state.trips = {}
geolocator = Nominatim(user_agent="vibe_travel_v21")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Mina Resor")
    trip_names = list(st.session_state.trips.keys())
    sel_trip = st.selectbox("Välj", options=trip_names, label_visibility="collapsed") if trip_names else None
    if st.button("+ Ny resa", use_container_width=True):
        st.session_state.add_mode = True
    if st.session_state.get('add_mode'):
        with st.form("new_trip"):
            n = st.text_input("Vart?")
            t = st.text_input("Vem? (t.ex. M, T)")
            if st.form_submit_button("Skapa"):
                st.session_state.trips[n] = {"places":[], "food":[], "travelers":[x.strip()[:1].upper() for x in t.split(",")] if t else ["M", "T"]}
                st.session_state.add_mode = False
                st.rerun()

# --- MAIN ---
if sel_trip:
    trip = st.session_state.trips[sel_trip]
    st.subheader(sel_trip)
    tabs = st.tabs(["📍 Platser", "🍝 Mat", "📸 Galleri"])

    # --- TAB: MAT (DEN VI FIXAR) ---
    with tabs[1]:
        with st.expander("➕ Lägg till"):
            f_n = st.text_input("Rätt")
            f_d = st.text_input("Info")
            if st.button("Spara"):
                if f_n:
                    trip['food'].append({"item": f_n, "desc": f_d, "checks": {name: False for name in trip['travelers']}})
                    st.rerun()

        st.write("")

        for i, f in enumerate(trip['food']):
            # Vi skapar en rad som Streamlit inte kan bryta vertikalt
            # genom att hålla kolumnerna extremt simpla
            c1, c2, c3, c4 = st.columns([0.55, 0.15, 0.15, 0.15])
            
            with c1:
                # Ingen Markdown-kod här, bara ren text
                st.markdown(f"**{f['item']}** \n*{f['desc']}*", unsafe_allow_html=True)
            
            # Checkbox för person 1
            with c2:
                name1 = trip['travelers'][0]
                f['checks'][name1] = st.checkbox("", value=f['checks'].get(name1, False), key=f"c1_{i}")
                st.markdown(f"<div style='text-align:center;font-size:10px;margin-top:-5px;'>{name1}</div>", unsafe_allow_html=True)
            
            # Checkbox för person 2 (om den finns)
            with c3:
                if len(trip['travelers']) > 1:
                    name2 = trip['travelers'][1]
                    f['checks'][name2] = st.checkbox("", value=f['checks'].get(name2, False), key=f"c2_{i}")
                    st.markdown(f"<div style='text-align:center;font-size:10px;margin-top:-5px;'>{name2}</div>", unsafe_allow_html=True)
            
            with c4:
                if st.button("🗑️", key=f"del_{i}"):
                    trip['food'].pop(i)
                    st.rerun()
            
            st.markdown("---")

    # --- TAB: PLATSER ---
    with tabs[0]:
        q = st.text_input("Sök plats...")
        if st.button("Lägg till"):
            loc = geolocator.geocode(q)
            if loc:
                trip['places'].append({"name":q, "lat":loc.latitude, "lon":loc.longitude})
                st.rerun()
        
        if trip['places']:
            center = [trip['places'][-1]['lat'], trip['places'][-1]['lon']]
            m = folium.Map(location=center, zoom_start=13, tiles="CartoDB Positron")
            for p in trip['places']:
                folium.Marker([p['lat'], p['lon']], popup=p['name']).add_to(m)
            st_folium(m, width="100%", height=300, use_container_width=True)

    # --- TAB: GALLERI ---
    with tabs[2]:
        up = st.file_uploader("Bild", type=['jpg', 'png'])
        if up:
            trip.setdefault('photos', []).append(up)
        if trip.get('photos'):
            c = st.columns(2)
            for idx, img in enumerate(trip['photos']):
                c[idx%2].image(img, use_container_width=True)

else:
    st.info("Skapa en resa i menyn!")
