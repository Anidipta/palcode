# streamlit_app.py
import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Blueprint Light Detector", layout="wide")

st.title("🔦 AI Emergency Light Detector for Blueprints")
st.markdown("Upload a multi-page electrical drawing PDF to detect and summarize emergency lighting fixtures.")

FLASK_API_URL = "[http://127.0.0.1:5000/process](http://127.0.0.1:5000/process)"

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    st.success(f"File '{uploaded_file.name}' uploaded successfully.")
    
    if st.button("Process Blueprint", type="primary"):
        with st.spinner("Analyzing blueprint... This may take a few minutes. Please wait."):
            try:
                files = {'file': (uploaded_file.name, uploaded_file.getvalue(), 'application/pdf')}
                response = requests.post(FLASK_API_URL, files=files, timeout=600)

                if response.status_code == 200:
                    st.balloons()
                    st.subheader("✅ Processing Complete!")
                    
                    result_data = response.json()

                    if "error" in result_data:
                         st.error(f"An error occurred: {result_data.get('details', result_data['error'])}")
                    else:
                        st.write("### Summary of Detected Emergency Lights")
                        
                        df_data = []
                        for symbol, details in result_data.items():
                            df_data.append({
                                "Symbol": symbol,
                                "Count": details.get("count"),
                                "Description": details.get("description")
                            })
                        
                        df = pd.DataFrame(df_data)
                        st.dataframe(df, use_container_width=True)

                        st.write("### Raw JSON Output")
                        st.json(result_data)

                else:
                    st.error(f"Error communicating with the processing API. Status Code: {response.status_code}")
                    st.json(response.json())

            except requests.exceptions.RequestException as e:
                st.error(f"An error occurred while calling the API: {e}")