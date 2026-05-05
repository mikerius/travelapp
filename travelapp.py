import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

# --- 1. THE "FORCE-STAY-HORIZONTAL" CSS ---
st.set_page_config(page_title="Travel Notepad", layout="wide")

st.markdown("""
    <style>
    /* Tvinga ljust läge för Notepad-känsla */
    :root { background-color: white; }
    
    /* EN RIKTIG HTML-TABELL - Denna kan inte staplas vertikalt! */
    .notepad-row {
        display: flex;
        flex-direction: row;
        align-items: center;
        width: 100%;
        padding: 12px 0;
        border-bottom: 0.5px solid #e5e5e5;
    }
    .col-info { width: 50%; flex-shrink: 1; }
    .col-btn  { width: 16%; text-align: center; }
    
    /* Design för våra egna "checkbox-knappar" */
    .check-btn {
        display: inline-block;
        width: 32px;
        height: 32px;
        line-height: 32px;
        border-radius: 50%;
        border: 1px solid #d2d2d7;
        text-decoration: none;
        color: #1d1d1f;
        font-weight: 600;
        font-size: 0.8rem;
        background-color: white;
    }
    .checked {
        background-color: #34c759 !important;
        color: white !important;
        border-color: #34c759 !important;
    }
    
    /* Göm Streamlits egna knappar för att inte skapa kaos */
    .stButton>button { border: none !important; background: transparent !important; padding: 0 !important; }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ---
if 'trips' not in st.session_state:
    st.session_state.trips = {}

# --- FUNKTIONER FÖR ATT ÄNDRA STATUS ---
def toggle_check(trip_name, item_idx, person):
    current = st.session_state.trips[trip_name]['food'][item_idx]['checks'][person]
    st.session_state.trips[trip_name]['food'][item_idx]['checks'][person] = not current

# --- SIDEBAR ---
with st.sidebar:
    st.title("Mina Resor")
    trip_names = list(st.session_state.trips.keys())
    sel_trip = st.selectbox("Välj", options=trip_names) if trip_names else None
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
    tabs = st.tabs(["📍 Platser", "🍝 Mat"])

    with tabs[1]:
        with st.expander("➕ Lägg till mat"):
            f_n = st.text_input("Vad?")
            f_d = st.text_input("Beskrivning")
            if st.button("Spara rätt", use_container_width=True):
                if f_n:
                    trip['food'].append({"item": f_n, "desc": f_d, "checks": {name: False for name in trip['travelers']}})
                    st.rerun()

        st.write("")

        # --- HÄR BYGGER VI DEN STUMMA LISTAN ---
        for i, f in enumerate(trip['food']):
            # Vi skapar en rad med st.columns men vi lägger nästan ingen "vikt" i dem
            # för att inte trigga Streamlits responsivitet
            c_txt, c_m, c_t, c_del = st.columns([0.5, 0.16, 0.16, 0.18])
            
            with c_txt:
                st.markdown(f"**{f['item']}**<br><small style='color:gray'>{f['desc']}</small>", unsafe_allow_html=True)
            
            # Istället för st.checkbox använder vi st.button som ser ut som en cirkel
            # Detta är mer robust för horisontell layout
            for idx, name in enumerate(trip['travelers'][:2]):
                target_col = c_m if idx == 0 else c_t
                with target_col:
                    is_checked = f['checks'].get(name, False)
                    btn_label = f"● {name}" if is_checked else f"○ {name}"
                    if st.button(btn_label, key=f"btn_{i}_{name}"):
                        f['checks'][name] = not is_checked
                        st.rerun()
            
            with c_del:
                if st.button("🗑️", key=f"del_{i}"):
                    trip['food'].pop(i)
                    st.rerun()
            
            st.markdown("<hr style='margin:0; opacity:0.1'>", unsafe_allow_html=True)

    with tabs[0]:
        st.write("Kartan är här...")
        # (Behåll din gamla kart-kod här om du vill)

else:
    st.info("Välkommen! Skapa en resa för att börja.")
