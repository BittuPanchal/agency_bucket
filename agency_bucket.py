import pandas as pd
import streamlit as st
import base64
import os
from google.cloud import storage


def read_file(file):
    if file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        df = pd.read_excel(file)
    elif file.type == "application/vnd.ms-excel":
        df = pd.read_excel(file)
    elif file.type == "text/csv":
        df = pd.read_csv(file)
    else:
        raise ValueError("Unsupported file format. Only XLSX, XLS, and CSV files are supported.")
    return df


def main():
    st.title("Data Upload and Manipulation")

    # Create an empty DataFrame
    df = pd.DataFrame()

    # Upload data
    file = st.file_uploader("Upload File", type=["xlsx", "xls", "csv"])
    if file is not None:
        df = read_file(file)

    # Add the "agency" column
    agency_values = ['Sterling, VA', 'Winchester, VA', 'Fairfield, CT', 'San Diego, CA', 'Martinsburg, WV']
    df['Agency'] = ''

    # Select agency value
    selected_agency = st.selectbox("Select an agency", agency_values)
    if st.button("Update Agency when 1st row is not header"):
        df['Agency'] = selected_agency
        df.at[1, 'Agency'] = "Agency"

    if st.button("Update Agency when 1st row is header"):
        df['Agency'] = selected_agency

    # Display the updated DataFrame
    st.write("Updated Data:")
    st.dataframe(df)

    # Download button
    if not df.empty:
        temp_file = "temp_file" + os.path.splitext(file.name)[-1]
        df.to_excel(temp_file, index=False, encoding='utf-8', engine='xlsxwriter')

        with open(temp_file, 'rb') as f:
            file_content = f.read()

        href_excel = f'data:application/octet-stream;base64,{base64.b64encode(file_content).decode()}'
        st.markdown(f'<a href="{href_excel}" download="{file.name}">Download Updated Data</a>', unsafe_allow_html=True)

        client = storage.Client()
        buckets = [bucket.name for bucket in client.list_buckets()]
        selected_bucket = st.selectbox("Select a bucket", buckets)

        if st.button("Upload"):
            bucket_name = selected_bucket
            blob_name = file.name

            # Upload the file to the selected bucket and blob
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            blob.upload_from_filename(temp_file)

            st.write("File uploaded successfully!")

            # Clean up temporary file
            os.remove(temp_file)

    else:
        st.warning("No data available to upload.")


if __name__ == '__main__':
    main()
