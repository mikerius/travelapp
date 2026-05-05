import streamlit as st

# --- 1. THE TRULY STATIC HTML (NO STREAMLIT WIDGETS IN ROWS) ---
st.set_page_config(page_title="Vibe Travel", layout="wide")

st.markdown("""
    <style>
    :root { background-color: white; }
    .block-container { padding-top: 1rem !important; }
    
    /* EN RIKTIG TABELL - STUM OCH HORISONTELL */
    .notepad-table {
        width: 100%;
        border-collapse: collapse;
        table-layout: fixed;
    }
    .notepad-table td {
        padding: 12px 4px;
        border-bottom: 0.5px solid #e5e5e5;
        vertical-align: middle;
    }
    .col-info { width: 60%; }
    .col-chk  { width: 15%; text-align: center; }
    
    /* Cirklar för status */
    .circle {
        height: 18px;
        width: 18px;
        border-radius: 50%;
        display: inline-block;
        border: 1px solid #ccc;
    }
    .checked { 
        background-color: #34c759; 
        border-color: #34c759; 
        box-shadow: inset 0 0 0 2px white;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ---
if 'trips' not in st.session_state:
    st.session_state.trips = {}

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
            t = st.text_input("Resenärer (ex: M, T)")
            if st.form_submit_button("Skapa"):
                st.session_state.trips[n] = {
                    "food": [], 
                    "travelers": [x.strip()[:1].upper() for x in t.split(",")] if t else ["M", "T"]
                }
                st.session_state.add_mode = False
                st.rerun()

# --- MAIN ---
if sel_trip:
    trip = st.session_state.trips[sel_trip]
    st.subheader(sel_trip)
    
    # --- INPUT DEL ---
    with st.expander("➕ Lägg till mat"):
        f_n = st.text_input("Vad?")
        f_d = st.text_input("Notis")
        if st.button("Spara"):
            if f_n:
                trip['food'].append({"item": f_n, "desc": f_d, "checks": {name: False for name in trip['travelers']}})
                st.rerun()

    # --- LISTAN (REN HTML) ---
    if trip['food']:
        html_table = "<table class='notepad-table'>"
        for i, f in enumerate(trip['food']):
            # Bygg cirklarna
            circles = ""
            for name in trip['travelers'][:2]:
                is_checked = f['checks'].get(name, False)
                status_class = "circle checked" if is_checked else "circle"
                circles += f"<td class='col-chk'><div class='{status_class}'></div><br><small>{name}</small></td>"
            
            html_table += f"""
                <tr>
                    <td class='col-info'>
                        <b>{i+1}. {f['item']}</b><br>
                        <span style='color:gray; font-size:0.8rem;'>{f['desc']}</span>
                    </td>
                    {circles}
                </tr>
            """
        html_table += "</table>"
        st.markdown(html_table, unsafe_allow_html=True)

        # --- KONTROLLPANEL (Längst ner, för att faktiskt ändra data) ---
        st.markdown("<br><br>", unsafe_allow_html=True)
        with st.container():
            st.write("---")
            st.caption("Ändra status:")
            c1, c2, c3 = st.columns([1, 1, 1])
            row_num = c1.number_input("Rad", min_value=1, max_value=len(trip['food']), step=1)
            who = c2.selectbox("Vem?", options=trip['travelers'])
            
            # Action-knappar
            btn_col1, btn_col2 = st.columns(2)
            if btn_col1.button("Check / Uncheck", use_container_width=True):
                trip['food'][row_num-1]['checks'][who] = not trip['food'][row_num-1]['checks'][who]
                st.rerun()
            if btn_col2.button("Ta bort rad", use_container_width=True):
                trip['food'].pop(row_num-1)
                st.rerun()
    else:
        st.info("Listan är tom. Lägg till något ovan!")

else:
    st.info("Välkommen! Skapa en resa i sidomenyn.")
