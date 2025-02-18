import streamlit as st
import pandas as pd
import io

# Predefined list of duplicate GST/PAN values
disallowed_gst_pan = {"AAAA1234K", "BBBB1234K"}

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
            df.loc[df["gst/pan"].isin(disallowed_gst_pan) | df["gst/pan"].duplicated(keep=False), "comments"] = "Failure, company already exists"
            
            # Summary statistics
            success_count = (df["comments"] == "Successful").sum()
            failure_count = (df["comments"] != "Successful").sum()
            
            st.success(f"Processing Complete: {success_count} successful, {failure_count} failed.")
            
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
st.title("Customer Onboarding Platform")

# Sidebar Navigation
menu = st.sidebar.radio("Select Onboarding Type", [
    "Transporter Onboarding", 
    "Vehicle Onboarding", 
    "Consignee Onboarding", 
    "Location Onboarding"
])

if menu == "Transporter Onboarding":
    st.header("Bulk Upload CSV/Excel")

    # Upload button in bright blue color
    st.markdown("""
        <style>
            div.stButton > button:first-child { 
                background-color: #007BFF; 
                color: white; 
                font-weight: bold;
            }
        </style>
    """, unsafe_allow_html=True)

    upload_button = st.file_uploader("Upload CSV/Excel", type=["csv", "xlsx"], key="upload")

    if upload_button:
        processed_df, file_extension = process_uploaded_file(upload_button)
        if processed_df is not None:
            st.dataframe(processed_df)
            st.download_button("Download Processed File", data=download_processed_file(processed_df, file_extension), file_name=f"processed_data.{file_extension}")

    # Manual entry section
    st.header("Manual Entry for Transporter Creation")
    company_name = st.text_input("Company Name")
    gst_pan = st.text_input("GST/PAN")
    email_id = st.text_input("Email ID")
    contact_name = st.text_input("Contact Name")
    contact_number = st.text_input("Contact Number")

    if st.button("Submit"):
        if gst_pan in disallowed_gst_pan:
            st.error("Failure: Company already exists")
        else:
            st.success("Transporter created successfully")

elif menu == "Vehicle Onboarding":
    st.header("Vehicle Onboarding")
    st.write("To be implemented...")

elif menu == "Consignee Onboarding":
    st.header("Consignee Onboarding")
    st.write("To be implemented...")

elif menu == "Location Onboarding":
    st.header("Location Onboarding")
    st.write("To be implemented...")
