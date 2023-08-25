import sys
sys.path.append("pages")
sys.path.append("app")

from imports_file import option_menu
from imports_file import translator_reverse
import fonctions as f

import streamlit as st
import pandas as pd

# streamlit page setup
st.set_page_config(
    page_title="Welcome to SAVE",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# initialisation des session_state
if 'data' not in st.session_state:
    st.session_state['data'] = []
if 'liste_ingredients' not in st.session_state:
    st.session_state['liste_ingredients'] = {}
if 'liste_finale' not in st.session_state:
    st.session_state['liste_finale'] = pd.DataFrame(columns=["name", "co2", "nutriscore", "classe",])


liste_menu = ["Prediction", "Barcode", 'Recettes', 'Conseils', 'A propos']
selected = liste_menu[0]
selected = option_menu(None, liste_menu,icons=["list-task","list-task","list-task", "list-task", "list-task"], menu_icon="cast", default_index=0, orientation="horizontal")


def main():
    st.markdown("""
    <style>
    #MainMenu {visibility: hidden; }
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)
    
    pred = -1
    
    # sidebar tips anti gaspillage
    st.sidebar.image("tips.jpg")
    
    # fruits & vegetables process
    if selected == liste_menu[0]:
        f.fruits()
    
    # barcode process
    if selected == liste_menu[1]:
        f.barcode()

    # display recipes
    if selected == liste_menu[2]:
        data = pd.read_csv('./Biodata.csv')
        if len(st.session_state.liste_ingredients) != 0 or len(st.session_state.data) !=0:
            data = pd.concat([data['compo'], pd.DataFrame.from_dict(st.session_state.data)],ignore_index=True)
            options = st.multiselect("rajouter des ingredients",data, default= pd.Series(st.session_state.liste_ingredients.keys()) )
            if st.button("valider"):
                st.session_state.liste_finale = [translator_reverse.translate(x) for x in options]
                f.api_call(pred)
    
    if selected == liste_menu[3]:
        st.divider()
        
        col3, col4 = st.columns(2)
        with col3:
            st.subheader("Un peu de data... Emission CO2")
            st.image("tableau_d_emission.jpg", caption='Ces catégories ne sont pas des chiffres officiels. Ils ne peuvent en aucun cas être utilisés comme référence.')

        with col4:
            st.subheader("Vidéo :video_camera:")
            st.text("Si tu souhaites en savoir plus sur le gaspillage alimentaire tu peux regarder les vidéos ci-dessous :")
            with st.expander("⏯️ Prévention anti-gaspillage", expanded=True):
                st.video("https://www.youtube.com/watch?v=rjxwfp8rs34")
            with st.expander("⏯️ Gaspillage et réchauffement climatique"):
                st.video("https://www.youtube.com/watch?v=ishA6kry8nc")
            with st.expander("⏯️ Empreinte carbonne du gaspillage alimentaire"):
                st.video("https://www.youtube.com/watch?v=IoCVrkcaH6Q")
        
        st.divider()

        st.subheader("Calendrier des fruits et légumes de saison")
        col1, col2 = st.columns(2)
        col1.image('1.jpg')
        col2.image('2.jpg')
            
    # page about
    if selected == liste_menu[4]:
        f.about()


if __name__ == '__main__':    
    main()