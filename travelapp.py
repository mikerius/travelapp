import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

st.set_page_config(page_title="Vibe Travel", layout="wide")

# --- 1. CSS (ENDAST FÖR ATT TA BORT ONÖDIGT MELLANRUM) ---
st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; }
    .stCheckbox { margin-bottom: -15px !important; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ---
if 'trips' not in st.session_state:
    st.session_state.trips = {}

geolocator = Nominatim(user_agent="vibe_v25")

# --- SIDEBAR ---
with st.sidebar:
    st.title("Mina Resor")
    trip_names = list(st.session_state.trips.keys())
    sel_trip = st.selectbox("Välj resa", options=trip_names) if trip_names else None
    if st.button("+ Ny resa"):
        st.session_state.add_mode = True
    
    if st.session_state.get('add_mode'):
        with st.form("new_trip"):
            n = st.text_input("Destination")
            t = st.text_input("Vilka reser? (ex: M, T)")
            if st.form_submit_button("Spara"):
                st.session_state.trips[n] = {
                    "food": [], "places": [], "travelers": [x.strip()[:1].upper() for x in t.split(",")] if t else ["M", "T"]
                }
                st.session_state.add_mode = False
                st.rerun()

# --- MAIN ---
if sel_trip:
    trip = st.session_state.trips[sel_trip]
    st.subheader(sel_trip)
    
    tabs = st.tabs(["📍 Platser", "🍝 Mat", "📸 Galleri"])

    # --- FLIK: MAT (DEN VI SKA FIXA NU) ---
    with tabs[1]:
        with st.expander("➕ Lägg till i listan"):
            f_n = st.text_input("Maträtt")
            f_d = st.text_input("Notis")
            if st.button("Spara"):
                if f_n:
                    trip['food'].append({"item": f_n, "desc": f_d, "checks": {name: False for name in trip['travelers']}})
                    st.rerun()

        st.write("---")

        for i, f in enumerate(trip['food']):
            # VI ANVÄNDER BARA EN ENDA RAD TEXT
            # Vi skapar status-ikoner: ✅ för klar, ⚪ för inte klar
            status_str = ""
            for name in trip['travelers']:
                icon = "✅" if f['checks'].get(name) else "⚪"
                status_str += f"{icon} {name}  "

            # Vi skriver ut allt som en enda textsträng. Detta KAN inte bli vertikalt.
            st.markdown(f"**{i+1}. {f['item']}** | {status_str}")
            if f['desc']:
                st.caption(f"_{f['desc']}_")
            
            # Kontroller för varje rad
            c1, c2, c3 = st.columns([1, 1, 1])
            if c1.button(f"Ändra {trip['travelers'][0]}", key=f"t1_{i}"):
                p = trip['travelers'][0]
                trip['food'][i]['checks'][p] = not trip['food'][i]['checks'].get(p)
                st.rerun()
            
            if len(trip['travelers']) > 1:
                if c2.button(f"Ändra {trip['travelers'][1]}", key=f"t2_{i}"):
                    p = trip['travelers'][1]
                    trip['food'][i]['checks'][p] = not trip['food'][i]['checks'].get(p)
                    st.rerun()
            
            if c3.button("🗑️", key=f"del_{i}"):
                trip['food'].pop(i)
                st.rerun()
            
            st.write("---")

    # --- FLIK: PLATSER ---
    with tabs[0]:
        q = st.text_input("Sök plats")
        if st.button("Sök och lägg till"):
            loc = geolocator.geocode(q)
            if loc:
                trip['places'].append({"name": q, "lat": loc.latitude, "lon": loc.longitude})
                st.rerun()
        if trip['places']:
            m = folium.Map(location=[trip['places'][-1]['lat'], trip['places'][-1]['lon']], zoom_start=12)
            for p in trip['places']:
                folium.Marker([p['lat'], p['lon']], popup=p['name']).add_to(m)
            st_folium(m, width="100%", height=300)

    # --- FLIK: GALLERI ---
    with tabs[2]:
        st.write("Galleri")

else:
    st.info("Välkommen! Skapa en resa i menyn.")
