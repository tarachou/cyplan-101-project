import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import os
import requests

API_KEY = "f2a281d2148e5d43afc2a662e56bd07dd08d150f"

# Load the SF Analysis Neighborhoods
neighborhoods = gpd.read_file(
    "data/analysis_neighborhoods.geojson"
)

# Look at the data
print(neighborhoods.head())

# How many rows and columns?
print("Shape:", neighborhoods.shape)

# What are the column names?
print("Columns:", neighborhoods.columns)

# Plot the neighborhoods
neighborhoods.plot()

plt.title("San Francisco Analysis Neighborhoods")
plt.show()


url = "https://api.census.gov/data/2024/acs/acs5"

params = {
    "get": "NAME,B19013_001E,B11001_001E",
    "for": "tract:*",
    "in": "state:06 county:075",
    "key": API_KEY
}

response = requests.get(url, params=params)
response.raise_for_status()

data = response.json()
income = pd.DataFrame(data[1:], columns=data[0])

# Convert income and household counts into numbers
income["B19013_001E"] = pd.to_numeric(
    income["B19013_001E"], errors="coerce"
)
income["B11001_001E"] = pd.to_numeric(
    income["B11001_001E"], errors="coerce"
)

# Replace Census missing-value codes with NaN
income.loc[income["B19013_001E"] < 0, "B19013_001E"] = float("nan")

# Create a unique ID for each census tract
income["GEOID"] = income["state"] + income["county"] + income["tract"]

print(income[["NAME", "B19013_001E", "B11001_001E"]].head())
print("Number of census tracts:", len(income))



# Download 2024 census tract boundaries for California
tract_url = (
    "https://www2.census.gov/geo/tiger/"
    "TIGER2024/TRACT/tl_2024_06_tract.zip"
)

os.makedirs("data/raw", exist_ok=True)
tract_file = "data/raw/ca_census_tracts.zip"

response = requests.get(tract_url, timeout=120)
print("Download status:", response.status_code)
response.raise_for_status()

with open(tract_file, "wb") as f:
    f.write(response.content)

# Read California boundaries and keep only San Francisco County
tracts = gpd.read_file(f"zip://{os.path.abspath(tract_file)}")
tracts = tracts[tracts["COUNTYFP"] == "075"].copy()

print("San Francisco census tract shape:", tracts.shape)
print(tracts[["GEOID", "NAME"]].head())

# Attach income estimates to each tract
tracts_income = tracts.merge(
    income[["GEOID", "B19013_001E", "B11001_001E"]],
    on="GEOID",
    how="left"
)

print(
    "Tracts with income data:",
    tracts_income["B19013_001E"].notna().sum()
)
print(
    "Tracts without income data:",
    tracts_income["B19013_001E"].isna().sum()
)



# STEP 1: Put both maps in a coordinate system measured in meters
neighborhoods_projected = neighborhoods.to_crs(epsg=26910)
tracts_projected = tracts_income.to_crs(epsg=26910)

# STEP 2: Find where census tracts overlap neighborhoods
overlaps = gpd.overlay(
    neighborhoods_projected[["nhood", "geometry"]],
    tracts_projected[
        ["GEOID", "B19013_001E", "B11001_001E", "geometry"]
    ],
    how="intersection"
)

# STEP 3: Measure the overlapping area
overlaps["overlap_area"] = overlaps.geometry.area

# STEP 4: Check the results
print("\nNumber of neighborhood-tract overlaps:", len(overlaps))

print(
    overlaps[
        ["nhood", "GEOID", "B19013_001E",
         "B11001_001E", "overlap_area"]
    ].head(10)
)

print("Neighborhoods represented:", overlaps["nhood"].nunique())



# Exclude tracts without valid income estimates
valid_overlaps = overlaps.dropna(
    subset=["B19013_001E", "B11001_001E"]
).copy()

# Calculate each tract's total land area
valid_overlaps["tract_area"] = (
    valid_overlaps["GEOID"]
    .map(
        tracts_projected.set_index("GEOID").geometry.area
    )
)

# Estimate the share of each tract's households in each neighborhood
valid_overlaps["tract_area_share"] = (
    valid_overlaps["overlap_area"]
    / valid_overlaps["tract_area"]
)

valid_overlaps["estimated_households"] = (
    valid_overlaps["B11001_001E"]
    * valid_overlaps["tract_area_share"]
)

# Estimate neighborhood income, weighting by estimated households
valid_overlaps["weighted_income"] = (
    valid_overlaps["B19013_001E"]
    * valid_overlaps["estimated_households"]
)

neighborhood_income = (
    valid_overlaps.groupby("nhood", as_index=False)
    .agg(
        weighted_income_sum=("weighted_income", "sum"),
        estimated_households=("estimated_households", "sum")
    )
)

neighborhood_income["estimated_income"] = (
    neighborhood_income["weighted_income_sum"]
    / neighborhood_income["estimated_households"]
)

neighborhood_income = neighborhood_income.drop(
    columns=["weighted_income_sum"]
)

print(neighborhood_income.head())


# Create the income table
income_table = neighborhood_income.copy()

# Sort neighborhoods from lowest to highest estimated income
income_table = income_table.sort_values(
    "estimated_income"
).reset_index(drop=True)

# Divide neighborhoods into three groups based on relative income
income_table["income_band"] = pd.qcut(
    income_table["estimated_income"],
    q=3,
    labels=["Lower", "Middle", "Higher"]
)

# Print estimated income and assigned income band
print("\nEstimated neighborhood income and relative income bands:")
print(
    income_table[
        ["nhood", "estimated_income", "income_band"]
    ].to_string(index=False)
)

# Count how many neighborhoods are in each income band
print("\nNeighborhoods per income band:")
print(income_table["income_band"].value_counts())