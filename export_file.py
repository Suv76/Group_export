import streamlit as st
import pandas as pd
import os
import zipfile
from io import BytesIO

# Function to process CSV files
def process_csv_files(input_folder):
    output_folder = "processed_files"
    os.makedirs(output_folder, exist_ok=True)
    
    dataframes = []

    for file in os.listdir(input_folder):
        if file.endswith('.csv'):
            input_file_path = os.path.join(input_folder, file)
            df = pd.read_csv(input_file_path, skiprows=2)

            df = df.drop(df.index[1:2])
            
            header_row = df[df.iloc[:, 0] == 'Member email address'].index[0]

            main_data = df.iloc[:header_row-1]
            member_data_raw = df.iloc[header_row + 0:]

            header_row_index = 1
            header_row = df.iloc[header_row_index]
            header_list = header_row.tolist()

            member_data_raw.columns = header_list

            final_df = pd.concat([main_data.reset_index(drop=True), member_data_raw.reset_index(drop=True)], axis=1)

            columns_to_keep = [
                'Group name',
                'Group email address',
                'Access level',
                'Total members',
                'Member email address',
                'Role',
                'Status'
            ]

            data = final_df[columns_to_keep]
            columns_to_fill = data.columns[:4]
            data.loc[:, columns_to_fill] = data.loc[:, columns_to_fill].ffill(axis=0)

            data.loc[:, 'Total members'] = data['Total members'].astype(float).astype('Int64')

            output_file_path = os.path.join(output_folder, file)
            data.to_csv(output_file_path, index=False)

            dataframes.append(data)
    
    merged_df = pd.concat(dataframes, ignore_index=True)
    excel_buffer = BytesIO()
    merged_df.to_excel(excel_buffer, index=False, engine='xlsxwriter')

    return output_folder, excel_buffer

# Streamlit app
st.title("Export File Processor")

uploaded_folder = st.file_uploader("Upload a ZIP file containing CSVs", type="zip")

if uploaded_folder is not None:
    with zipfile.ZipFile(uploaded_folder, 'r') as zip_ref:
        zip_ref.extractall("input_folder")

    if st.button("Generate Output"):
        output_folder, excel_buffer = process_csv_files("input_folder")
        
        # Create a zip of the processed CSV files
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            for root, _, files in os.walk(output_folder):
                for file in files:
                    zf.write(os.path.join(root, file), arcname=file)
        zip_buffer.seek(0)
        
        st.download_button(
            label="Download Excel",
            data=excel_buffer,
            file_name="Export_file.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        st.download_button(
            label="Download Folder",
            data=zip_buffer,
            file_name="Output_Export_File.zip",
            mime="application/zip"
        )
