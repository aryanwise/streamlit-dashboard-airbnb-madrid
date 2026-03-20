import streamlit as st
import pandas as pd
import plotly.express as px

# page configuration
st.set_page_config(page_title="Airbnb Business Dashboard", page_icon="📊", layout="wide")

# ----------------------
# STYLING
# ----------------------
st.markdown("""
<style>
.main {background-color: #f5f7fb;}

h1, h2, h3 {
    color: #1f2937;
    font-weight: 600;
}

.kpi-card {
    background: white;
    padding: 18px;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.06);
    text-align: center;
}

.insight-box {
    background-color: #1f2937;  /* dark card */
    padding: 12px;
    border-radius: 10px;
    border-left: 5px solid #6366f1;
    margin-top: 10px;
    color: #e5e7eb;  /* light text */
}

.section {
    margin-top: 40px;
}
            
.kpi-card {
    background: rgba(255,255,255,0.9);
    padding: 18px;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    text-align: center;
    color: #111827;
}
</style>
""", unsafe_allow_html=True)

px.defaults.template = "plotly_white"

# ----------------------
# TITLE
# ----------------------
st.title("Airbnb Madrid – Business Intelligence Dashboard")

st.markdown("""
### Executive Summary
- Mid-range pricing maximizes occupancy and revenue  
- Revenue is driven more by occupancy than price  
- Some neighbourhoods offer high returns with lower competition  
""")

# ----------------------
# LOAD DATA
# ----------------------
@st.cache_data
def load_data():
    df = pd.read_csv("listings_madrid.csv")

    df = df.dropna(subset=['price']).copy()
    df['reviews_per_month'] = df['reviews_per_month'].fillna(0)

    df = df[(df['price'] <= 1000) & (df['minimum_nights'] <= 30)]

    # ---- BUSINESS LOGIC ----
    df["estimated_bookings"] = df["reviews_per_month"] * 0.6
    df["estimated_nights"] = df["estimated_bookings"] * 3
    df["occupancy_rate"] = (df["estimated_nights"] / 30).clip(0, 1)
    df["est_revenue"] = df["price"] * df["estimated_nights"]

    return df

df = load_data()

# ----------------------
# SIDEBAR
# ----------------------
st.sidebar.header("Filters")

st.sidebar.markdown("""
<span style="color:#9ca3af; font-size:13px;">
Adjust the price range to explore how pricing impacts revenue and demand.
</span>
""", unsafe_allow_html=True)

price_range = st.sidebar.slider(
    "Price Range (€)",   
    int(df.price.min()),
    int(df.price.max()),
    (50, 300)
)

room_type = st.sidebar.multiselect(
    "Room Type",
    df.room_type.unique(),
    default=df.room_type.unique()
)

filtered_df = df[
    (df.price.between(price_range[0], price_range[1])) &
    (df.room_type.isin(room_type))
]

# ----------------------
# KPI CARDS
# ----------------------
def kpi(title, value):
    st.markdown(f"""
    <div class="kpi-card">
        <h4>{title}</h4>
        <h2>{value}</h2>
    </div>
    """, unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    kpi("Listings", len(filtered_df))

with col2:
    kpi("Avg Price (€)", round(filtered_df.price.mean(), 2))

with col3:
    kpi("Avg Revenue (€)", round(filtered_df.est_revenue.mean(), 2))

st.markdown("---")

# ======================
# 1. MARKET OVERVIEW
# ======================
st.markdown('<div class="section">', unsafe_allow_html=True)
st.header("1. Market Overview")
st.caption("Understand supply distribution and competition across the city.")

col1, col2 = st.columns(2)

with col1:
    fig = px.pie(filtered_df, names="room_type", title="Room Type Distribution")
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    top_neigh = filtered_df.neighbourhood.value_counts().head(10)
    fig = px.bar(top_neigh, orientation='h', title="Top Neighbourhoods by Listings")
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig, use_container_width=True)

