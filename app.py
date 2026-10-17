import streamlit as st
import pandas as pd

from src.data_profiler import profile_dataset
from src.data_transformer import apply_operations
from src.create_ui import render_create_section
from src.update_ui import render_update_section


st.set_page_config(
    page_title="AI Data Assistant",
    layout="wide"
)

st.title("AI Data Assistant")

dataset_tab, employee_tab = st.tabs([
    "Dataset Explorer",
    "Employee Management"
])


# TAB 1: DATASET EXPLORER
with dataset_tab:

    st.header("Dataset Explorer")

    uploaded_file = st.file_uploader(
        "Upload CSV or Excel file",
        type=["csv", "xlsx"]
    )

    if uploaded_file is not None:

        try:
            if uploaded_file.name.lower().endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

        except Exception as error:
            st.error(f"Could not read the file: {error}")

        else:
            st.success("File uploaded successfully!")

            st.subheader("Dataset Preview")
            st.dataframe(df.head(20))

            profile = profile_dataset(df)

            st.subheader("Dataset Overview")

            col1, col2, col3 = st.columns(3)

            col1.metric("Rows", profile["row_count"])
            col2.metric("Columns", profile["column_count"])
            col3.metric(
                "Duplicate Rows",
                profile["duplicate_rows"]
            )

            st.subheader("Column Analysis")

            st.dataframe(
                pd.DataFrame(profile["columns"]),
                use_container_width=True
            )

            st.subheader("Data Transformations")

            selected_operations = st.multiselect(
                "Select transformations",
                options=[
                    "normalize_whitespace",
                    "remove_duplicates"
                ]
            )

            if selected_operations:
                transformed_df = apply_operations(
                    df,
                    selected_operations
                )

                st.subheader("Transformed Dataset")
                st.dataframe(transformed_df)

                st.write(
                    "Rows before:", len(df),
                    "Rows after:", len(transformed_df)
                )

                st.download_button(
                    "Download Cleaned CSV",
                    data=transformed_df.to_csv(
                        index=False
                    ).encode("utf-8-sig"),
                    file_name="cleaned_data.csv",
                    mime="text/csv"
                )


# TAB 2: EMPLOYEE MANAGEMENT
with employee_tab:

    render_create_section()

    st.divider()

    render_update_section()