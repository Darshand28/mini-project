
import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="Industrial By-Product Matchmaking",
    page_icon="♻️",
    layout="wide"
)

# CSV file paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


@st.cache_data
def load_data():
    suppliers = pd.read_csv(DATA_DIR / "suppliers.csv")
    buyers = pd.read_csv(DATA_DIR / "buyers.csv")
    return suppliers, buyers


# Find suitable suppliers for buyers
def find_matches(suppliers, buyers):
    matches = []

    for _, buyer in buyers.iterrows():
        for _, supplier in suppliers.iterrows():

            same_material = (
                str(supplier["material"]).strip().lower()
                == str(buyer["needed_material"]).strip().lower()
            )

            enough_quantity = (
                supplier["quantity_tons"] >= buyer["required_tons"]
            )

            sufficient_purity = (
                supplier["purity_pct"] >= buyer["min_purity_pct"]
            )

            if same_material and enough_quantity and sufficient_purity:
                matches.append({
                    "Buyer": buyer["company"],
                    "Supplier": supplier["company"],
                    "Material": supplier["material"],
                    "Available Tons": supplier["quantity_tons"],
                    "Required Tons": buyer["required_tons"],
                    "Purity (%)": supplier["purity_pct"],
                    "Supplier Location": supplier["location"],
                    "Buyer Location": buyer["location"],
                    "Disposal Cost (₹/ton)": (
                        supplier["disposal_cost_per_ton"]
                    )
                })

    return pd.DataFrame(matches)


# Main application
st.title("♻️ Industrial By-Product B2B Matchmaking")
st.write(
    "Find industries that can reuse waste materials "
    "and connect suppliers with potential buyers."
)

try:
    suppliers, buyers = load_data()
except (FileNotFoundError, pd.errors.EmptyDataError) as error:
    st.error(f"Please check your CSV files in the data folder: {error}")
    st.stop()
except Exception as error:
    st.error(f"Unable to load data: {error}")
    st.stop()

# Sidebar
st.sidebar.header("Search Options")

material_list = sorted(suppliers["material"].dropna().unique())
selected_material = st.sidebar.selectbox(
    "Select Material",
    ["All Materials"] + material_list
)

# Filter suppliers
filtered_suppliers = suppliers.copy()

if selected_material != "All Materials":
    filtered_suppliers = filtered_suppliers[
        filtered_suppliers["material"] == selected_material
    ]

# Match filtered suppliers with buyers
matches = find_matches(filtered_suppliers, buyers)

# Dashboard metrics
col1, col2, col3 = st.columns(3)

col1.metric("Total Suppliers", len(suppliers))
col2.metric("Total Buyers", len(buyers))
col3.metric("Suitable Matches", len(matches))

st.divider()

# Matching results
st.subheader("🔗 Recommended Matches")

if matches.empty:
    st.warning("No suitable matches found for this material.")
else:
    st.dataframe(matches, use_container_width=True)

    csv_file = matches.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Match Results CSV",
        data=csv_file,
        file_name="matching_results.csv",
        mime="text/csv"
    )

# Supplier data
st.subheader("🏭 Supplier Information")
st.dataframe(filtered_suppliers, use_container_width=True)

# Buyer data
st.subheader("📦 Buyer Information")
st.dataframe(buyers, use_container_width=True)

st.caption(
    "Industrial By-Product B2B Matchmaking "
    "| Built using Python, Pandas and Streamlit"
)