st.markdown("""
<div class="insight-box">
<b>Insight:</b> Supply is concentrated in a few neighbourhoods, indicating uneven competition and potential entry barriers.
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ======================
# 2. PRICING STRATEGY
# ======================
st.markdown('<div class="section">', unsafe_allow_html=True)
st.header("2. Pricing Strategy")
st.caption("Analyze pricing distribution and variation across listing types.")

col1, col2 = st.columns(2)

with col1:
    fig = px.histogram(filtered_df, x="price", nbins=50, title="Price Distribution")
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.box(filtered_df, x="room_type", y="price", title="Price by Room Type")
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig, use_container_width=True)

st.markdown("""
<div class="insight-box">
<b>Insight:</b> Entire homes command higher prices but exhibit wide variability, suggesting pricing inefficiencies and optimization opportunities.
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ======================
# 3. REVENUE ANALYSIS
# ======================
st.markdown('<div class="section">', unsafe_allow_html=True)
st.header("3. Revenue Analysis")
st.caption("Understand the relationship between price, occupancy, and revenue.")

col1, col2 = st.columns(2)

with col1:
    fig = px.scatter(
        filtered_df,
        x="price",
        y="est_revenue",
        color="room_type",
        hover_data=["neighbourhood", "occupancy_rate"],
        title="Price vs Revenue"
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.scatter(
        filtered_df,
        x="occupancy_rate",
        y="est_revenue",
        color="room_type",
        title="Occupancy vs Revenue"
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("""
<div class="insight-box">
<b>Insight:</b> Revenue is more sensitive to occupancy than price, indicating that aggressive pricing can reduce bookings and overall earnings.
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ======================
# 4. LOCATION INTELLIGENCE
# ======================
st.header("4. Location Intelligence")
st.caption("Identify high-performing neighbourhoods for investment.")

top_rev = filtered_df.groupby("neighbourhood")["est_revenue"] \
    .mean().sort_values(ascending=False).head(10)

fig = px.bar(top_rev, orientation='h', title="Top Areas by Revenue")
st.plotly_chart(fig, use_container_width=True)

st.markdown("""
<div class="insight-box">
<b>Insight:</b> Some neighbourhoods generate higher revenue despite fewer listings, indicating high-demand and underutilized opportunities.
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ======================
# 5. SMART PRICING TOOL
# ======================
st.header("5. Smart Pricing Tool")
st.caption("Simulate pricing decisions and estimate expected revenue.")

col1, col2 = st.columns(2)

with col1:
    selected_neigh = st.selectbox("Neighbourhood", df.neighbourhood.unique())

with col2:
    selected_room = st.selectbox("Room Type", df.room_type.unique())

subset = df[
    (df.neighbourhood == selected_neigh) &
    (df.room_type == selected_room)
]

if len(subset) > 0:
    st.subheader("Revenue Simulation")
    median_price = subset.price.median()
    avg_nights = subset.estimated_nights.mean()

    price_input = st.slider(
        "Test your price (€)",
        20, 500, int(median_price)
    )

    revenue = price_input * avg_nights
    market_revenue = subset.est_revenue.mean()

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Estimated Revenue", f"€{round(revenue,2)}")

    with col2:
        diff = revenue - market_revenue
        st.metric(
            "vs Market Avg",
            f"{round(diff,2)} €",
            delta=f"{round((diff/market_revenue)*100,1)}%"
        )

    # Pricing zone logic
    if price_input < median_price * 0.8:
        performance = "Underpriced"
        color = "orange"
    elif price_input > median_price * 1.3:
        performance = "Overpriced"
        color = "red"
    else:
        performance = "Optimal Range"
        color = "green"

    st.markdown(f"""
    <div style="padding:10px;border-radius:8px;
    background-color: rgba(99,102,241,0.1);margin-top:10px;">
    <b>Pricing Zone:</b> <span style="color:{color}">{performance}</span>
    </div>
    """, unsafe_allow_html=True)

    # Revenue curve
    sim_prices = list(range(20, 500, 10))
    sim_revenue = [p * avg_nights for p in sim_prices]

    import plotly.express as px

    fig = px.line(
        x=sim_prices,
        y=sim_revenue,
        labels={"x": "Price (€)", "y": "Revenue (€)"},
        title="Revenue vs Price"
    )

    fig.add_scatter(
        x=[price_input],
        y=[revenue],
        mode="markers",
        marker=dict(size=10),
        name="Your Price"
    )

    fig.add_vline(
        x=median_price,
        line_dash="dash",
        annotation_text="Market Median"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Dynamic insight
    if performance == "Underpriced":
        st.warning("This price may increase occupancy but reduce potential revenue.")
    elif performance == "Overpriced":
        st.error("This price may reduce bookings and lower overall revenue.")
    else:
        st.success("This price is within the optimal range for balancing demand and revenue.")

st.markdown("---")

# ======================
# 6. KEY INSIGHTS
# ======================
st.header("6. Key Business Insights")

st.caption(
    "💡 Adjust the Price Range and Room Type filters to explore investment insights dynamically."
)

best_area = top_rev.index[0]
best_room = filtered_df.groupby("room_type")["est_revenue"].mean().idxmax()

st.success(f"""
• Best neighbourhood to invest: {best_area}  
• Most profitable room type: {best_room}  
• Mid-range pricing maximizes occupancy and revenue  
• Revenue depends more on demand (occupancy) than price alone  
""")

# ----------------------
# DOWNLOAD
# ----------------------
st.download_button(
    "Download Filtered Data",
    filtered_df.to_csv(index=False),
    "filtered_data.csv"
)

st.markdown("---")
st.caption("Built by Aryan Mishra • B106 Data Visualisation")