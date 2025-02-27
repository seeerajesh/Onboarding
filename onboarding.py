import streamlit as st
import pandas as pd
import io
import os

# Predefined list of disallowed GST/PAN values
disallowed_gst_pan = {"AAAA1234K", "BBBB1234K", "CCCC1234K"}

# File to store uploaded transporter data
data_file = "transporter_data.csv"

# Ensure the data file exists
if not os.path.exists(data_file):
    pd.DataFrame(columns=["Company Name", "GST/PAN", "Email ID", "Contact Name", "Contact Number"]).to_csv(data_file, index=False)

# Set write permissions
try:
    os.chmod(data_file, 0o666)
except Exception as e:
    st.error(f"Error setting file permissions: {e}")

# Load existing data with error handling
def load_existing_data():
    try:
        if os.stat(data_file).st_size == 0:
            return pd.DataFrame(columns=["Company Name", "GST/PAN", "Email ID", "Contact Name", "Contact Number"])
        df = pd.read_csv(data_file, dtype=str, encoding='utf-8', on_bad_lines='skip')
        df["Company Name"] = df["Company Name"].apply(lambda x: x if x.endswith("-zepto") else x + "-zepto")
        return df
    except Exception as e:
        st.error(f"Error loading data file: {e}")
        return pd.DataFrame(columns=["Company Name", "GST/PAN", "Email ID", "Contact Name", "Contact Number"])

existing_data = load_existing_data()

st.title("Transporter Onboarding")

# User input for manual transporter creation
with st.form("manual_entry_form"):
    cols = st.columns(5)
    company_name = cols[0].text_input("Company Name")
    gst_pan = cols[1].text_input("GST/PAN")
    email_id = cols[2].text_input("Email ID")
    contact_name = cols[3].text_input("Contact Name")
    contact_number = cols[4].text_input("Contact Number")
    submit_button = st.form_submit_button("Add Transporter")

if submit_button:
    if gst_pan in disallowed_gst_pan:
        st.error("Failure: Disallowed GST/PAN")
    elif gst_pan in existing_data["GST/PAN"].values:
        st.warning("GST/PAN already exists for another transporter. Do you want to merge with the existing transporter?")
        if st.button("Yes"):
            st.success("Transporter name merged with existing.")
        elif st.button("No"):
            st.error("Please contact Admin.")
    else:
        company_name = company_name if company_name.endswith("-zepto") else company_name + "-zepto"
        new_entry = pd.DataFrame([[company_name, gst_pan, email_id, contact_name, contact_number]],
                                 columns=["Company Name", "GST/PAN", "Email ID", "Contact Name", "Contact Number"])
        new_entry.to_csv(data_file, mode='a', header=False, index=False, encoding='utf-8', sep=',')
        st.success("Transporter added successfully")
        existing_data = load_existing_data()

uploaded_file = st.file_uploader("Upload Excel/CSV file", type=["xlsx", "csv"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file, dtype=str, encoding='utf-8', on_bad_lines='skip')
        else:
            df = pd.read_excel(uploaded_file, dtype=str)
        
        if "GST/PAN" not in df.columns:
            st.error("Uploaded file must contain a 'GST/PAN' column.")
        else:
            failed_entries = []
            new_entries = []
            
            for _, row in df.iterrows():
                gst_pan = str(row["GST/PAN"]).strip()
                
                # Check for mandatory fields
                if row.isnull().any():
                    failed_entries.append(row)
                    continue
                
                # Check for disallowed GST/PAN
                if gst_pan in disallowed_gst_pan:
                    failed_entries.append(row)
                    continue
                
                # Check for duplicate GST/PAN in existing data
                if gst_pan in existing_data["GST/PAN"].values:
                    failed_entries.append(row)
                    continue
                
                # Append valid entry to new entries list
                row["Company Name"] = row["Company Name"] if row["Company Name"].endswith("-zepto") else row["Company Name"] + "-zepto"
                new_entries.append(row)
            
            # Append new valid entries to transporter_data.csv
            if new_entries:
                new_df = pd.DataFrame(new_entries)
                new_df.to_csv(data_file, mode='a', header=False, index=False, encoding='utf-8', sep=',')
                existing_data = load_existing_data()
            
            # Output results
            success_count = len(new_entries)
            failure_count = len(failed_entries)
            
            st.success(f"Processing complete: {success_count} successful, {failure_count} failed")
            
            if failed_entries:
                failed_df = pd.DataFrame(failed_entries)
                failed_buffer = io.BytesIO()
                failed_df.to_csv(failed_buffer, index=False, encoding='utf-8')
                st.download_button("Download Failed Entries", failed_buffer, file_name="failed_entries.csv", mime="text/csv")
    except Exception as e:
        st.error(f"Error processing file: {e}")

# Display existing data
table_height = min(500, 40 * (len(existing_data) + 1))
st.dataframe(existing_data, height=table_height)
