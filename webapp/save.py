import base64
from st_clickable_images import clickable_images
import streamlit as st
from streamlit_extras.switch_page_button import switch_page

def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
        background-size: cover
    }}
    </style>
    """,unsafe_allow_html=True)

def main():
    # cacher le menu principal de l'application streamlit 
    st.markdown("""
        <style>
        #MainMenu {visibility: hidden; }
        footer {visibility: hidden;}
        </style>
        """, unsafe_allow_html=True)
    #   clicked = clickable_images(
    #    [("logo.jpg")],
    #    div_style={"display": "flex", "justify-content": "center", "flex-wrap": "wrap"}
    #)
    #st.markdown( switch_page("streamlit_app_2")  if clicked > -1 else "")
    add_bg_from_local('logo.jpg')
    col1, col2 = st.columns([8,1])
    with col2:
        with st.container():
            for x in range(45):
                st.write("")
            
    #col2.image("tips-copie.jpg")
    result = col2.button("cliquez-ici pour découvrir SAVE 🌍")
    if (result==True):
        st.markdown(switch_page("application"))


if __name__ == '__main__':
    # streamlit page setup
    st.set_page_config(
        page_title="Welcome to SAVE",
        page_icon="🌍",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    main()