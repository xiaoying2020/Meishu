import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Meishu Breeding Tools", layout="centered")

# Sidebar navigation
tool = st.sidebar.radio("Select a tool:", ["🌱 Plant List Generator", "🧬 Marker Suggestion Plan"])

if tool == "🌱 Plant List Generator":
    st.title("🌱 Plant List Generator")

    st.markdown("""
    #### 👋 Welcome to Meishu Breeding Tools!

    This tool helps you quickly generate transplant plant lists for field layout planning.  
    Just upload your Excel file with the following three important columns:

    | sow.nr         | transplant | generation |
    |----------------|------------|------------|
    | 25s.0001       | 10         | F2         |
    | 25s.0002       | 8          | F3         |

    📌 **sow.nr** can be named with any seasonal prefix like `25s.sow.nr`, `25a.sow.nr`, etc.  
    The app will automatically recognize any column name that **contains `sow.nr`**.

    📌 **transplant** must contain the number of plants transplanted for each field number.  

    📌 **generation** will be automatically incremented (e.g., F2 → F3).  
    ➡️ For cross-pollination seeds, fill in **F0**, then it will advance to **F1** in the transplant list.              

    All other columns will be preserved and copied across all generated plant entries.

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
                if 'sow.nr' in col.lower():
                    field_col = col
                if col.strip().lower() == 'transplant':
                    transplant_col = col

            if not transplant_col or not field_col:
                st.error("❌ Required columns not found. Please ensure your sheet includes a 'transplant' column and a column containing 'sow.nr'.")
            else:
                st.success("✅ File loaded successfully!")

                plant_ids = []
                transplant_counts = []
                metadata = []

                for idx, row in df.iterrows():
                    base_id = row[field_col]
                    count = int(row[transplant_col])

                    row_data = row.to_dict()

                    # Handle generation increment
                    gen = str(row_data.get('generation', '')).strip().upper()
                    if gen.startswith('F') and gen[1:].isdigit():
                        row_data['generation'] = f"F{int(gen[1:]) + 1}"
                    elif gen == '':
                        row_data['generation'] = 'F1'

                    for i in range(1, count + 1):
                        plant_id = f"{base_id}-{str(i).zfill(3)}"
                        plant_ids.append(plant_id)
                        transplant_counts.append(count)
                        metadata.append(row_data.copy())

                # Combine data
                output_df = pd.DataFrame(metadata)
                output_df.insert(0, 'Transplant Count', transplant_counts)
                output_df.insert(0, 'Plant ID', plant_ids)

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

elif tool == "🧬 Marker Suggestion Plan":
    st.title("🧬 Marker Suggestion Plan Generator")

    st.markdown("""
    ### 🧪 Marker Suggestion Plan
    Upload your **sow list Excel file**, and this tool will help generate a basic marker testing suggestion plan.

    **Logic**:
    - If marker result for a marker is blank → suggest testing all markers.
    - If marker result available:
      - R or H → suggest test
      - S → skip test

    📌 Example input format:

    | sow.nr     | Ty1 | Ty2 | Ty3 | Tm-2a |
    |------------|-----|-----|-----|--------|
    | 25s.0178   | H   | S   | H   | R      |
    | 25s.0179   | R   | S   | R   | R      |
    | 25s.0180   |     |     |     |        |
    | 25s.0181   | H   | S   | H   | S      |
    | 25s.0182   | R   | S   | R   | R      |

    You can then manually input the number of plants per marker and proceed to generate your sample plan.
    """)

    uploaded_file = st.file_uploader("Upload Excel file", type=[".xlsx"])
    sheet_name = st.text_input("Enter sheet name", value="P1")

    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file, sheet_name=sheet_name)

            # Make a copy for suggestion output
            suggestion_df = df.copy()

            marker_cols = ['Ty1', 'Ty2', 'Ty3', 'Tm-2a']

            for marker in marker_cols:
                if marker not in suggestion_df.columns:
                    suggestion_df[marker] = ''

            def suggest_marker(val):
                val = str(val).strip().upper()
                return 'yes' if val in ['R', 'H'] else 'no'

            for idx, row in suggestion_df.iterrows():
                for marker in marker_cols:
                    value = str(row.get(marker, '')).strip().upper()
                    # If no marker info at all, suggest all
                    if value == '' or pd.isna(value):
                        suggestion_df.at[idx, marker] = 'yes'
                    else:
                        suggestion_df.at[idx, marker] = suggest_marker(value)

            st.write("### 📋 Suggested Marker Plan (Preview):")
            st.dataframe(suggestion_df.head(10))

            def to_excel(df):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Marker Suggestion')
                return output.getvalue()

            st.download_button(
                label="📥 Download Marker Suggestion Plan",
                data=to_excel(suggestion_df),
                file_name="marker_suggestion_plan.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        except Exception as e:
            st.error(f"❌ Error reading file: {e}")
