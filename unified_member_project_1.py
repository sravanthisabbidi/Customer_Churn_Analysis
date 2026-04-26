import streamlit as st
import pandas as pd
import plotly.express as px



st.markdown("""
<style>
[data-testid="stMetric"] {
    background-color: #1F2937;
    padding: 15px;
    border-radius: 10px;
    box-shadow: 0px 2px 6px rgba(0,0,0,0.3);
}

/* KPI cards */
[data-testid="stMetric"] {
    background-color: #1F2937;
    padding: 25px;              /* increased size */
    border-radius: 12px;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.4);
    border-left: 5px solid #FFC300;   /* yellow highlight */
}

/* KPI value (big number) */
[data-testid="stMetricValue"] {
    font-size: 28px;
    font-weight: bold;
    color: #FFFFFF;
}

/* KPI label */
[data-testid="stMetricLabel"] {
    font-size: 16px;
    color: #EAEAEA;
}
}

/* Headers */
h1, h2, h3 {
    color: #FFC300;
}

/* Alerts */
.stAlert {
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

st.set_page_config(layout="wide")


# ------------------ TITLE ------------------
st.markdown("""
<h2 style='text-align: center; color:"#FFC300";'>
📊 Customer Engagement & Product Utilization Analytics for Retention Strategy
</h2>
<p style='text-align: center; font-size:14px; "#FFC300">
💡 Data-driven insights to improve customer retention and reduce churn
</p>
""", unsafe_allow_html=True)
st.markdown("---")
# ------------------ LOAD DATA ------------------
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, "European_Bank.csv")

df = pd.read_csv("European_Bank.csv")

# ------------------ SIDEBAR FILTERS ------------------
st.sidebar.header("🔍 Filters")
filtered_df = df.copy()

## ENGAGEMENT FILTER
engagement_filter = st.sidebar.selectbox(
    "Engagement Status",
    ["All", "Active", "Inactive"]
)

filtered_df = df.copy()

if engagement_filter == "Active":
    filtered_df = filtered_df[filtered_df['IsActiveMember'] == 1]

elif engagement_filter == "Inactive":
    filtered_df = filtered_df[filtered_df['IsActiveMember'] == 0]

# Product slider
product_filter = st.sidebar.slider(
    "Number of Products",
    int(df['NumOfProducts'].min()),
    int(df['NumOfProducts'].max()),
    (1, 3)
)
filtered_df = filtered_df[
    (filtered_df['NumOfProducts'] >= product_filter[0]) &
    (filtered_df['NumOfProducts'] <= product_filter[1])
]

balance_filter = st.sidebar.slider(
    "Balance Range",
    int(df['Balance'].min()),
    int(df['Balance'].max()),
    (0, 200000)
)

filtered_df = filtered_df[
    (filtered_df['Balance'] >= balance_filter[0]) &
    (filtered_df['Balance'] <= balance_filter[1])
]

threshold = st.sidebar.slider(
    "High Value Balance Threshold",
    int(df['Balance'].min()),
    int(df['Balance'].max()),
    100000
)

high_value_at_risk = df[
    (df["Balance"] > threshold) &
    (df["IsActiveMember"] == 0) &
    (df["NumOfProducts"] <= 2)
]

def kpi_card(title, value, icon, color):
    st.markdown(f"""
    <div style="
        background-color:{color};
        padding:15px;
        border-radius:10px;
        text-align:center;
        color:white;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.2);
    ">
        <h4>{icon} {title}</h4>
        <h2>{value}</h2>
    </div>
    """, unsafe_allow_html=True)

GREEN = "#4CAF50"
BLUE = "#2196F3"
ORANGE = "#FF9800"
RED = "#F44336"
PURPLE = "#9C27B0"
# ------------------ KPI ------------------
st.markdown("### 📌 Key Performance Indicators")

## 1. Engagement Retention Ratio

active = filtered_df[filtered_df['IsActiveMember']==1]['Exited'].mean()
inactive = filtered_df[filtered_df['IsActiveMember']==0]['Exited'].mean()

engagement_ratio = inactive / active if active != 0 else 0


## 2. Product Depth Index

product_loyalty = filtered_df.groupby('NumOfProducts')['Exited'].mean()
product_depth_index = 1 - product_loyalty.mean()

## 3. High-Balance Disengagement Rate

high_balance = filtered_df[filtered_df['Balance'] > 100000]

high_balance_disengagement = high_balance[
    high_balance['IsActiveMember'] == 0
].shape[0] / len(high_balance) if len(high_balance) > 0 else 0

## 4. Credit Card Stickiness Score

card_yes = filtered_df[filtered_df['HasCrCard']==1]['Exited'].mean()
card_no = filtered_df[filtered_df['HasCrCard']==0]['Exited'].mean()

credit_card_stickiness = card_no - card_yes

## 5. Relationship Strength Index (RSI)

filtered_df['RSI'] = (
    0.4 * filtered_df['IsActiveMember'] +
    0.3 * (filtered_df['NumOfProducts'] / filtered_df['NumOfProducts'].max()) +
    0.3 * (filtered_df['Balance'] / filtered_df['Balance'].max())
)

rsi_score = filtered_df['RSI'].mean()

## DISPLAY KPI'S

col1, col2, col3, col4, col5 = st.columns([1.2, 1.2, 1.2, 1.2, 1.2])

with col1:
    kpi_card("Engagement Ratio", round(engagement_ratio, 2), "🔄", "#800000")

with col2:
    kpi_card("Product Depth", round(product_depth_index, 2), "📦", "#FFC300")

with col3:
    kpi_card("High Balance Risk", round(high_balance_disengagement, 2), "💰", "#800000")

with col4:
    kpi_card("Card Stickiness", round(credit_card_stickiness, 2), "💳", "#FFC300")

with col5:
    kpi_card("RSI Score", round(rsi_score, 2), "📈", "#800000")

with st.expander("ℹ️ Understand KPIs"):
    st.write("""
    **Engagement Ratio:**  
    If >1 → inactive customers churn more  

    **Product Depth Index:**  
    Higher value → better retention  

    **High Balance Disengagement:**  
    Focus on these customers for retention  

    **Credit Card Stickiness:**  
    Positive → cards improve loyalty  

    **RSI Score:**  
    Combines multiple factors into one metric  
    """)

st.markdown("---")

#---------------CHARTS--------------------------------
st.markdown("### 📊 Insights Dashboards")

# Common layout styling function
def style_fig(fig, title_color="#FFC300"):
    fig.update_layout(
        plot_bgcolor="#161B22",
        paper_bgcolor="#0E1117",
        font=dict(color="#EAEAEA"),
        title_x=0.5,
        title_font=dict(size=18, color=title_color),
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor="#2A2F38")
    )
    return fig


# Row 1
col1, col2 = st.columns(2)

with col1:
    st.markdown("📊 Engagement vs Churn")

    filtered_df['IsActiveMember'] = filtered_df['IsActiveMember'].astype(str)

    fig1 = px.bar(
        filtered_df,
        x='IsActiveMember',
        y='Exited',
        color='IsActiveMember',
        color_discrete_map={
            0: "#800000",  # maroon → inactive
            1: "#FFC300"   # yellow → active
        }
    )

    fig1.update_traces(width=0.4) 

    st.plotly_chart(fig1, use_container_width=True)


with col2:
    st.markdown("📦 Product Utilization")

    filtered_df['ProductCategory'] = filtered_df['NumOfProducts'].apply(
        lambda x: "Low (1-2)" if x <= 2 else "High (3-4)"
    )

    fig2 = px.bar(
        filtered_df,
        x='ProductCategory',
        y='Exited',
        color='ProductCategory',
        color_discrete_map={
            "Low (1-2)": "#800000",   # maroon → risk
            "High (3-4)": "#FFC300"   # yellow → good engagement
        }
    )

    fig2.update_traces(width=0.4)

    fig2.update_layout(
        plot_bgcolor="#161B22",
        paper_bgcolor="#0E1117",
        font=dict(color="#EAEAEA"),
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor="#2A2F38")
    )

    st.plotly_chart(fig2, use_container_width=True)


# Row 2
col3, col4 = st.columns(2)

with col3:
    st.markdown("💰 High-Value Customers")

    fig3 = px.histogram(
        filtered_df,
        x='Balance',
        nbins=20,
        color_discrete_sequence=['#FFC300']
    )

    fig3.update_traces(
        opacity=0.85,
        marker=dict(line=dict(width=1, color="#0E1117"))
    )

    
    st.plotly_chart(fig3, use_container_width=True)


with col4:
    st.markdown("📈 Retention Strength Index (RSI)")

    fig4 = px.histogram(
        filtered_df,
        x='RSI',
        nbins=20,
        color_discrete_sequence=["#800000"]
    )

    fig4.update_traces(
        opacity=0.85,
        marker=dict(line=dict(width=1, color="#0E1117"))
    )

    st.plotly_chart(fig4, use_container_width=True)


st.markdown("### 📌 Key Metrics Overview")

if engagement_ratio > 1:
    st.warning("⚠️ Inactive customers churn more — improve engagement")

if high_balance_disengagement > 0.3:
    st.warning("⚠️ High-value customers are at risk!")

if credit_card_stickiness > 0:
    st.success("✅ Credit cards improve retention")

if rsi_score < 0.5:
    st.warning("⚠️ Weak customer relationships overall")

st.markdown("### 💰 High-Value At-Risk Customers")

st.caption("Customers with high balance but low engagement — critical for retention strategy")

st.dataframe(high_value_at_risk.head(5))

st.markdown("### 💡 Key Insights")

st.success("✅ Active customers show significantly lower churn")
st.warning("⚠️ High-balance inactive customers are at high risk")
st.info("ℹ️ Increasing product usage improves retention")

st.markdown("---")

st.markdown("""
<p style='text-align: center; font-size:12px; color:gray;'>
Created by Sravanthi Reddy | Data Analyst Project 🚀
</p>
""", unsafe_allow_html=True)


