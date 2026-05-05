import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

# --- 1. PRO SAAS UI (MOBILE FIRST) ---
st.set_page_config(page_title="Vibe Travel", layout="wide", page_icon="📍")

st.markdown("""
    <style>
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

    /* Själva raden för maten */
    .food-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 5px 0;
        border-bottom: 1px solid #eee;
        gap: 10px;
    }

    /* Namn och beskrivning */
    .food-info {
        flex: 2;
        line-height: 1.2;
    }

    /* Initial-rutorna */
    .check-area {
        display: flex;
        gap: 15px; /* Avstånd mellan M och T */
        align-items: center;
    }

    /* Gör Streamlits checkboxar mindre och tajtare */
    [data-testid="stCheckbox"] {
        margin-bottom: -15px !important;
        width: 30px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONFIG & API ---
# Hämtar dina nycklar från Secrets
try:
    MAPBOX_TOKEN = st.secrets["MAPBOX_TOKEN"]
except:
    MAPBOX_TOKEN = None # Fallback om token saknas

geolocator = Nominatim(user_agent="vibe_travel_v15")

if 'trips' not in st.session_state:
    st.session_state.trips = {}

# --- SIDEBAR ---
with st.sidebar:
    st.title("🗺️ Resor")
    trip_names = list(st.session_state.trips.keys())
    sel_trip = st.selectbox("Välj resa", options=trip_names, label_visibility="collapsed") if trip_names else None
    if st.button("+ Ny resa", use_container_width=True):
        st.session_state.add_mode = True
    
    if st.session_state.get('add_mode'):
        with st.form("new_trip"):
            n = st.text_input("Destination")
            t = st.text_input("Vilka reser? (t.ex Micke, Tessan)")
            if st.form_submit_button("Skapa"):
                st.session_state.trips[n] = {"places":[], "schedule":[], "food":[], "photos":[], "travelers":[x.strip() for x in t.split(",")] if t else ["Micke"]}
                st.session_state.add_mode = False
                st.rerun()

# --- MAIN ---
if sel_trip:
    trip = st.session_state.trips[sel_trip]
    st.markdown(f"### {sel_trip}")
    
    tabs = st.tabs(["📍 Platser", "📅 Schema", "🍝 Mat", "📸 Bilder"])

    with tabs[0]:
        c1, c2 = st.columns([1, 2])
        with c1:
            with st.expander("➕ Lägg till", expanded=False):
                q = st.text_input("Sök...", placeholder="Namn på plats")
                cat = st.selectbox("Typ", ["Sevärdhet", "Restaurang", "Bostad", "Annat"])
                note = st.text_input("Notis", placeholder="T.ex 'Bästa pizzan'")
                if st.button("Spara plats", use_container_width=True):
                    loc = geolocator.geocode(q)
                    if loc:
                        colors = {"Sevärdhet":"#ff5a5f", "Restaurang":"#ffa000", "Bostad":"#008489", "Annat":"#767676"}
                        icons = {"Sevärdhet":"camera", "Restaurang":"cutlery", "Bostad":"home", "Annat":"info"}
                        trip['places'].append({"name":q, "lat":loc.latitude, "lon":loc.longitude, "note":note, "cat":cat, "color":colors[cat], "icon":icons[cat]})
                        st.rerun()
            
            for i, p in enumerate(trip['places']):
                with st.expander(f"📍 {p['name']}"):
                    st.write(f"{p['cat']}: {p['note']}")
                    if st.button("Radera", key=f"dp{i}"): trip['places'].pop(i); st.rerun()

        with c2:
            center = [trip['places'][-1]['lat'], trip['places'][-1]['lon']] if trip['places'] else [48.2082, 16.3738]
            # Använder Mapbox om token finns, annars standard
            tiles = "CartoDB Positron"
            if MAPBOX_TOKEN:
                tiles = f"https://api.mapbox.com/styles/v1/mapbox/streets-v11/tiles/{{z}}/{{x}}/{{y}}?access_token={MAPBOX_TOKEN}"
            
            m = folium.Map(location=center, zoom_start=13, tiles=tiles, attr="Mapbox")
            for p in trip['places']:
                folium.Marker([p['lat'], p['lon']], popup=p['name'], icon=folium.Icon(color="white", icon_color=p['color'], icon=p['icon'], prefix='fa')).add_to(m)
            st_folium(m, width="100%", height=400, use_container_width=True)

    with tabs[1]:
        st.write("#### 📅 Din tidsplan")
        with st.expander("➕ Lägg till i schema"):
            d = st.date_input("Dag")
            t = st.time_input("Tid")
            act = st.text_input("Vad händer?")
            if st.button("Spara händelse"):
                trip['schedule'].append({"date": str(d), "time": str(t), "activity": act})
                st.rerun()
        
        for item in sorted(trip['schedule'], key=lambda x: (x['date'], x['time'])):
            st.info(f"**{item['date']} kl {item['time'][:5]}**: {item['activity']}")

    with tabs[2]:
        st.write("#### 🍴 Mat-bucketlist")
        
        with st.expander("➕ Lägg till ny rätt"):
            f_n = st.text_input("Rätt")
            f_d = st.text_input("Beskrivning")
            if st.button("Spara", use_container_width=True):
                if f_n:
                    trip['food'].append({"item": f_n, "desc": f_d, "checks": {name: False for name in trip['travelers']}})
                    st.rerun()

        st.write("") # Lite luft efter expandern

        for i, f in enumerate(trip['food']):
            # Vi skapar en rad med tre fasta kolumner som INTE bryts på mobil
            col_txt, col_chk, col_btn = st.columns([0.5, 0.4, 0.1])
            
            with col_txt:
                # Maträtt + kursiv beskrivning på samma rad/tajt under
                st.markdown(f"**{f['item']}** <span style='color:gray; font-size:0.8rem; font-style:italic;'>{f['desc']}</span>", unsafe_allow_html=True)
            
            with col_chk:
                # Vi lägger initialerna horisontellt
                c_idx = st.columns(len(trip['travelers']))
                for idx, name in enumerate(trip['travelers']):
                    initial = name[0].upper()
                    trip['food'][i]['checks'][name] = c_cols[idx].checkbox(initial, value=f['checks'][name], key=f"f{i}{name}")
            
            with col_btn:
                # En liten papperskorg längst ut
                if st.button("🗑️", key=f"df{i}"):
                    trip['food'].pop(i)
                    st.rerun()

    with tabs[3]:
        st.write("#### 📸 Bilder")
        img = st.file_uploader("Ladda upp", type=['jpg', 'png'])
        if img: trip['photos'].append(img); st.success("Uppladdad!")
        if trip['photos']:
            cols = st.columns(3)
            for i, p in enumerate(trip['photos']): cols[i%3].image(p, use_container_width=True)

else:
    st.info("Skapa en resa för att börja!")
