import streamlit as st

st.set_page_config(layout="wide")

st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {
            width: 250px !important; # Set the width to your desired value
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# === INTERFACCIA ===
st.title("💸 Financial Overview")
st.markdown("""
Welcome to the **Big Data Analytics** Project Dashboard.  
This system, built using a *requirement-driven approach*, enables interactive analysis of financial transactions on stock securities.

For more details, you can download the project documentation in PDF format.
""")

# === PULSANTE PER SCARICARE IL PDF ===
with open("./project_report.pdf", "rb") as file:
    st.download_button(
        label="📄 Download pdf",
        data=file,
        file_name="project_report.pdf",
        mime="application/pdf"
    )
