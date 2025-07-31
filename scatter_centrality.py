import streamlit as st
import pandas as pd
import plotly.express as px

# Set wide layout and page title
st.set_page_config(layout="wide")
st.title("📈 County GDP vs. Climate-Tech Centrality")

# Load county-level centrality data
centrality_df = pd.read_csv("county_centrality_output.csv")

# Load county-level GDP data
gdp_df = pd.read_csv("county_gdp_2023.csv", skiprows=3)
gdp_df = gdp_df.rename(columns={"GeoFips": "GEOID", "GeoName": "County", "2023": "gdp_2023"})
gdp_df["gdp_2023"] = pd.to_numeric(gdp_df["gdp_2023"], errors="coerce")

# Ensure both GEOID columns are strings and properly zero-padded
centrality_df["GEOID"] = centrality_df["GEOID"].astype(str).str.zfill(5)
gdp_df["GEOID"] = gdp_df["GEOID"].astype(str).str.zfill(5)

# Merge datasets on GEOID
merged = pd.merge(centrality_df, gdp_df[["GEOID", "gdp_2023"]], on="GEOID", how="inner")

# Let user select which centrality type to view
tech_options = [col for col in centrality_df.columns if col.endswith("_degree_centrality")]
selected_tech = st.sidebar.selectbox("Select Climate-Tech Centrality:", tech_options)

# Drop rows with missing values for selected centrality or GDP
plot_df = merged[[selected_tech, "gdp_2023", "NAME"]].dropna()

# Create scatter plot with regression trendline
fig = px.scatter(
    plot_df,
    x=selected_tech,
    y="gdp_2023",
    hover_name="NAME",
    trendline="ols",
    labels={
        selected_tech: selected_tech.replace("_degree_centrality", "") + " Centrality",
        "gdp_2023": "County GDP (2023, USD)"
    },
    title=f"GDP vs. {selected_tech.replace('_degree_centrality', '')} Centrality by County"
)

# Display plot
st.plotly_chart(fig, use_container_width=True)