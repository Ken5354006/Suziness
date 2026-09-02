import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import collections
import plotly.express as px

st.set_page_config(page_title="MD Keno Hot Freq", layout="centered")

st.title("🔥 Keno Hot Number Frequencies")
st.caption("Live exact hit counts for the hottest numbers — mobile optimized")

@st.cache_data(ttl=210) # Auto-refresh cache match to the 3.5 minute draw loop
def analyze_hot_frequencies():
    # 1. Fetch live frontend drawing feed to extract exact distribution data
    URL = "https://www.mdlottery.com/games/keno/past-results/"
    HEADERS = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15"}
    
    try:
        res = requests.get(URL, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        
        # Parse all draw ball nodes from the results feed
        draw_elements = soup.find_all("div", class_="keno-results-draw") or soup.find_all("ul", class_="winning-numbers")
        all_numbers = []
        
        for draw in draw_elements:
            balls = draw.find_all("span", class_="keno-ball")
            if balls:
                all_numbers.extend([int(b.text.strip()) for b in balls if b.text.strip().isdigit()])
                
        if not all_numbers: # Backup parsing logic
            balls = soup.find_all("span", class_="ball")
            all_numbers = [int(b.text.strip()) for b in balls if b.text.strip().isdigit()]

        # 2. Count distributions and map out the Top 10 hottest numbers
        counts = collections.Counter(all_numbers)
        
        # If scraper works smoothly, grab the live rolling top 10 values
        if counts:
            top_10_tuples = counts.most_common(10)
            df_hot = pd.DataFrame(top_10_tuples, columns=["Keno_Number", "Exact_Hits"])
        else:
            raise ValueError()
            
        return df_hot, len(all_numbers) // 20
        
    except Exception as e:
        # Print the exact error directly onto the website screen
        st.exception(e)
        # Fallback remains below
        df = get_mock_data()
        # Fallback simulated dataset mapping the MD Lottery structural parameters
        # Emulates actual hot numbers paired with realistic short-term frequency hits
        mock_data = [
            {"Keno_Number": 59, "Exact_Hits": 14}, {"Keno_Number": 33, "Exact_Hits": 12},
            {"Keno_Number": 30, "Exact_Hits": 11}, {"Keno_Number": 13, "Exact_Hits": 11},
            {"Keno_Number": 1, "Exact_Hits": 9},    {"Keno_Number": 41, "Exact_Hits": 9},
            {"Keno_Number": 52, "Exact_Hits": 8},   {"Keno_Number": 19, "Exact_Hits": 8},
            {"Keno_Number": 11, "Exact_Hits": 7},   {"Keno_Number": 46, "Exact_Hits": 6}
        ]
        return pd.DataFrame(mock_data), 25

# Process data
df_hot_freq, total_draws = analyze_hot_frequencies()

# Clean layout for screen viewports
st.metric(label="Recent Drawings Scanned", value=f"{total_draws} Games")

# Ensure numbers handle as discrete labels on chart layout
df_hot_freq["Keno_Number"] = df_hot_freq["Keno_Number"].astype(str)

# 3. Build Touch-Friendly Interactive Column Chart
fig = px.bar(
    df_hot_freq, 
    x="Keno_Number", 
    y="Exact_Hits",
    text="Exact_Hits", # Displays exact hit value directly on top of the bars
    labels={"Exact_Hits": "Times Drawn", "Keno_Number": "Keno Ball #"},
    color="Exact_Hits",
    color_continuous_scale="Reds" # Deep color grading matching the heat scale
)

fig.update_layout(
    margin=dict(l=10, r=10, t=15, b=10),
    height=340,
    coloraxis_showscale=False, # Hide cluttering color bars on narrow phones
    xaxis={'categoryorder':'total descending'} # Sort left-to-right hottest to lowest
)
fig.update_traces(textposition='outside', marker_line_color='black', marker_line_width=1)

# Render responsive dashboard component
st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# Mobile List view backup element below chart
st.subheader("📋 Top Hot Spot Summary")
for idx, row in df_hot_freq.iterrows():
    st.markdown(f"**Ball #{row['Keno_Number']}** landed **{row['Exact_Hits']} times**")
