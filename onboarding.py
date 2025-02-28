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
    pd.DataFrame(columns=["Company Name", "GST/PAN", "Email ID", "Contact Name", "Contact Number", "Comments"]).to_csv(data_file, index=False)

# Set write permissions
try:
    os.chmod(data_file, 0o666)
except Exception as e:
    st.error(f"Error setting file permissions: {e}")

# Load existing data with error handling
def load_existing_data():
    try:
        if os.stat(data_file).st_size == 0:
            return pd.DataFrame(columns=["Company Name", "GST/PAN", "Email ID", "Contact Name", "Contact Number", "Comments"])
        return pd.read_csv(data_file)
    except Exception as e:
        st.error(f"Error loading data file: {e}")
        return pd.DataFrame(columns=["Company Name", "GST/PAN", "Email ID", "Contact Name", "Contact Number", "Comments"])

existing_data = load_existing_data()

# Streamlit UI
st.title("Transporter Onboarding")

uploaded_file = st.file_uploader("Upload Excel/CSV file", type=["xlsx", "csv"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        if "GST/PAN" not in df.columns:
            st.error("Uploaded file must contain a 'GST/PAN' column.")
        else:
            df["Comments"] = "Successful"
            failed_entries = []
            new_entries = []
            
            for _, row in df.iterrows():
                gst_pan = row["GST/PAN"].strip()
                
                # Check for mandatory fields
                if row.isnull().any():
                    row["Comments"] = "Failure: Mandatory field missing"
                    failed_entries.append(row)
                    continue
                
                # Check for disallowed GST/PAN
                if gst_pan in disallowed_gst_pan:
                    row["Comments"] = "Failure: Disallowed GST/PAN"
                    failed_entries.append(row)
                    continue
                
                # Check for duplicate GST/PAN in existing data
                if gst_pan in existing_data["GST/PAN"].values:
                    row["Comments"] = "Failure: GST/PAN already exists"
                    failed_entries.append(row)
                    continue
                
                # Append valid entry to new entries list
                new_entries.append(row)
            
            # Append new valid entries to transporter_data.csv
            if new_entries:
                new_df = pd.DataFrame(new_entries)
                new_df.to_csv(data_file, mode='a', header=False, index=False)
                
            # Output results
            success_count = len(new_entries)
            failure_count = len(failed_entries)
            
            st.success(f"Processing complete: {success_count} successful, {failure_count} failed")
            
            if failed_entries:
                failed_df = pd.DataFrame(failed_entries)
                failed_buffer = io.BytesIO()
                failed_df.to_csv(failed_buffer, index=False)
                st.download_button("Download Failed Entries", failed_buffer, file_name="failed_entries.csv", mime="text/csv")
    except Exception as e:
        st.error(f"Error processing file: {e}")
