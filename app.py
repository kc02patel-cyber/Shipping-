import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
import time

st.set_page_config(page_title="Global Logistics Intelligence", layout="wide")

@st.cache_data
def load_data():
    return pd.read_excel("logistics_dataset.xlsx")

df = load_data()

# ===== HEADER =====
st.title("Global Logistics Intelligence Command Center")
st.caption("Flexport-Style Trade Lane Analytics | Investor-Grade Visualization | Real-Time Simulation Engine")

# ===== SIDEBAR CONTROLS =====
st.sidebar.header("Control Panel")
modes = st.sidebar.multiselect("Transport Mode", df["mode"].unique(), default=df["mode"].unique())
carriers = st.sidebar.multiselect("Carriers", df["carrier"].unique(), default=df["carrier"].unique())
df_f = df[df["mode"].isin(modes) & df["carrier"].isin(carriers)]

# ===== KPI METRICS =====
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Shipments", len(df_f))
col2.metric("Carbon Footprint (kg)", f"{int(df_f['co2_kg'].sum()):,}")
col3.metric("Cargo Value (USD)", f"${df_f['cargo_value_usd'].sum():,.0f}")
col4.metric("Avg Lead Time (Days)", round(df_f['lead_time_days'].mean(),2))
col5.metric("Delivered %", f"{round((df_f['status']=='Delivered').mean()*100,2)}%")

st.markdown("---")

# ===== SANKEY FLOW: ORIGIN → DESTINATION → CARRIER =====
st.subheader("Trade Lane Flow: Origin → Destination → Carrier (Sankey)")
sankey = df_f.groupby(["origin_country","destination_country","carrier"]).size().reset_index(name="count")

nodes = list(pd.unique(sankey[["origin_country","destination_country","carrier"]].values.ravel()))
index = {v:k for k,v in enumerate(nodes)}

source = sankey["origin_country"].map(index)
mid = sankey["destination_country"].map(index)
target = sankey["carrier"].map(index)

fig_sankey = go.Figure(data=[go.Sankey(
    node=dict(label=nodes, pad=20),
    link=dict(
        source=source.tolist() + mid.tolist(),
        target=mid.tolist() + target.tolist(),
        value=sankey["count"].tolist() + sankey["count"].tolist()
))])
st.plotly_chart(fig_sankey, use_container_width=True)

st.markdown("---")

# ===== TRADE LANE CONGESTION HEATMAP =====
st.subheader("Trade Lane Congestion Heatmap (Shipments Density)")
matrix = df_f.pivot_table(index="origin_country", columns="destination_country", values="shipment_id", aggfunc="count").fillna(0)
fig_heat = px.imshow(matrix, color_continuous_scale="RdYlGn_r", text_auto=True)
st.plotly_chart(fig_heat, use_container_width=True)

st.markdown("---")

# ===== CARRIER PERFORMANCE =====
st.subheader("Carrier Performance Dashboard")
perf = df_f.groupby("carrier").agg({
    "lead_time_days":"mean",
    "cargo_value_usd":"sum",
    "co2_kg":"mean",
    "shipment_id":"count"
}).rename(columns={"shipment_id":"shipments"})

fig_perf = px.bar(perf, x=perf.index, y="shipments", title="Shipments by Carrier")
st.plotly_chart(fig_perf, use_container_width=True)

fig_co2 = px.bar(perf, x=perf.index, y="co2_kg", title="Avg CO₂ Emissions by Carrier")
st.plotly_chart(fig_co2, use_container_width=True)

st.markdown("---")

# ===== CARBON INTENSITY =====
st.subheader("Carbon Intensity per Dollar Moved")
df_f["co2_per_dollar"] = df_f["co2_kg"] / df_f["cargo_value_usd"]
fig_co2d = px.box(df_f, x="mode", y="co2_per_dollar", title="CO₂ / USD by Transport Mode")
st.plotly_chart(fig_co2d, use_container_width=True)

st.markdown("---")

# ===== REAL-TIME STREAM SIMULATION =====
st.subheader("Live Trade Pressure Simulation (Real-Time Feed)")
placeholder = st.empty()
for _ in range(1):
    sample = df_f.sample(200)
    fig_stream = px.scatter(
        sample,
        x="distance_km",
        y="cargo_value_usd",
        color="mode",
        size="lead_time_days",
        title="Pressure View: Distance vs Value vs Lead Time"
    )
    placeholder.plotly_chart(fig_stream, use_container_width=True)
    time.sleep(0.1)

st.markdown("---")

# ===== INSIGHT GENERATOR =====
st.subheader("Automated Intelligence Insights")
insights = []

# Insight 1: Congestion
top_lane = matrix.stack().idxmax()
insights.append(f"Highest congestion corridor: {top_lane[0]} → {top_lane[1]}")

# Insight 2: Carbon
high_carbon_mode = df_f.groupby("mode")["co2_kg"].mean().idxmax()
insights.append(f"Highest avg CO₂ mode: {high_carbon_mode}")

# Insight 3: Carrier Value Capture
top_value_carrier = perf["cargo_value_usd"].idxmax()
insights.append(f"Carrier capturing most cargo value: {top_value_carrier}")

# Insight 4: Delay Risk Approximation
delay_rate = round(100*(df_f['status']!='Delivered').mean(),2)
insights.append(f"Estimated delay risk across network: {delay_rate}%")

for i in insights:
    st.write(f"- {i}")

st.markdown("End of Report.")
