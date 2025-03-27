import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Plant List Generator", layout="centered")
st.title("🌱 Plant List Generator")
st.markdown("""
#### 👋 Welcome to Meishu Plant Breeding Tools!

This tool helps you quickly generate transplant plant lists for field layout planning.  
Just upload your Excel file with the following two columns:

| field.nr       | transplant |
|----------------|------------|
| 25s.0001       | 10         |
| 25s.0002       | 8          |

📌 **field.nr** can be named with any seasonal prefix like `25s.field.nr`, `25a.field.nr`, etc.  
The app will automatically recognize any column name that **contains `field.nr`**.

📌 **transplant** must contain the number of plants transplanted for each field number.  

Need help? Contact the Meishu team.
""")

# File uploader
uploaded_file = st.file_uploader("Upload Excel File", type=[".xlsx"])
sheet_name = st.text_input("Enter sheet name (e.g., Sheet1)", value="Sheet1")

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, sheet_name=sheet_name)

        # Detect columns dynamically
        transplant_col = None
        field_col = None

        for col in df.columns:
            if 'field.nr' in col.lower():
                field_col = col
            if col.strip().lower() == 'transplant':
                transplant_col = col

        if not transplant_col or not field_col:
            st.error("❌ Required columns not found. Please ensure your sheet includes a 'transplant' column and a column containing 'field.nr'.")
        else:
            st.success("✅ File loaded successfully!")

            plant_ids = []
            transplant_counts = []

            for idx, row in df.iterrows():
                base_id = row[field_col]
                count = int(row[transplant_col])
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

