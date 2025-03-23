import streamlit as st
import pandas as pd
from lib.cleaning import CleanData

st.title("🛠️ Data Cleaning App")

# File uploader & session initialization
path = st.file_uploader("Upload your CSV file", type=["csv"])

if path:
    if "cleaner" not in st.session_state:
        st.session_state.cleaner = CleanData(path)  # Store cleaner in session state

    cleaner = st.session_state.cleaner  # Retrieve cleaner instance
    st.write("### Raw Data", cleaner.df)

    # Option 1: Remove duplicates
    if st.button("Remove Duplicates"):
        cleaner.drop_duplicates()
        st.write("### Data After Removing Duplicates", cleaner.df)

    # Option 2: Create new column
    new_col_name = st.text_input("Enter the new column name:")
    formula = st.text_input("Enter the formula (e.g., [col1] * [col2]):")

    # Apply button for creating the new column
    if st.button("Apply New Column"):
        if new_col_name and formula:
            cleaner.add_col(new_col_name, formula)
            st.write(f"### Data After Adding New Column '{new_col_name}'", cleaner.df)
        else:
            st.warning("Please provide both a column name and a valid formula.")

    # Store filters in session state
    if "filters" not in st.session_state:
        st.session_state.filters = {}

    col = st.selectbox("Select column to filter", cleaner.df.columns)
    condition = st.text_input("Enter condition (e.g., '> 5', '== \"active\"')")

    if st.button("Add Filter"):
        if col and condition:
            st.session_state.filters[col] = condition
            st.success(f"Added filter: `{col} {condition}`")

    if st.button("Apply Filters"):
        cleaner.filter_rows(st.session_state.filters)
        st.write("### Data After Filtering", cleaner.df)

    # Download cleaned file
    st.download_button(
        label="Download Cleaned Data",
        data=cleaner.df.to_csv(index=False).encode("utf-8"),
        file_name="cleaned_data.csv",
        mime="text/csv",
    )