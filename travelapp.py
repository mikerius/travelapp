import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

# --- 1. CLEAN PRO DESIGN (WITHOUT TIMELINE) ---
st.set_page_config(page_title="Vibe Travel Pro", layout="wide", page_icon="📍")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
        background-color: #ffffff;
    }

    /* Minimalistiska kort för platser */
    .place-card {
        padding: 10px 15px;
        margin-bottom: 6px;
        border-radius: 8px;
        border: 1px solid #f0f0f0;
        background-color: #ffffff;
        border-left: 5px solid #ff5a5f; /* Standardfärg */
    }
    
    .place-name {
        font-weight: 600;
        font-size: 0.95rem;
        color: #1a1a1a;
    }
    
    .place-meta {
        font-size: 0.8rem;
        color: #717171;
        margin-top: 2px;
    }

    /* Tajta till matlistan ytterligare */
    .food-row {
        border-bottom: 1px solid #f5f5f5;
        padding: 4px 0;
    }

    /* Snyggare input-fält */
    .stTextInput input, .stSelectbox select {
        border-radius: 6px !important;
    }

    /* Ta bort onödigt margin i listor */
    [data-testid="stVerticalBlock"] > div {
        gap: 0rem !important;
        margin-bottom: -4px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIK ---
if 'trips' not in st.session_state:
    st.session_state.trips = {}
geolocator = Nominatim(user_agent="vibe_travel_v13")

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
            t = st.text_input("Deltagare (t.ex. Micke, Tessan)")
            if st.form_submit_button("Skapa"):
                st.session_state.trips[n] = {"places":[], "schedule":[], "food":[], "photos":[], "travelers":[x.strip() for x in t.split(",")] if t else ["Jag"]}
                st.session_state.add_mode = False
                st.rerun()

# --- CONTENT ---
if sel_trip:
    trip = st.session_state.trips[sel_trip]
    st.title(f"{sel_trip}")
    
    tabs = st.tabs(["📍 Platser", "📅 Itinerary", "🍝 Bucket List", "📸 Galleri"])

    with tabs[0]:
        c1, c2 = st.columns([1, 2])
        
        with c1:
            with st.expander("🔍 Lägg till ny plats", expanded=True):
                q = st.text_input("Sök plats...", label_visibility="collapsed")
                cat = st.selectbox("Typ", ["Sevärdhet", "Restaurang", "Bostad", "Annat"])
                note = st.text_input("Notering", placeholder="Kort info...")
                if st.button("Spara", use_container_width=True):
                    loc = geolocator.geocode(q, addressdetails=True)
                    if loc:
                        name = loc.raw.get('address', {}).get('amenity') or loc.address.split(',')[0]
                        colors = {"Sevärdhet":"#ff5a5f", "Restaurang":"#ffa000", "Bostad":"#008489", "Annat":"#767676"}
                        icons = {"Sevärdhet":"camera", "Restaurang":"cutlery", "Bostad":"home", "Annat":"info"}
                        trip['places'].append({"name":name, "lat":loc.latitude, "lon":loc.longitude, "note":note, "cat":cat, "color":colors[cat], "icon":icons[cat]})
                        st.rerun()

            st.write("")
            for i, p in enumerate(trip['places']):
                # Clean Card-design
                st.markdown(f"""
                <div class="place-card" style="border-left-color: {p['color']};">
                    <div class="place-name">{p['name']}</div>
                    <div class="place-meta">{p['cat']} • <i>{p['note']}</i></div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("Radera", key=f"dp{i}"):
                    trip['places'].pop(i); st.rerun()

        with c2:
            center = [trip['places'][-1]['lat'], trip['places'][-1]['lon']] if trip['places'] else [48.2082, 16.3738]
            m = folium.Map(location=center, zoom_start=14, tiles="CartoDB Positron")
            for p in trip['places']:
                folium.Marker([p['lat'], p['lon']], popup=p['name'], icon=folium.Icon(color="white", icon_color=p['color'], icon=p['icon'], prefix='fa')).add_to(m)
            st_folium(m, width="100%", height=650, use_container_width=True)

    with tabs[2]:
        st.subheader("Food Bucket List")
        c1, c2 = st.columns([1, 1])
        f_n = c1.text_input("Rätt", key="fn", label_visibility="collapsed", placeholder="Vad vill vi äta?")
        f_d = c2.text_input("Info", key="fd", label_visibility="collapsed", placeholder="Beskrivning...")
        if st.button("Lägg till i listan"):
            trip['food'].append({"item": f_n, "desc": f_d, "checks": {name: False for name in trip['travelers']}})
            st.rerun()
        
        st.write("---")
        for i, f in enumerate(trip['food']):
            col_txt, col_chk, col_btn = st.columns([3, 4, 0.5])
            with col_txt:
                st.markdown(f"**{f['item']}**: <span style='color:#777; font-size:0.85rem;'><i>{f['desc']}</i></span>", unsafe_allow_html=True)
            with col_chk:
                chk_cols = st.columns(len(trip['travelers']))
                for idx, name in enumerate(trip['travelers']):
                    trip['food'][i]['checks'][name] = chk_cols[idx].checkbox(name, value=f['checks'][name], key=f"f{i}{name}")
            with col_btn:
                if st.button("🗑", key=f"df{i}"):
                    trip['food'].pop(i); st.rerun()
            st.markdown("<hr style='margin: 0; opacity:0.05'>", unsafe_allow_html=True)

    with tabs[1]:
        st.subheader("Itinerary")
        with st.expander("+ Planera tid"):
            c1, c2, c3, c4 = st.columns([2,1,1,2])
            d, s, e, a = c1.date_input("Dag"), c2.time_input("Från"), c3.time_input("Till"), c4.text_input("Vad?")
            if st.button("Lägg till"): trip['schedule'].append({"date": d, "start": s, "end": e, "activity": a}); st.rerun()
        if trip['schedule']:
            df = pd.DataFrame(trip['schedule']).sort_values(["date", "start"])
            for date, group in df.groupby("date"):
                st.markdown(f"#### 🗓 {date.strftime('%A %d %B')}")
                for i, row in group.iterrows():
                    st.markdown(f"• **{row['start'].strftime('%H:%M')} - {row['end'].strftime('%H:%M')}**: {row['activity']}")

    with tabs[3]:
        up = st.file_uploader("Ladda upp bild", label_visibility="collapsed")
        if up: trip['photos'].append(up); st.rerun()
        if trip['photos']:
            cols = st.columns(4)
            for i, photo in enumerate(trip['photos']): cols[i%4].image(photo, use_container_width=True)

else:
    st.info("Börja med att skapa en resa i menyn till vänster! 🛫")