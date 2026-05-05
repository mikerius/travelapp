import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

# --- 1. THE "NO-STACK" ENGINE (CSS) ---
st.set_page_config(page_title="Vibe Travel", layout="wide")

st.markdown("""
    <style>
    /* Tvinga ljust läge */
    :root { --primary-color: #007aff; }
    
    /* TABELLEN SOM INTE KAN STAPLAS */
    .notepad-table {
        width: 100%;
        border-collapse: collapse;
        table-layout: fixed; /* Låser bredden */
    }
    .notepad-table td {
        padding: 12px 5px;
        border-bottom: 0.5px solid #e5e5e5;
        vertical-align: middle;
        font-family: -apple-system, sans-serif;
    }
    .col-info { width: 55%; }
    .col-chk  { width: 15%; text-align: center; }
    .col-del  { width: 15%; text-align: center; }

    /* Snygga till checkboxarna så de inte ser ut som kaos */
    div[data-testid="stCheckbox"] label { 
        display: flex !important;
        justify-content: center !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    div[data-testid="stCheckbox"] label span { display: none !important; }
    
    /* Göm Streamlit-pynt */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ---
if 'trips' not in st.session_state:
    st.session_state.trips = {}
geolocator = Nominatim(user_agent="vibe_travel_v23")

# --- SIDEBAR ---
with st.sidebar:
    st.title("Mina Resor")
    trip_names = list(st.session_state.trips.keys())
    sel_trip = st.selectbox("Välj", options=trip_names) if trip_names else None
    if st.button("+ Ny resa"):
        st.session_state.add_mode = True
    if st.session_state.get('add_mode'):
        with st.form("new"):
            n = st.text_input("Vart ska ni?")
            t = st.text_input("Vilka reser? (t.ex. M, T)")
            if st.form_submit_button("Skapa"):
                st.session_state.trips[n] = {"places":[], "food":[], "travelers":[x.strip()[:1].upper() for x in t.split(",")] if t else ["M", "T"]}
                st.session_state.add_mode = False
                st.rerun()

# --- MAIN ---
if sel_trip:
    trip = st.session_state.trips[sel_trip]
    st.subheader(sel_trip)
    
    tabs = st.tabs(["📍 Platser", "🍝 Mat", "📸 Galleri"])

    with tabs[1]:
        with st.expander("➕ Lägg till i listan"):
            f_n = st.text_input("Maträtt")
            f_d = st.text_input("Notis")
            if st.button("Spara"):
                if f_n:
                    trip['food'].append({"item": f_n, "desc": f_d, "checks": {name: False for name in trip['travelers']}})
                    st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # HÄR ÄR DEN NYA STRATEGIN:
        # Vi bygger raden som en tabell i HTML men "petar in" checkboxarna i cellerna.
        for i, f in enumerate(trip['food']):
            # Vi skapar en behållare för varje rad
            row = st.container()
            with row:
                # Vi använder kolumner men med EXTREMT specifika mått som tvingar dem på rad
                # Genom att ha label="" och ingen text alls minimerar vi risken för stapling
                c_txt, c_m, c_t, c_del = st.columns([0.5, 0.15, 0.15, 0.2])
                
                with c_txt:
                    st.markdown(f"**{f['item']}**<br><small style='color:gray'>{f['desc']}</small>", unsafe_allow_html=True)
                
                # Person 1 (t.ex Micke)
                with c_m:
                    name1 = trip['travelers'][0]
                    f['checks'][name1] = st.checkbox("", value=f['checks'].get(name1, False), key=f"chk1_{i}")
                    st.markdown(f"<p style='font-size:10px; text-align:center; margin-top:-10px;'>{name1}</p>", unsafe_allow_html=True)
                
                # Person 2 (t.ex Tessan)
                with c_t:
                    if len(trip['travelers']) > 1:
                        name2 = trip['travelers'][1]
                        f['checks'][name2] = st.checkbox("", value=f['checks'].get(name2, False), key=f"chk2_{i}")
                        st.markdown(f"<p style='font-size:10px; text-align:center; margin-top:-10px;'>{name2}</p>", unsafe_allow_html=True)
                
                with c_del:
                    if st.button("🗑", key=f"del_{i}"):
                        trip['food'].pop(i)
                        st.rerun()
                
                st.markdown("<hr style='margin: 0px; opacity:0.1'>", unsafe_allow_html=True)

    with tabs[0]:
        q = st.text_input("Lägg till plats")
        if st.button("Sök"):
            loc = geolocator.geocode(q)
            if loc:
                trip['places'].append({"name":q, "lat":loc.latitude, "lon":loc.longitude})
                st.rerun()
        if trip['places']:
            m = folium.Map(location=[trip['places'][-1]['lat'], trip['places'][-1]['lon']], zoom_start=13)
            st_folium(m, width="100%", height=300)

else:
    st.info("Skapa en resa för att börja!")
