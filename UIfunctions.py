import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timezone
import pandas as pd
import functions
import base64

#---------------------------------------------------------------------------------------------------------
def generateFullResults(search, steam_ids):

    st.html(f"""<div style ='padding: 0; margin: 0; padding: 0; font-size: 16px; font-weight: bold;'> 
                All Content: {search}
             </div>""")

    ## == If nothing has been searched display the top ten items
    if search == None or search == "":
        items =  steam_ids[3:].head(10)
    else:
        items =  steam_ids[steam_ids['Title'].str.contains(search, case=False)]
    

    # == Generate links to each url parameter for the items
    buttons = ""

    # == Create list of buttons for this section
    for i in range(len(items)):
        buttons += f" <a href='?gID={items.iloc[i]['id']}' class= 'Results-Button'> {items.iloc[i]['Title']} </a> "
        
    # == Display the buttons in a masonry like style forming 2 
    # columns with unequal row heights.
    st.html(f" <div class='masonry'> {buttons} </div> ")

#---------------------------------------------------------------------------------------------------------

def trendingItems(search):

    st.html(f"""<div style ='padding: 0; margin: 0; padding: 0; font-size: 16px; font-weight: bold;'> 
                Trending: {search}
             </div>""")

    quickResults = functions.storeQuickResults(search.lower())

    if not quickResults:
        st.warning("No results found.")
        return

    # == Rows ==============================================   
    qRchildren1 = ""
    qRchildren2 = ""

    # == Generate Row 1 ====
    for i in range(int((len(quickResults)/2))):
        qRchildren1 += f""" <div style="display: inline-block; text-align: center;">
                                <a href='?gID={quickResults[i]['id']}'>
                                    <img src='{quickResults[i]['tiny_image']}' width='125' style='cursor:pointer; margin: 3px;' />
                                </a>
                            </div> """
    # == Generate Row 2 ====
    for i in range(int(len(quickResults)/2) + 1, len(quickResults)):
        qRchildren2 += f""" <div style="display: inline-block; text-align: center;">
                                <a href='?gID={quickResults[i]['id']}'>
                                    <img src='{quickResults[i]['tiny_image']}' width='125' style='cursor:pointer; margin: 3px;' />
                                </a>
                            </div> """
                                
                
    ###Wrap results up into a two row container to scroll through
    st.html(f"""<div style = 'display: inline-flex' > {qRchildren1} </div> <br> <div style = 'display: inline-flex' > {qRchildren2} </div>""")

#---------------------------------------------------------------------------------------------------------

