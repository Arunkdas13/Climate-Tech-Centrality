# cent2.py — streamlined version that starts from already-filtered U.S. data

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# Load the pre-filtered U.S. centrality dataset
centrality_df = pd.read_csv("centrality_us_only.csv")

# Confirm dataset size
print("✅ Loaded US-only dataset with rows:", len(centrality_df))

# Drop rows with missing coordinates
centrality_df = centrality_df.dropna(subset=["latitude", "longitude"])

# Fix lat/lon if needed (assumes they were still saved reversed in the CSV)
centrality_df = centrality_df.rename(columns={"latitude": "temp_lat", "longitude": "temp_lon"})
centrality_df["latitude"] = centrality_df["temp_lon"]
centrality_df["longitude"] = centrality_df["temp_lat"]
centrality_df = centrality_df.drop(columns=["temp_lat", "temp_lon"])

# Create Point geometry for spatial operations
geometry = [Point(xy) for xy in zip(centrality_df["longitude"], centrality_df["latitude"])]
centrality_gdf = gpd.GeoDataFrame(centrality_df, geometry=geometry, crs="EPSG:4326")

# Load U.S. counties shapefile
counties_gdf = gpd.read_file("tl_2022_us_county.shp").to_crs("EPSG:4326")

# Spatial join: match orgs to counties
joined_gdf = gpd.sjoin(centrality_gdf, counties_gdf, how="left", predicate="within")

# Check sample result
print("\nJoined Sample:\n", joined_gdf[["Linkedin_name", "latitude", "longitude", "GEOID", "NAME"]].head())

# Aggregate: sum centrality values by county
centrality_cols = [col for col in joined_gdf.columns if col.endswith("_degree_centrality")]
county_centrality = joined_gdf.groupby("GEOID")[centrality_cols].sum().reset_index()

# Add readable county names
county_names = joined_gdf[["GEOID", "NAME"]].drop_duplicates(subset="GEOID")
county_centrality = county_centrality.merge(county_names, on="GEOID", how="left")

# Preview final result
print("\nAggregated County Centrality (sample):\n", county_centrality.head())

# Save to CSV for Streamlit use
county_centrality.to_csv("county_centrality_output.csv", index=False)
print("✅ Saved county-level data to county_centrality_output.csv")