import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Page Settings
st.set_page_config(page_title="Google Play Games Analysis", layout="wide")

# Dashboard Title
st.title("Google Play Games Analysis 🎮")

st.markdown("""
In this notebook, we will do some analysis by looking at the data of Top Play Store Games.
* What is the percentage of free video games?
* Which video game category has the most overall ratings?
* What category of video games are the most installed?
* What are the best video games according to Google Play?
""")

# Data Update
@st.cache_data  # Data Caching
def load_data():
    url = "https://raw.githubusercontent.com/anthoguille/data_analysis/refs/heads/main/eda_top_games_google_play/android-games.csv"
    data = pd.read_csv(url)
    # Data Cleaning
    data[['installs', 'mult']] = data['installs'].str.split(expand=True)
    pd.set_option('future.no_silent_downcasting', True)
    data['mult'] = data['mult'].replace({'M': 1, 'K': 0.1, 'k': 0.1})
    data['installs'] = data['installs'].astype(float) * data['mult']
    data['price'] = data['price'].apply(lambda x: 'Free' if x == 0 else 'Paid')
    return data

data = load_data()

# Sidebar for filters
st.sidebar.title("Filters")
category_filter = st.sidebar.selectbox("Select a category", ['All'] + list(data['category'].unique()))
price_filter = st.sidebar.selectbox("Select price type", ['All', 'Free', 'Paid'])

# Filters applying
if category_filter != 'All':
    data = data[data['category'] == category_filter]
if price_filter != 'All':
    data = data[data['price'] == price_filter]

# Answers to key questions
st.header("Answers to Key Questions")

# 1. Percentage of free games
# Container for the first question
with st.container():
    st.subheader("1. Percentage of Free Games")
    free_games = data[data['price'] == 'Free'].shape[0]
    paid_games = data[data['price'] == 'Paid'].shape[0]
    total_games = free_games + paid_games
    free_percentage = (free_games / total_games) * 100

    col1, col2 = st.columns([2, 1])
    with col1:
        fig1 = go.Figure(go.Pie(
            labels=['Free', 'Paid'],
            values=[free_games, paid_games],
            hole=0.5,
            marker=dict(colors=['#1f77b4', '#ff7f0e'])
        ))
        fig1.update_layout(title_text="Distribution of Free vs Paid Games", title_x=0.5)
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        st.metric("Percentage of Free Games", f"{free_percentage:.2f}%")

# 2. Category with the most total ratings
# Container for the second question
with st.container():
    st.subheader("2. Category with the Most Total Ratings")
    category_ratings = data.groupby('category')['total ratings'].sum().reset_index()
    category_ratings = category_ratings.sort_values('total ratings', ascending=False)

    fig2 = px.bar(category_ratings, x='category', y='total ratings', color='category',
                  labels={'total ratings': 'Total Ratings', 'category': 'Category'})
    fig2.update_layout(title_text="Total Ratings by Category", title_x=0.5, showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

    top_category = category_ratings.iloc[0]['category']
    top_ratings = category_ratings.iloc[0]['total ratings']
    st.write(f"The category with the most ratings is **{top_category}** with **{top_ratings:,.0f}** ratings.")

# 3. Most Installed Category
# Container for the third question
with st.container():
    st.subheader("3. Most Installed Category")
    category_installs = data.groupby('category')['installs'].sum().reset_index()
    category_installs = category_installs.sort_values('installs', ascending=False)

    fig3 = px.bar(category_installs, x='category', y='installs', color='category',
                  labels={'installs': 'Installs (Millions)', 'category': 'Category'})
    fig3.update_layout(title_text="Installs by Category", title_x=0.5, showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

    top_install_category = category_installs.iloc[0]['category']
    top_installs = category_installs.iloc[0]['installs']
    st.write(f"The most installed category is **{top_install_category}** with **{top_installs:,.0f}M** installs.")

# 4. Best Games According to Google Play
# Container for the fourth question
with st.container():
    st.subheader("4. Best Games According to Google Play")
    st.markdown("""
    The best games are calculated using a weighted score that combines:
    - **Average Rating** (average rating).
    - **Total Ratings** (total ratings).
    - **Installs** (installs).
    """)

    # Calculate the weighted score
    # Ensure that 'total ratings' and 'installs' are numeric and handle NaN values
    data['total ratings'] = pd.to_numeric(data['total ratings'], errors='coerce')
    data['installs'] = pd.to_numeric(data['installs'], errors='coerce')
    data['total ratings'] = data['total ratings'].fillna(0)
    data['installs'] = data['installs'].fillna(0)

    data['score'] = data['average rating'] * np.log(data['total ratings'] + 1) * np.log(data['installs'] + 1)

    # Get the top 10 games
    top_games = data.sort_values(by='score', ascending=False).head(10)
    top_games = top_games[['title', 'category', 'average rating', 'total ratings', 'installs', 'price']]

    fig4 = go.Figure(data=[go.Table(
        header=dict(values=list(top_games.columns),
                    fill_color='lightblue',
                    align='center'),
        cells=dict(values=[top_games['title'], top_games['category'], top_games['average rating'],
                           top_games['total ratings'], top_games['installs'], top_games['price']],
                   align='left'))
    ])
    fig4.update_layout(title_text="Top 10 Games According to Google Play", title_x=0.5)
    st.plotly_chart(fig4, use_container_width=True)

# Explanation of the formula
st.markdown("**Score Formula:**")
st.latex(r"""
\text{Score} = \text{average rating} \times \log(\text{total ratings} + 1) \times \log(\text{installs} + 1)
""")
st.markdown("""
- **average rating**: Average rating of the game.
- **total ratings**: Total number of ratings.
- **installs**: Total number of installs.
""")

# Footer
st.markdown("---")
st.markdown("Dashboard created with ❤️ using Streamlit and Plotly.")