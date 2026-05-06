import streamlit as st
from streamlit_option_menu import option_menu # Installera med: pip install streamlit-option-menu
import folium # För kartan
from streamlit_folium import st_folium

# --- APP-KONFIGURATION ---
st.set_page_config(page_title="Vibe Travel", layout="centered")

# CSS för att få det att se ut som en riktig mobilapp
st.markdown("""
    <style>
    /* Ta bort Streamlit-menyer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Mobil-anpassning av containern */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 5rem;
    }

    /* Styling för de vertikala "korten" i Flik 2 */
    .travel-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        border-left: 5px solid #ccc;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .day-header {
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 10px;
        color: #333;
        display: flex;
        align-items: center;
    }
    .dot {
        height: 12px;
        width: 12px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- NAVBAR (BOTTMENY) ---
# Detta skapar de tre flikarna vi visualiserat
selected = option_menu(
    menu_title=None,
    options=["Karta", "Schema", "Matlista"],
    icons=["map", "calendar-event", "list-check"], # Bootstrap icons
    menu_icon="cast",
    default_index=1,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#fafafa"},
        "icon": {"color": "gray", "font-size": "20px"}, 
        "nav-link": {"font-size": "14px", "text-align": "center", "margin":"0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "#e0e0e0", "color": "black"},
    }
)

# --- INNEHÅLL PER FLIK ---

if selected == "Karta":
    st.subheader("Flik 1: Karta")
    # Skapa en enkel karta centrerad på Wien som exempel
    m = folium.Map(location=[48.2082, 16.3738], zoom_start=13)
    folium.Marker([48.2082, 16.3738], popup="Wien", icon=folium.Icon(color='blue')).add_to(m)
    st_folium(m, width=700, height=500)

elif selected == "Schema":
    st.subheader("Flik 2: Sparade & Schema")
    
    st.write("### Sparade (ej schemalagda)")
    st.markdown('<div class="travel-card">📍 Wien national-museum</div>', unsafe_allow_html=True)
    st.markdown('<div class="travel-card">📍 Gröna Lund</div>', unsafe_allow_html=True)
    st.markdown('<div class="travel-card">📍 Karlskirche</div>', unsafe_allow_html=True)

    st.write("---")
    
    st.markdown('### Schema')
    
    # Torsdag
    st.markdown('<div class="day-header"><span class="dot" style="background-color: blue;"></span> Torsdag 14 Maj</div>', unsafe_allow_html=True)
    st.markdown('<div class="travel-card" style="border-left-color: blue;">🍴 Wienerschnitzel</div>', unsafe_allow_html=True)
    
    # Söndag
    st.markdown('<div class="day-header"><span class="dot" style="background-color: gold;"></span> Söndag 17 Maj</div>', unsafe_allow_html=True)
    st.markdown('<div class="travel-card" style="border-left-color: gold;">🏰 Stockholms slott</div>', unsafe_allow_html=True)
    
    if st.button("+ Lägg till dag"):
        st.toast("Funktion kommer snart!")

elif selected == "Matlista":
    st.subheader("Flik 3: Matlista")
    
    # Enkel interaktiv lista med checkboxar
    col1, col2 = st.columns([0.8, 0.2])
    
    mat_rader = [
        ("1. Wienerschnitzel", "Kalvrätt med potatissallad"),
        ("2. Apfelstrudel", "Äppelpaj med glass"),
        ("3. Baconkrasse", "Baconhis med fioh"),
        ("4. Friesdrope", "Potatissallad")
    ]
    
    for mat, info in mat_rader:
        c1, c2, c3 = st.columns([0.6, 0.2, 0.2])
        with c1:
            st.markdown(f"**{mat}**\n\n*{info}*")
        with c2:
            st.checkbox("M", key=mat+"M")
        with c3:
            st.checkbox("T", key=mat+"T")
        st.divider()