def activePlayerPlot(id, gameTitle):

    playerCountData = functions.steamChartsDataFetch(id)

    #Check if the data is the correct type before trying to create plotly
    if playerCountData.empty:
        st.warning("There is currently no player time series data associated with this item")
    elif playerCountData is None:
        st.warning("There was a problem retrieving data. Please try again later or check your network connection.")
    elif isinstance(playerCountData, pd.DataFrame):

        playerCountData['Tstamp'] = pd.to_datetime(playerCountData['Tstamp'], unit = 'ms')

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=playerCountData.Tstamp,
            y=playerCountData.PlayerCount,
            mode='lines',
            name='trace 0',
            line=dict(
                color='#cc6633',
                width=1,
                dash='solid',
                shape='linear',
                simplify=True
            ),
            error_x=dict(
                visible=False,
                type='percent',
                symmetric=True,
                value=10,
                color='#636efa',
                thickness=2,
                width=4
            ),
            error_y=dict(
                visible=False
            ),
            hoverinfo='y',
            connectgaps=False,
            fill='none',
            hoveron='points',
            hoverlabel=dict(
                namelength=15,
                font=dict(family='Arial, sans-serif', size=13),
                align='auto'
            ),
            opacity=1,
            showlegend=True,
            visible=True
        ))

        fig.update_layout(
            title=dict(
                text=f'{gameTitle}: Active Player Count',
                font=dict(size=14, family='Times New Roman', color='white'),
                xanchor='center',
                x = 0.5,
                automargin=True,
                pad = dict(t = 15, b = 15)
            ),
            xaxis=dict(
                type='date',
                showline=False,
                linecolor="#0076b6",
                linewidth=0.5,
                showgrid=False,
                zeroline=False,
                tickfont=dict(family='Times New Roman', size=8, color='white'),
                rangeslider=dict(
                    visible=True,
                    bgcolor = "#0e1117",
                    bordercolor = 'rgba(0, 119, 182, 0.25)',
                    borderwidth = 1,
                    thickness = 0.1
                ),
                rangeselector=dict(
                    visible=True,
                    buttons=[
                        dict(count=1, label='1M', step='month', stepmode='backward'),
                        dict(count=3, label='3M', step='month', stepmode='backward'),
                        dict(count=6, label='6M', step='month', stepmode='backward'),
                        dict(count=12, label='1Y', step='month', stepmode='backward'),
                        dict(step='all', label='All')
                    ],
                    x=0, y=0.9250,
                    xanchor='left', yanchor='bottom',
                    font=dict(family='Times New Roman', size=8, color='white'),
                    bgcolor='#131720',
                    activecolor='#ae81ff',
                    bordercolor='rgba(0, 119, 182, 0.5)',
                    borderwidth=1
                ),
                title=dict(
                    text='',
                    font=dict(family='Times New Roman', size=13, color='#2a3f5f')
                )
            ),
            yaxis=dict(
                type='linear',
                showgrid=True,
                gridcolor= 'rgba(0, 119, 182, 0.2)',
                zeroline=False,
                tickmode='auto',
                showticklabels=False,
                fixedrange=True,
                title=dict(
                    text='',
                    font=dict(family='Times New Roman', size=13, color='white')
                )
            ),
            paper_bgcolor='#0e1117',
            plot_bgcolor='#0e1117',
            hovermode='closest',
            showlegend=False,
            width=700,
            height=250,
            margin=dict(l=0, r=20, t=50, b=10),
            font=dict(family='Times New Roman', size=11, color='white')
        )

        with st.container(key='plotly', height=250):
            st.plotly_chart(fig, use_container_width=True)
    else:
        print("Error occurred returned type: ", type(playerCountData))
        return

#---------------------------------------------------------------------------------------------------------

def generateMainPage(id):

    # ====== Fetch Game Data ================================
    # Use the Steam ID to pull full information from the API
    fetched = functions.steamIDSearch(id)

    if fetched is None:
        generateErrorPage()
        return
    
    else:
        data = fetched.get(id)
    # =======================================================


    # ====== Main Content Rendering ==========================
    # Display information only if the URL parameter is a valid 
    # game from the steam api that successfully returns data
    # ========================================================
    if data.get('success') == True:
        
        # Content dependent on item type {game or dlc/expansion}

        # ====== Type: Game ======----------------------------------------------------------------------------------------

        if data.get('data').get('type') == 'game':
            
            typeGame(data, id)

        
        # ====== Type: DLC ======-----------------------------------------------------------------------------------------


        elif data.get('data').get('type') == 'dlc':
            
            typeDLC(data, id)
    
        # ====== Type: Other ======-----------------------------------------------------------------------------------------
        else:
            generateErrorPage()

#?????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
# ====== Error Page ======
    else:

        generateErrorPage()

#---------------------------------------------------------------------------------------------------------

def typeGame(data, id):

    title = data.get('data').get('name')

    # ====== Main Content Header ============================
    # includes game genre and other tags, short description,
    # title, and tag image provided throught the api request
    # =======================================================
    build_header_(data, title)
    
    #====== Plotly =====================================================
    #===================================================================
    
    # Player count information from Steam Charts
    
    activePlayerPlot(id, title)
    
    #===================================================================
    #===================================================================

    col_reviews, col_screenshots = st.columns(2)

    #===== Reviews for the page ========================================
    #===================================================================
    with col_reviews:
        build_reviews_container_(id)
            
    #===== Screenshot Bar ==============================================
    #===================================================================
    with col_screenshots:

        build_screenshot_bar_(data)

