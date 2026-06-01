import pandas as pd
import numpy as np
from pathlib import Path

# -----------------------------
# File paths
# -----------------------------
INPUT_FILE = Path("MetObjects.xlsx")
OUTPUT_FULL = Path("met_clean_full.csv")
OUTPUT_SAMPLE = Path("met_clean_30000.csv")

# -----------------------------
# Load dataset
# -----------------------------
print("Loading Excel file... This may take some time.")

df = pd.read_excel(INPUT_FILE, engine="openpyxl")

print("Original shape:", df.shape)
print("Original columns:")
print(df.columns.tolist())

# -----------------------------
# Select useful columns
# -----------------------------
columns_to_keep = [
    "Object ID",
    "Object Number",
    "Is Highlight",
    "Is Timeline Work",
    "Is Public Domain",
    "Object Name",
    "Title",
    "Culture",
    "Period",
    "Artist Display Name",
    "Artist Nationality",
    "Artist Gender",
    "Object Date",
    "Object Begin Date",
    "Object End Date",
    "Medium",
    "Dimensions",
    "Classification",
    "Department",
    "Credit Line",
    "Geography Type",
    "City",
    "State",
    "County",
    "Country",
    "Region",
    "Subregion",
    "Link Resource",
    "Object Wikidata URL",
    "Tags",
]

# Keep only columns that actually exist in the file
existing_columns = [col for col in columns_to_keep if col in df.columns]
df = df[existing_columns].copy()

print("After selecting columns:", df.shape)

# -----------------------------
# Rename columns for easier coding
# -----------------------------
rename_map = {
    "Object ID": "object_id",
    "Object Number": "object_number",
    "Is Highlight": "is_highlight",
    "Is Timeline Work": "is_timeline_work",
    "Is Public Domain": "is_public_domain",
    "Object Name": "object_name",
    "Title": "title",
    "Culture": "culture",
    "Period": "period",
    "Artist Display Name": "artist_name",
    "Artist Nationality": "artist_nationality",
    "Artist Gender": "artist_gender",
    "Object Date": "object_date",
    "Object Begin Date": "object_begin_date",
    "Object End Date": "object_end_date",
    "Medium": "medium",
    "Dimensions": "dimensions",
    "Classification": "classification",
    "Department": "department",
    "Credit Line": "credit_line",
    "Geography Type": "geography_type",
    "City": "city",
    "State": "state",
    "County": "county",
    "Country": "country",
    "Region": "region",
    "Subregion": "subregion",
    "Link Resource": "link_resource",
    "Object Wikidata URL": "object_wikidata_url",
    "Tags": "tags",
}

df = df.rename(columns=rename_map)

# -----------------------------
# Basic cleaning
# -----------------------------
# Remove completely empty titles/departments/classifications
important_columns = ["object_id", "title", "department", "classification", "object_begin_date", "object_end_date"]

for col in important_columns:
    if col in df.columns:
        df[col] = df[col].replace("", np.nan)

df = df.dropna(subset=[col for col in important_columns if col in df.columns])

print("After removing weak records:", df.shape)

# -----------------------------
# Keep public domain objects
# -----------------------------
if "is_public_domain" in df.columns:
    df = df[df["is_public_domain"] == True].copy()

print("After keeping public domain objects:", df.shape)

# -----------------------------
# Clean date values
# -----------------------------
df["object_begin_date"] = pd.to_numeric(df["object_begin_date"], errors="coerce")
df["object_end_date"] = pd.to_numeric(df["object_end_date"], errors="coerce")

df = df.dropna(subset=["object_begin_date", "object_end_date"])

df["object_mid_year"] = ((df["object_begin_date"] + df["object_end_date"]) / 2).round().astype(int)

# Remove extreme or unreliable dates
df = df[(df["object_mid_year"] >= -5000) & (df["object_mid_year"] <= 2026)]

print("After cleaning dates:", df.shape)

# -----------------------------
# Create time period groups
# -----------------------------
def create_time_group(year):
    if year < 0:
        return "Before 0"
    elif year <= 999:
        return "0–999"
    elif year <= 1499:
        return "1000–1499"
    elif year <= 1699:
        return "1500–1699"
    elif year <= 1799:
        return "1700–1799"
    elif year <= 1899:
        return "1800–1899"
    elif year <= 1949:
        return "1900–1949"
    else:
        return "1950–present"

