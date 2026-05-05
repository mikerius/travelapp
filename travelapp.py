import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

# --- 1. THE "FORCED HORIZONTAL" ENGINE ---
st.set_page_config(page_title="Vibe Travel", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

    /* TABELL-DESIGN (Vägrar staplas vertikalt) */
    .notepad-table {
        width: 100%;
        border-collapse: collapse;
        table-layout: fixed;
    }
    .notepad-table td {
        padding: 10px 5px;
        border-bottom: 0.5px solid #eee;
        vertical-align: middle;
    }
    .col-text { width: 50%; }
    .col-chk  { width: 20%; text-align: center; }
    .col-del  { width: 10%; text-align: right; }

    /* Streamlit Checkbox-trix för att få dem i tabellen */
    div[data-testid="stCheckbox"] label { margin-bottom: -15px !important; }
    div[data-testid="stCheckbox"] label span { display: none !important; }

    .stTabs [data-baseweb="tab-list"] { background-color: #f0f0f2; border-radius: 10px; }
    .stTabs [data-baseweb="tab"] { font-size: 12px !important; padding: 10px; }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ---
if 'trips' not in st.session_state:
    st.session_state.trips = {}
geolocator = Nominatim(user_agent="vibe_travel_v22")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Resor")
    trip_names = list(st.session_state.trips.keys())
    sel_trip = st.selectbox("Välj", options=trip_names) if trip_names else None
    if st.button("+ Ny resa"):
        st.session_state.add_mode = True
    if st.session_state.get('add_mode'):
        with st.form("new"):
            n = st.text_input("Destination")
            t = st.text_input("Vem? (t.ex. M,T)")
            if st.form_submit_button("Skapa"):
                st.session_state.trips[n] = {"places":[], "food":[], "travelers":[x.strip()[:1].upper() for x in t.split(",")] if t else ["M","T"]}
                st.session_state.add_mode = False
                st.rerun()

# --- MAIN ---
if sel_trip:
    trip = st.session_state.trips[sel_trip]
    st.subheader(sel_trip)
    tabs = st.tabs(["📍 Platser", "🍝 Mat", "📸 Galleri"])

    # --- TAB: MAT (DEN VI TVINGAR) ---
    with tabs[1]:
        with st.expander("➕ Lägg till"):
            f_n = st.text_input("Rätt")
            f_d = st.text_input("Beskrivning")
            if st.button("Spara"):
                if f_n:
                    trip['food'].append({"item": f_n, "desc": f_d, "checks": {name: False for name in trip['travelers']}})
                    st.rerun()

        st.write("")

        # Nu använder vi en hybrid: Vi ritar en rad i taget
        # men vi tvingar kolumnerna att vara extremt smala.
        for i, f in enumerate(trip['food']):
            # Vi skapar kolumner på nytt för varje rad för att nollställa Streamlits minne
            c1, c2, c3, c4 = st.columns([0.5, 0.15, 0.15, 0.2])
            
            with c1:
                st.markdown(f"**{f['item']}**<br><small>{f['desc']}</small>", unsafe_allow_html=True)
            
            # Person 1
            with c2:
                name1 = trip['travelers'][0]
                f['checks'][name1] = st.checkbox("", value=f['checks'].get(name1, False), key=f"c1_{i}")
                st.markdown(f"<p style='font-size:10px; text-align:center; margin-top:-5px;'>{name1}</p>", unsafe_allow_html=True)
            
            # Person 2
            with c3:
                if len(trip['travelers']) > 1:
                    name2 = trip['travelers'][1]
                    f['checks'][name2] = st.checkbox("", value=f['checks'].get(name2, False), key=f"c2_{i}")
                    st.markdown(f"<p style='font-size:10px; text-align:center; margin-top:-5px;'>{name2}</p>", unsafe_allow_html=True)
            
            with c4:
                if st.button("🗑", key=f"del_{i}"):
                    trip['food'].pop(i)
                    st.rerun()
            
            st.markdown("---")

    # --- ÖVRIGA ---
    with tabs[0]:
        q = st.text_input("Sök plats")
        if st.button("Lägg till"):
            loc = geolocator.geocode(q)
            if loc: trip['places'].append({"name":q, "lat":loc.latitude, "lon":loc.longitude}); st.rerun()
        if trip['places']:
            m = folium.Map(location=[trip['places'][-1]['lat'], trip['places'][-1]['lon']], zoom_start=13)
            st_folium(m, width="100%", height=250)
    with tabs[2]:
        st.write("Galleri")

else:
    st.info("Skapa en resa för att börja!")