#---------------------------------------------------------------------------------------------------------

def typeDLC(data, id):

    title = data.get('data').get('name')

    # == ID of the parent game / content ===================
    # =======================================================
    if not data.get('data').get('fullgame') is None:
        parent_id = data.get('data').get('fullgame').get('appid')
        parent_title = data.get('data').get('fullgame').get('name')
        parent = True
    else:
        parent = False


    # ====== Main Content Header ============================
    # (Mostly the same as the content header for typeGame() )
    # includes game genre and other tags, short description,
    # title, and tag image provided throught the api request
    # =======================================================
    if parent:
        build_header_(data, title, parent_id, parent_title)
    else:
        build_header_(data, title)
    
    #====== Plotly =====================================================
    #===================================================================

    # Player count information from Steam Charts
    if parent:
            
        activePlayerPlot(parent_id, parent_title)

    else:
        pass
    
    #===================================================================
    #===================================================================

    col_reviews, col_screenshots = st.columns(2)

    #===== Reviews for the page ========================================
    #===================================================================
    with col_reviews:

        build_reviews_container_(id)
            
    #===== Screenshot Bar ==============================================
    #===================================================================
    with col_screenshots:

        build_screenshot_bar_(data)

#---------------------------------------------------------------------------------------------------------

def generateErrorPage():
    

    #===== Error Header =============================================
    #===================================================================
    st.html(f"""
                <div style="display: inline-flex; width: 100%; gap: 45%;">
                    <h1 style= 'font-size: 32px; padding: 0; width: 48%; margin-right: 2%; text-align: center;'> 
                        Content Not Found
                    </h1>   
                    <span class='cat-tag' style="height: fit-content; font-size: 12px;" > ERROR </span>
                </div>
                <div class='header-info'>
                        <p style='text-align: center; font-size: 18px;'> 
                            We couldn’t find a valid Steam store page for this title. This may happen for a few reasons:
                        </p>
                        <ul style='text-align: left; margin-left: 5%;'>
                            <li>The steam content ID is depreciated or does not exist</li>
                            <li>The ID refers to a test app or internal tool, not a public game or dlc content</li>
                            <li>There is not a valid steam store page for the provided ID </li>
                            <li>There was a problem retrieving data from Steam or internal datasets</li>
                        </ul>
                    <!-- <img class='header-image' src=''><br> -->
                </div>
            """)

#---------------------------------------------------------------------------------------------------------

def build_header_(data, title, parent_id = None, parent_title = None):
    
    # ====== Main Content Header ============================
    # includes game genre and other tags, short description,
    # title, and tag image provided throught the api request
    # =======================================================

    # ====== Generating Tags ===============================
    # ====== Genre and Category Tags =======================
    tags = ""
    
    # == Genre ==
    if not data.get('data').get('genres') is None:
        for gen in data.get('data').get('genres'):
            tags += f" <div class='gen-tag'>{gen.get('description')}</div> "
    
    # == Category ==
    if not data.get('data').get('categories') is None:
        for cat in data.get('data').get('categories'):
            tags += f" <div class='cat-tag'>{cat.get('description')}</div> "
    
    # ===== Publisher and Developer Lists ===================
    # =======================================================

    # == Developers ==
    devs = ""
    if not data.get('data').get('developers') is None:
        for i in range(len(data.get('data').get('developers'))):
            devs += f" <span class='pubdev-tag'> {data.get('data').get('developers')[i]} </span> "

    if not len(devs) == 0:
        devs = f"<h4 style='margin: 15px 2.5% 0; text-align: left; font-size: 14px; line-height: 2'> Developer: <span>{devs}</span> </h4>"
    
    # == Publishers ==
    pubs = ""
    if not data.get('data').get('publishers') is None:
        for i in range(len(data.get('data').get('publishers'))):
            pubs += f" <span class='pubdev-tag'> {data.get('data').get('publishers')[i]} </span> "
    
    if not len(pubs) == 0:
        pubs = f"<h4 style='margin: 15px 2.5% 0; text-align: left; font-size: 14px; line-height: 2'> Publisher: <span>{pubs}</span> </h4>"


    # == DLC Specific ==

    fullgameheader = ""
    
    if not parent_id == None and not parent_title == None:
        fullgameheader = f"""<h4 style='margin: 15px 2.5% 0; text-align: left; font-size: 14px; line-height: 2'> Content Pack For:
                            <span class='pubdev-tag'> <a href='?gID={parent_id}' style='text-decoration: none;'> {parent_title} </a> </span>
                    </h4>"""


    #===== Complete Header =============================================
    #===================================================================
    st.html(f"""
                <div style="display: inline-flex; width: 100%; gap: 45%;">
                    <h1 style= 'font-size: 24px; padding: 0; width: 48%; margin-right: 2%; text-align: center;'> 
                        {title}
                    </h1>   
                    <span class='cat-tag' style="height: fit-content; font-size: 10px;" > {data.get('data').get('type').upper()} </span>
                </div>
                <div class='header'>
                    <div class='header-info'>
                        <p style='text-align: center; font-size: 12px;'> {data.get('data').get('short_description')} </p>
                        <hr style='margin: 0 5% 0; border: 0; border-top: 2px solid #0077b6;'>
                        <div class='cat-tag-container'>{tags}</div>
                    </div>
                    <img class='header-image' src='{data.get('data').get('header_image')}'><br>
                </div>
                <hr style='margin: 15px 2.5% 0; border: 0; border-top: 2px solid #0077b6;'>
                {fullgameheader}
                {devs} {pubs} 
            """)

