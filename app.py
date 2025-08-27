

#Imports

#Streamlit
import streamlit as st
st.set_page_config(layout="wide")

#Util files
import data_utils_
import ui_utils_

#== Global Stuff ==

#Grab gamelist from steam for game ids 
steam_ids = data_utils_.steamIDListLoad()

#==== List of cursors that have been called so user can navigate backwards
if 'cursorList' not in st.session_state:
    st.session_state.cursorList = ["*"]

#==== The cursor of the currently displayed reviews
if 'cursor' not in st.session_state:
    st.session_state.cursor = st.session_state.cursorList[0]

# == Style Sheet ================================================
with open("assets/styles.css") as s:
    st.markdown(f"<style>{s.read()}</style>", unsafe_allow_html=True)

# == Defining Columns ===========================================
blank1, col1, col2, blank2 = st.columns([0.05, 0.25, 0.65, 0.05])

#-------------------------------------------------------------------------------------------------------------------------
# ====== Searching Column ======================================= 
with col1:

    # == Search =================================================
    # search bar to search and retrieve options for games to view
    with st.container(key="searchbar", height = 90):
        st.html("<div style ='padding: 0; margin: 0; text-align: center; padding: 0; font-size: 16px;'> Search </div>")
        st.text_input(label = "", key="search", placeholder="Enter game name here...", label_visibility="collapsed")
        st.markdown("<style> input {font-size: 12px !important} </style> ", unsafe_allow_html=True,)
        
    # == Quick Results / Trending items==========================================
    # A list of ~10 items from the steam store that are returned 
    # from a simple request
    with st.container(key="quickResults", height=180):

       ui_utils_.trendingItems(st.session_state.search)

    # == Full Results ==========================================
    # A  complete list of all items from the steam store id list
    # that contain the searched substring
    with st.container(key="fullResults", height = 250):
        
        ui_utils_.generateFullResults(st.session_state.search, steam_ids)

#-------------------------------------------------------------------------------------------------------------------------
# ====== Main Panel Column ======================================
with col2:
     
    #Check for a query parameter
    with st.container(key="mainPanel", height = 540):

        if 'gID' in st.query_params:

            id = st.query_params.get("gID")
            id = str.split(id, ",")[0]

            ui_utils_.generateMainPage(id)
        
        else:
            
            landing = data_utils_.storeQuickResults("")

            if landing:
                id = landing[0].get('id')
                ui_utils_.generateMainPage(str(id))
            else:
                ui_utils_.generateErrorPage()