df["time_period_group"] = df["object_mid_year"].apply(create_time_group)

# -----------------------------
# Create simplified medium groups
# -----------------------------
def create_medium_group(medium):
    if pd.isna(medium):
        return "Unknown"

    m = str(medium).lower()

    if any(word in m for word in ["oil", "tempera", "acrylic", "paint"]):
        return "Painting"
    elif any(word in m for word in ["paper", "ink", "etching", "lithograph", "engraving", "print", "drawing", "watercolor"]):
        return "Paper / Print / Drawing"
    elif any(word in m for word in ["photograph", "albumen", "gelatin silver", "daguerreotype"]):
        return "Photography"
    elif any(word in m for word in ["silk", "cotton", "wool", "linen", "textile", "velvet", "tapestry"]):
        return "Textile"
    elif any(word in m for word in ["ceramic", "porcelain", "stoneware", "earthenware", "clay"]):
        return "Ceramic"
    elif any(word in m for word in ["bronze", "gold", "silver", "copper", "iron", "steel", "metal"]):
        return "Metal"
    elif any(word in m for word in ["wood", "oak", "walnut", "mahogany"]):
        return "Wood"
    elif any(word in m for word in ["glass"]):
        return "Glass"
    elif any(word in m for word in ["marble", "stone", "limestone", "granite"]):
        return "Stone"
    else:
        return "Mixed / Other"

df["medium_group"] = df["medium"].apply(create_medium_group)

# -----------------------------
# Create geography availability variable
# -----------------------------
geo_cols = ["country", "region", "culture"]
for col in geo_cols:
    if col in df.columns:
        df[col] = df[col].replace("", np.nan)

df["has_geography_info"] = df[geo_cols].notna().any(axis=1)

# -----------------------------
# Create visibility group
# -----------------------------
def visibility_group(row):
    highlight = row.get("is_highlight", False)
    timeline = row.get("is_timeline_work", False)

    if highlight and timeline:
        return "Highlight and Timeline Work"
    elif highlight:
        return "Highlight"
    elif timeline:
        return "Timeline Work"
    else:
        return "Regular Collection Object"

df["visibility_group"] = df.apply(visibility_group, axis=1)

# -----------------------------
# Remove duplicated object IDs
# -----------------------------
df = df.drop_duplicates(subset=["object_id"])

print("After removing duplicates:", df.shape)

# -----------------------------
# Save full cleaned dataset
# -----------------------------
df.to_csv(OUTPUT_FULL, index=False, encoding="utf-8-sig")
print(f"Saved full cleaned dataset: {OUTPUT_FULL}")
print("Full cleaned shape:", df.shape)

# -----------------------------
# Create 30,000-row working sample
# -----------------------------
# Stratified sample by department if possible
sample_size = 30000

if len(df) > sample_size:
    df_sample = (
        df.groupby("department", group_keys=False)
        .apply(lambda x: x.sample(
            min(len(x), max(1, int(sample_size * len(x) / len(df)))),
            random_state=42
        ))
    )

    # If stratified sampling gives slightly less/more than 30,000, adjust
    if len(df_sample) > sample_size:
        df_sample = df_sample.sample(sample_size, random_state=42)
    elif len(df_sample) < sample_size:
        remaining = df.drop(df_sample.index)
        needed = sample_size - len(df_sample)
        df_extra = remaining.sample(min(needed, len(remaining)), random_state=42)
        df_sample = pd.concat([df_sample, df_extra])

else:
    df_sample = df.copy()

df_sample.to_csv(OUTPUT_SAMPLE, index=False, encoding="utf-8-sig")
print(f"Saved 30,000-row working dataset: {OUTPUT_SAMPLE}")
print("Sample shape:", df_sample.shape)

# -----------------------------
# Print summary
# -----------------------------
print("\nSummary:")
print("Departments:", df["department"].nunique())
print("Classifications:", df["classification"].nunique())
print("Medium groups:", df["medium_group"].value_counts())
print("Time groups:", df["time_period_group"].value_counts())
print("Visibility groups:", df["visibility_group"].value_counts())