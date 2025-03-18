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
           
            padding-top:60%;
    
        }}

        /* Style for buttons */
        .stButton>button {{
            
            width: 200px;
            height: 40px;
            font-size: 16px;
            margin: 6px; /* Spacing between buttons */
            background-color: rgb(106 110 118 / 47%);
        }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)

# Call the function with your local image filename
    set_background("EVback.png")

    if st.button("Go to Sign-up", key="button1"):
        navigate("signin")

    elif st.button("Go to log-in", key="button2"):
        navigate("login")
    
    elif st.button("Go to contact", key="button3"):
        navigate("contact")
    
 



