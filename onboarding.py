import streamlit as st
import pandas as pd
import io
import os

# Predefined list of duplicate GST/PAN values
disallowed_gst_pan = {"AAAA1234K", "BBBB1234K", "CCCC1234K"}

# File to store uploaded transporter data
DATA_FILE = "transporter_data.csv"

# Load existing data
if os.path.exists(DATA_FILE):
    existing_data = pd.read_csv(DATA_FILE)
else:
    existing_data = pd.DataFrame(columns=["Company Name", "GST/PAN", "Email ID", "Contact Name", "Contact Number", "Comments"])

def process_uploaded_file(uploaded_file):
    if uploaded_file is not None:
        try:
            file_extension = "csv" if uploaded_file.name.endswith(".csv") else "xlsx"
            df = pd.read_csv(uploaded_file) if file_extension == "csv" else pd.read_excel(uploaded_file)
            
            # Normalize column names (strip spaces, convert to lowercase)
            df.columns = df.columns.str.strip().str.lower()
            required_columns = {"company name", "gst/pan", "email id", "contact name", "contact number"}
            
            if not required_columns.issubset(set(df.columns)):
                st.error(f"Uploaded file is missing required columns. Found columns: {list(df.columns)}")
                return None, file_extension
            
            # Adding comments column
            df["comments"] = "Successful"
            
            # Checking for duplicate GST/PAN within the uploaded file
            for index, row in df.iterrows():
                gst_pan = row["gst/pan"]
                if pd.isna(gst_pan) or any(pd.isna(row[col]) for col in required_columns):
                    df.at[index, "comments"] = "Failure, mandatory field not filled"
                elif gst_pan in disallowed_gst_pan or gst_pan in existing_data["GST/PAN"].values:
                    df.at[index, "comments"] = "Failure, company already exists"
            
            # Summary statistics
            success_count = (df["comments"] == "Successful").sum()
            failure_count = (df["comments"] != "Successful").sum()
            
            st.success(f"Processing Complete: {success_count} successful, {failure_count} failed.")
            
            # Append successful entries to the existing data file
            successful_entries = df[df["comments"] == "Successful"]
            successful_entries.to_csv(DATA_FILE, mode='a', header=not os.path.exists(DATA_FILE), index=False)
            
            return df, file_extension
        except Exception as e:
            st.error(f"Error processing file: {e}")
            return None, ""

def download_processed_file(df, file_extension):
    output = io.BytesIO()
    if file_extension == "csv":
        df.to_csv(output, index=False)
    else:
        df.to_excel(output, index=False, engine='xlsxwriter')
    output.seek(0)
    return output

# Streamlit UI
st.set_page_config(layout="wide")

# Sidebar Navigation
st.sidebar.title("Onboarding Menu")
menu_option = st.sidebar.radio("Select an option:", ["Transporter Onboarding", "Vehicle Onboarding", "Consignee Onboarding", "Location Onboarding"])

# Display Company Logo and Login Details
col1, col2, col3 = st.columns([1, 5, 1])
with col1:
    st.image("Image_1.png", width=100)
with col3:
    st.image("Image_2.png", width=100)

st.title("Customer Onboarding Platform")

if menu_option == "Transporter Onboarding":
    st.header("Bulk Upload CSV/Excel")
    
    st.markdown(
        """
        <style>
            div.stButton > button:first-child { 
                background-color: #007BFF; 
                color: white; 
                font-weight: bold;
            }
        </style>
        """, unsafe_allow_html=True)
    
    upload_button = st.file_uploader("Add Transporter", type=["csv", "xlsx"], key="upload")
    
    if upload_button:
        processed_df, file_extension = process_uploaded_file(upload_button)
        if processed_df is not None:
            st.dataframe(processed_df)
            st.download_button("Download Processed File", data=download_processed_file(processed_df, file_extension), file_name=f"processed_data.{file_extension}")
    
    st.header("Manual Entry for Transporter Creation")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        company_name = st.text_input("Company Name")
    with col2:
        gst_pan = st.text_input("GST/PAN")
    with col3:
        email_id = st.text_input("Email ID")
    with col4:
        contact_name = st.text_input("Contact Name")
    with col5:
        contact_number = st.text_input("Contact Number")
    
    submit_button = st.button("Submit", disabled=not (company_name and gst_pan and email_id and contact_name and contact_number))
    
    if submit_button:
        if gst_pan in disallowed_gst_pan or gst_pan in existing_data["GST/PAN"].values:
            st.error("Failure: Company already exists")
        else:
            new_entry = pd.DataFrame([[company_name, gst_pan, email_id, contact_name, contact_number, "Successful"]],
                                     columns=existing_data.columns)
            new_entry.to_csv(DATA_FILE, mode='a', header=not os.path.exists(DATA_FILE), index=False)
            st.success("Transporter created successfully")

else:
    st.header(f"{menu_option} - Coming Soon!")
