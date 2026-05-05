import streamlit as st
import pandas as pd

# --- 1. CONFIG & ULTRA-CLEAN CSS ---
st.set_page_config(page_title="Vibe Travel", layout="wide")

st.markdown("""
    <style>
    /* Notepad-vibe: Vit bakgrund och ren text */
    :root { --primary-color: #007aff; }
    .block-container { padding: 1rem !important; max-width: 600px !important; }
    
    /* Tvinga horisontell layout för matlistan */
    [data-testid="column"] {
        flex: 1 1 0px !important;
        min-width: 0px !important;
    }
    div[data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important;
        align-items: center !important;
        border-bottom: 0.5px solid #eee;
        padding: 5px 0;
    }
    
    /* Göm Streamlit-pynt */
    div[data-testid="stCheckbox"] label span { display: none; }
    .stButton > button { border: none; background: transparent; padding: 0; color: #8e8e93; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA INITIALIZATION ---
if 'trips' not in st.session_state:
    st.session_state.trips = {}

# --- SIDEBAR: NY RESA (BUG-FIX) ---
with st.sidebar:
    st.title("🗺️ Resor")
    
    # Val av existerande resa
    trip_names = list(st.session_state.trips.keys())
    sel_trip = st.selectbox("Välj resa", options=trip_names, label_visibility="collapsed") if trip_names else None
    
    st.divider()
    
    # Skapa ny resa - nu med st.form för att undvika nollställning
    with st.expander("+ Skapa ny resa", expanded=not trip_names):
        with st.form("trip_creator", clear_on_submit=True):
            new_n = st.text_input("Vart?")
            new_t = st.text_input("Vem? (ex: M, T)")
            submit = st.form_submit_button("Skapa")
            
            if submit and new_n:
                st.session_state.trips[new_n] = {
                    "food": [],
                    "travelers": [x.strip()[:1].upper() for x in new_t.split(",")] if new_t else ["M", "T"]
                }
                st.rerun()

# --- MAIN APP ---
if sel_trip:
    trip = st.session_state.trips[sel_trip]
    st.subheader(sel_trip)
    
    # Input för ny mat (Notepad-stil)
    with st.expander("➕ Lägg till i matlistan"):
        c1, c2 = st.columns([2, 1])
        f_n = c1.text_input("Maträtt", placeholder="Schnitzel...")
        f_d = c2.text_input("Notis", placeholder="Gott!")
        if st.button("Spara", use_container_width=True):
            if f_n:
                trip['food'].append({"item": f_n, "desc": f_d, "checks": {name: False for name in trip['travelers']}})
                st.rerun()

    st.write("") # Spacer

    # --- MATLISTAN (DEN HORISONTELLA) ---
    for i, f in enumerate(trip['food']):
        # Vi använder en extremt tajt kolumn-layout
        # Namn/Desc får 60%, sen 15% per person, sen 10% för del
        cols = st.columns([0.6, 0.15, 0.15, 0.1])
        
        with cols[0]:
            st.markdown(f"**{f['item']}** \n<small style='color:gray'>{f['desc']}</small>", unsafe_allow_html=True)
        
        # Checkboxar (Nu klickbara direkt på bokstaven!)
        for idx, name in enumerate(trip['travelers'][:2]):
            with cols[idx+1]:
                # Vi visar bokstaven och checkboxen tajt
                f['checks'][name] = st.checkbox(name, value=f['checks'].get(name, False), key=f"chk_{sel_trip}_{i}_{name}")
        
        with cols[3]:
            if st.button("✕", key=f"del_{i}"):
                trip['food'].pop(i)
                st.rerun()

else:
    st.info("Börja med att skapa en resa i sidomenyn!")
