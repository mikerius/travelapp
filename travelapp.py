import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

# --- 1. MINIMALIST NOTEPAD UI ---
st.set_page_config(page_title="Vibe Travel", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; background-color: white; }
    
    /* Rad-design för Notepad-känsla */
    .item-row {
        padding: 10px 0;
        border-bottom: 0.5px solid #eee;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    /* Göm Streamlits standard-knappar och gör dem till små diskreta texter/ikoner */
    .stButton > button {
        border: none !important;
        background: transparent !important;
        color: #007aff !important;
        padding: 0px 5px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }
    
    .delete-btn > div > button { color: #ff3b30 !important; font-size: 12px !important; }

    /* Fixa marginaler */
    .block-container { padding-top: 1rem !important; max-width: 500px !important; }
    [data-testid="stVerticalBlock"] { gap: 0rem !important; }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA LOGIC ---
if 'trips' not in st.session_state:
    st.session_state.trips = {}

# --- SIDEBAR ---
with st.sidebar:
    st.title("🗺️ Resor")
    trip_names = list(st.session_state.trips.keys())
    sel_trip = st.selectbox("Välj", options=trip_names) if trip_names else None
    if st.button("+ Skapa ny resa"):
        st.session_state.add_mode = True
    
    if st.session_state.get('add_mode'):
        with st.form("new_trip"):
            n = st.text_input("Destination")
            t = st.text_input("Vem? (ex: Micke, Tessan)")
            if st.form_submit_button("Spara"):
                # Vi sparar hela namnet men visar bara första bokstaven i listan
                st.session_state.trips[n] = {
                    "food": [], "places": [], 
                    "travelers": [x.strip() for x in t.split(",")] if t else ["Micke", "Tessan"]
                }
                st.session_state.add_mode = False
                st.rerun()

# --- MAIN ---
if sel_trip:
    trip = st.session_state.trips[sel_trip]
    st.subheader(sel_trip)
    
    tabs = st.tabs(["🍝 Mat", "📍 Platser", "📸 Galleri"])

    # --- FLIK: MAT ---
    with tabs[0]:
        with st.expander("➕ Lägg till ny rätt"):
            f_n = st.text_input("Vad?")
            f_d = st.text_input("Notis")
            if st.button("Spara i listan", use_container_width=True):
                if f_n:
                    trip['food'].append({"item": f_n, "desc": f_d, "checks": {name: False for name in trip['travelers']}})
                    st.rerun()

        st.write("") # Spacer

        for i, f in enumerate(trip['food']):
            # Vi skapar en rad med horisontell layout som INTE bryts
            # Col 1: Namn, Col 2: Person 1, Col 3: Person 2, Col 4: Radera
            c1, c2, c3, c4 = st.columns([0.5, 0.15, 0.15, 0.15])
            
            with c1:
                st.markdown(f"**{f['item']}**")
                if f['desc']: st.caption(f['desc'])
            
            # Person-knappar (Toggle)
            for idx, name in enumerate(trip['travelers'][:2]):
                with (c2 if idx == 0 else c3):
                    is_checked = f['checks'].get(name, False)
                    # Vi använder symboler: ● för ifylld, ○ för tom
                    icon = "●" if is_checked else "○"
                    if st.button(f"{icon}{name[0]}", key=f"t_{i}_{name}"):
                        f['checks'][name] = not is_checked
                        st.rerun()
            
            with c4:
                st.markdown('<div class="delete-btn">', unsafe_allow_html=True)
                if st.button("✕", key=f"d_{i}"):
                    trip['food'].pop(i)
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("---")

    # --- FLIK: PLATSER ---
    with tabs[1]:
        q = st.text_input("Sök plats")
        if st.button("Lägg till"):
            loc = Nominatim(user_agent="vibe_v26").geocode(q)
            if loc:
                trip['places'].append({"name": q, "lat": loc.latitude, "lon": loc.longitude})
                st.rerun()
        if trip['places']:
            m = folium.Map(location=[trip['places'][-1]['lat'], trip['places'][-1]['lon']], zoom_start=12)
            st_folium(m, width="100%", height=300)

else:
    st.info("Välkommen! Skapa en resa i menyn.")
