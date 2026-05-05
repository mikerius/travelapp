import streamlit as st
import pandas as pd

st.set_page_config(page_title="Vibe Travel", layout="wide")

# --- CLEAN UI ---
st.markdown("""
    <style>
    .block-container { padding: 1rem !important; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

if 'trips' not in st.session_state:
    st.session_state.trips = {}

# --- SIDEBAR ---
with st.sidebar:
    st.title("🗺️ Resor")
    trip_names = list(st.session_state.trips.keys())
    sel_trip = st.selectbox("Välj resa", options=trip_names) if trip_names else None
    if st.button("+ Ny resa"):
        name = st.text_input("Destination", key="new_dest")
        folks = st.text_input("Vilka reser? (ex: M, T)", key="new_folks")
        if name:
            st.session_state.trips[name] = {
                "food": pd.DataFrame(columns=["Maträtt", "Notis"] + [f.strip()[:1].upper() for f in folks.split(",")]),
                "places": []
            }
            st.rerun()

# --- MAIN ---
if sel_trip:
    trip = st.session_state.trips[sel_trip]
    st.header(sel_trip)
    
    tab1, tab2 = st.tabs(["🍝 Bucket List", "📍 Platser"])

    with tab1:
        st.write("### Matlista")
        st.caption("Tips: Klicka direkt i rutorna för att checka av eller ändra text.")
        
        # HÄR ÄR DEN ENDA HORISONTELLA LÖSNINGEN
        # Vi använder en interaktiv tabell som är låst horisontellt
        edited_df = st.data_editor(
            trip["food"],
            num_rows="dynamic", # Detta skapar "Add row"-knappen automatiskt längst ner
            use_container_width=True,
            hide_index=True,
            key=f"editor_{sel_trip}"
        )
        
        # Spara ändringar
        trip["food"] = edited_df

    with tab2:
        st.write("Kartan och platserna kan vi fixa när listan väl sitter.")

else:
    st.info("Skapa en resa i menyn till vänster!")