#---------------------------------------------------------------------------------------------------------

def build_screenshot_bar_(data):

    images = data.get('data').get('screenshots')

    if not images == None:

        paths = ""

        for image in enumerate(images):
            paths += f"<img class='screenshot' src= {image[1].get('path_thumbnail')} >"

        st.html(f"<div class='screenshot-box'> <div class='screenshot-container'>{paths}</div> </div>")
    
    else:
        path = "assets/NoScreenshots.png"

        with open(path, "rb") as file:
            image = base64.b64encode(file.read()).decode()

        image = f"<img class='screenshot' src='data:image/png;base64,{image}'>"
        st.html(f"<div class='screenshot-box'> <div class='screenshot-container'> {image} </div> </div>")
    
#---------------------------------------------------------------------------------------------------------

def build_reviews_container_(id):

    #==== Container and reviews
        with st.container(key="reviewBox"):
            
            #==== HTML List of the reivews
            reviewList = ""

            with st.container():
                
                reviews, next_cursor = functions.getReview(id = id, cursor = st.session_state.cursor)

                if next_cursor not in st.session_state.cursorList:
                    st.session_state.cursorList.append(next_cursor)

                if reviews is None:
                    st.warning("There was a problem retrieving reviews. Please try again later or check your network connection.")
                    return

                for r in reviews:
                    if not r['review'] == "":
                        reviewList += f"""
                            <div class='review' title='{r['timestamp_created']}'>
                                <p style='font-style:italic; font-size: 13px; padding-bottom: 3px; margin-bottom: 0 ;'> 
                                    {datetime.fromtimestamp(r['timestamp_created'], tz=timezone.utc).strftime("%I:%M %B %d, %Y")} 
                                </p>
                                {r['review']}
                            </div>"""
                st.html(
                    f"""
                        <div class='review-container'>
                            <p style='text-align:center; height: 5%; margin-bottom: 4%; margin-top: 2%; font-size: 16px; font-weight: bold;'> 
                                Reviews
                            </p>
                            {reviewList}
                        </div>
                    """
                )
            
            #==== Buttons to navigate to the next/previous review batch
            back, forward = st.columns(2)
            with back:
                with st.container(key="reviewButtonColumnPrev"):
                    st.button(label = ":material/arrow_back:", key="prev", on_click=functions.prevCursor)
            with forward:
                with st.container(key="reviewButtonColumnNext"):
                    st.button(label = ":material/arrow_forward:", key="next", on_click=functions.nextCursor)
