import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime

#~10 results for a quickmatch of user search
@st.cache_data(ttl=3600)
def storeQuickResults(keyword: str) -> list:
    
    search = keyword.replace(" ", "%20")

    url = f"https://store.steampowered.com/api/storesearch/?term={search}&cc=us&l=en"

    try:
        response = requests.get(url, timeout=3)
        data = response.json()
    
        return data.get('items', [])
    
    except requests.exceptions.RequestException as e:
        
        return None

#------------------------------------------------------------------------------

#Gets the list of all steam games from steampowered api
def steamIDListRequest():

    url = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"

    response = requests.get(url)
    data = response.json()
    data = json.dumps(data.get('applist').get('apps'))
    data = pd.read_json(data)
    data = data.rename(columns = {'appid': 'id', 'name':'Title'})

    return data

#------------------------------------------------------------------------------

#Loads the local id list
def steamIDListLoad():

    with open('datasets/appIDList.json', 'r', encoding='utf-8') as file:
        df = pd.read_json(file)
        df = df.rename(columns={'appid': 'id', 'name': 'Title'})
        return df

#------------------------------------------------------------------------------

#Searchs the id to retrieve details
@st.cache_data(ttl=3600)
def steamIDSearch(id: str) -> dict:

    search = id.replace(" ", "%20")

    url = f"https://store.steampowered.com/api/appdetails?appids={id}"

    try:
        response = requests.get(url, timeout=3)
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        return None

#------------------------------------------------------------------------------

#Gets the reviews from steam for an id and cursor
@st.cache_data(ttl=3600)
def getReview(id: str, cursor: str = "*") -> tuple[list, str]:
    
    url = f"https://store.steampowered.com/appreviews/{id}"

    params = {"json":"1", "cursor": cursor,  "filter": "recent", "language": "english",
    "review_type": "all", "purchase_type": "all", "num_per_page": "5" }

    try:
        response = requests.get(url, params=params, timeout=3)

        if response.status_code == 200:
            page = response.json()
            rev = page.get('reviews', [])
            c = page.get('cursor', None)

        return rev, c
    
    except requests.exceptions.RequestException as e:
        return None, None
    
#Helper functions to navigate between review batches on click of the buttons
def nextCursor():
    i = st.session_state.cursorList.index(st.session_state.cursor)

    if len(st.session_state.cursorList) > i + 1:
        st.session_state.cursor = st.session_state.cursorList[i + 1]       

def prevCursor():
    
    i = st.session_state.cursorList.index(st.session_state.cursor)

    if i == 0:
        return
    
    else:
        st.session_state.cursor = st.session_state.cursorList[i - 1]

#------------------------------------------------------------------------------

#Retrieves plot data
@st.cache_data(ttl=3600)
def steamChartsDataFetch(id: str) -> pd.DataFrame:  

    url = f"https://steamcharts.com/app/{id}/chart-data.json"

    try: 
        response = requests.get(url, timeout=3)

        if response.status_code == 200:
            data = response.json()
            data = pd.DataFrame(data)

            #Will provide an error for empty data as this error is handled by caller
            if data.empty:
                return data 

            data = data.rename(columns = {0:'Tstamp', 1:"PlayerCount"})
            return data
        
        else:
            return None
        
    except requests.exceptions.RequestException as e:
        return None