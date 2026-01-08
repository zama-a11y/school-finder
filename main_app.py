import pandas as pd
import streamlit as st
from urllib.parse import quote

st.set_page_config(page_title="School Navigator", layout="wide")

st.title("🏫 School Navigator")
st.caption("Search a school and open directions in Google Maps (default).")

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    # Basic cleanup / validation
    required = {"school_name", "latitude", "longitude"}
    missing = required - set(df.columns.str.lower())
    if missing:
        st.error(f"CSV is missing columns: {', '.join(missing)}")
        st.stop()

    # Normalize column names
    df.columns = [c.strip().lower() for c in df.columns]
    df["school_name"] = df["school_name"].astype(str).str.strip()

    # Ensure numeric
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df = df.dropna(subset=["latitude", "longitude", "school_name"])

    # Remove duplicates by name (keep first)
    df = df.drop_duplicates(subset=["school_name"], keep="first")
    return df.sort_values("school_name").reset_index(drop=True)

df = load_data("schools.csv")

# --- Predictive text search (starts-with) ---
st.subheader("Find a school")

typed = st.text_input(
    "Type the first letters of the school name",
    placeholder="e.g. Cha…",
)

typed_clean = (typed or "").strip()

if typed_clean:
    suggestions = df[
        df["school_name"].str.lower().str.startswith(typed_clean.lower())
    ]
else:
    suggestions = df

if suggestions.empty:
    st.warning("No schools start with that. Try a different spelling.")
    st.stop()

school = st.selectbox(
    "Suggestions",
    suggestions["school_name"].tolist(),
    index=0
)

row = df[df["school_name"] == school].iloc[0]
lat = float(row["latitude"])
lon = float(row["longitude"])

# Google Maps directions:
# If origin is omitted, Google Maps typically uses "current location" (best for phone use).
google_maps_url = f"https://www.google.com/maps/dir/?api=1&destination={lat},{lon}&travelmode=driving"

# Optional: show a map preview in-app (nice on desktop, still fine on phone)
st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}))

# Big, tappable button for phones
st.link_button("🧭 Navigate (Google Maps)", google_maps_url)

# Optional extra buttons (if you ever want them)
with st.expander("More options"):
    # Open in Google Maps search by name too (helpful if coords are wrong)
    google_search_url = f"https://www.google.com/maps/search/?api=1&query={quote(school)}"
    st.link_button("🔎 Search in Google Maps (by name)", google_search_url)

    # Waze (not default, but available)
    waze_url = f"https://waze.com/ul?ll={lat}%2C{lon}&navigate=yes"
    st.link_button("🚗 Navigate (Waze)", waze_url)





