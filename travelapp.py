import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

# --- CONFIG & CSS ---
st.set_page_config(page_title="Vibe Travel Pro", layout="wide", page_icon="📍")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
    .place-card { padding: 10px; margin-bottom: 6px; border-radius: 8px; border: 1px solid #f0f0f0; border-left: 5px solid #ff5a5f; }
    .stButton>button { border-radius: 6px; background-color: white; border: 1px solid #e0e0e0; }
    [data-testid="stVerticalBlock"] > div { gap: 0rem !important; margin-bottom: -4px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALIZE SESSION STATE ---
# I molnet vill vi att datan ska bestå, så vi förbereder för kopplingar här
if 'trips' not in st.session_state:
    st.session_state.trips = {}

geolocator = Nominatim(user_agent="vibe_travel_v14")

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 🗺️ Mina Resor")
    trip_names = list(st.session_state.trips.keys())
    sel_trip = st.selectbox("Välj resa", options=trip_names, label_visibility="collapsed") if trip_names else None
    
    if st.button("+ Ny resa", use_container_width=True):
        st.session_state.add_mode = True
    
    if st.session_state.get('add_mode'):
        with st.form("new_trip"):
            n = st.text_input("Vart ska ni?")
            t = st.text_input("Vilka reser?")
            if st.form_submit_button("Skapa"):
                st.session_state.trips[n] = {"places":[], "schedule":[], "food":[], "photos":[], "travelers":[x.strip() for x in t.split(",")] if t else ["Jag"]}
                st.session_state.add_mode = False
                st.rerun()

# --- MAIN APP ---
if sel_trip:
    trip = st.session_state.trips[sel_trip]
    st.title(f"{sel_trip}")
    
    tabs = st.tabs(["📍 Platser", "📅 Itinerary", "🍝 Bucket List", "📸 Galleri"])

    with tabs[0]:
        c1, c2 = st.columns([1, 2.5])
        with c1:
            with st.expander("🔍 Lägg till plats", expanded=True):
                q = st.text_input("Sök...", label_visibility="collapsed")
                cat = st.selectbox("Typ", ["Sevärdhet", "Restaurang", "Bostad", "Annat"])
                note = st.text_input("Info", placeholder="Kort notering...")
                if st.button("Spara"):
                    loc = geolocator.geocode(q, addressdetails=True)
                    if loc:
                        name = loc.raw.get('address', {}).get('amenity') or loc.address.split(',')[0]
                        colors = {"Sevärdhet":"#ff5a5f", "Restaurang":"#ffa000", "Bostad":"#008489", "Annat":"#767676"}
                        icons = {"Sevärdhet":"camera", "Restaurang":"cutlery", "Bostad":"home", "Annat":"info"}
                        trip['places'].append({"name":name, "lat":loc.latitude, "lon":loc.longitude, "note":note, "cat":cat, "color":colors[cat], "icon":icons[cat]})
                        st.rerun()
            for i, p in enumerate(trip['places']):
                st.markdown(f'<div class="place-card" style="border-left-color: {p["color"]};"><b>{p["name"]}</b><br><small>{p["cat"]} • {p["note"]}</small></div>', unsafe_allow_html=True)
                if st.button("Radera", key=f"dp{i}"): trip['places'].pop(i); st.rerun()

        with c2:
            center = [trip['places'][-1]['lat'], trip['places'][-1]['lon']] if trip['places'] else [48.2082, 16.3738]
            # HÄR KAN VI SEN BYTA TILL MAPBOX-STIL
            m = folium.Map(location=center, zoom_start=14, tiles="CartoDB Positron")
            for p in trip['places']:
                folium.Marker([p['lat'], p['lon']], popup=p['name'], icon=folium.Icon(color="white", icon_color=p['color'], icon=p['icon'], prefix='fa')).add_to(m)
            st_folium(m, width="100%", height=600, use_container_width=True)

    # --- BUCKET LIST ---
    with tabs[2]:
        st.subheader("Food Bucket List")
        c1, c2 = st.columns([1, 1])
        f_n = c1.text_input("Rätt", key="fn", label_visibility="collapsed", placeholder="Rätt...")
        f_d = c2.text_input("Beskrivning", key="fd", label_visibility="collapsed", placeholder="Info...")
        if st.button("Lägg till"):
            trip['food'].append({"item": f_n, "desc": f_d, "checks": {name: False for name in trip['travelers']}})
            st.rerun()
        for i, f in enumerate(trip['food']):
            col_txt, col_chk, col_btn = st.columns([3, 4, 0.5])
            with col_txt: st.markdown(f"**{f['item']}**: <small><i>{f['desc']}</i></small>", unsafe_allow_html=True)
            with col_chk:
                chk_cols = st.columns(len(trip['travelers']))
                for idx, name in enumerate(trip['travelers']):
                    trip['food'][i]['checks'][name] = chk_cols[idx].checkbox(name, value=f['checks'][name], key=f"f{i}{name}")
            if col_btn.button("🗑", key=f"df{i}"): trip['food'].pop(i); st.rerun()
            st.markdown("<hr style='margin:0; opacity:0.1'>", unsafe_allow_html=True)

    # --- ÖVRIGA ---
    with tabs[1]:
        if trip['schedule']:
            df = pd.DataFrame(trip['schedule'])
            st.write(df) # Förenklat för nu
        else: st.info("Planera ditt schema här!")
    with tabs[3]:
        st.info("Galleriet aktiveras när vi kopplat databasen!")
else:
    st.info("Skapa en resa för att börja planera! 🛫")
