import streamlit as st

def app(navigate):

    import base64

    def set_background(image_file):
        with open(image_file, "rb") as img:
            encoded = base64.b64encode(img.read()).decode()  # Convert image to base64
        css = f"""
        <style>
        .stApp {{
        background: url("data:image/png;base64,{encoded}") no-repeat center center fixed;
        background-size: cover;
        }}
         /* Centering container */
        div[data-testid="stVerticalBlock"] {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 80vh; /* Adjust height as needed */
            padding-top:90%;
            padding-left:40%;
        }}

        /* Style for buttons */
        .stButton>button {{
            width: 200px;
            height: 50px;
            font-size: 16px;
            margin: 10px; /* Spacing between buttons */
            background-color: rgb(106 110 118 / 47%);
        }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)

# Call the function with your local image filename
    set_background("EVback.png")

    if st.button("Go to Sign-up"):
        navigate("signin")

    elif st.button("Go to log-in"):
        navigate("login")
    
    elif st.button("Go to contact"):
        navigate("contact")
    
 



