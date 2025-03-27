import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Plant List Generator", layout="centered")
st.title("🌱 Plant List Generator")
st.write("Upload your transplant list (with field numbers and transplant counts), and this tool will generate full plant IDs like 25s.0001-001.")

# File uploader
uploaded_file = st.file_uploader("Upload Excel File", type=[".xlsx"])
sheet_name = st.text_input("Enter sheet name (e.g., P1)", value="P1")

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
        if 'transplant' not in df.columns or 'field.nr' not in df.columns:
            st.error("❌ Required columns not found. Please ensure your sheet has 'field.nr' and 'transplant' columns.")
        else:
            st.success("✅ File loaded successfully!")

            plant_ids = []
            transplant_counts = []

            for idx, row in df.iterrows():
                base_id = row['field.nr']
                count = int(row['transplant'])
                for i in range(1, count + 1):
                    plant_id = f"{base_id}-{str(i).zfill(3)}"
                    plant_ids.append(plant_id)
                    transplant_counts.append(count)

            output_df = pd.DataFrame({
                'Plant ID': plant_ids,
                'Transplant Count': transplant_counts
            })

            st.write("### 🔍 Preview (first 10 rows):")
            st.dataframe(output_df.head(10))

            # Download link
            def to_excel(df):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Plant List')
                processed_data = output.getvalue()
                return processed_data

            st.download_button(
                label="📥 Download Full Plant List as Excel",
                data=to_excel(output_df),
                file_name="plant_list_generated.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
