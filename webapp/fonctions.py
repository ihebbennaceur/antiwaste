import imports_file as i
import streamlit as st
import numpy as np

api = i.sp.API(i.os.environ["SPOONACULAR_API_KEY"]) # Spoonacular api key -> heroku

def fix_image(upload):
    imagefile = i.Image.open(upload)
    newsize = (400, 500)
    imagefile = imagefile.resize(newsize)
    col7, col8 = st.columns(2)
    col7.write("Original Image :camera:")
    col7.image(imagefile)
    detectedBarcodes = i.decode(imagefile)
    
    # If not detected then print the message
    if not detectedBarcodes:
       st.write("Barcode Not Detected or your barcode is blank/corrupted!")
    else:
        for barcode in detectedBarcodes: 
            if barcode.data!="": 
            # Print the barcode data
                st.write(barcode.data)
                st.write(barcode.type)
    return detectedBarcodes

# save uploaded file to local temporary directory
def save_uploaded_file_to_temp(uploaded_file):
    try:
        with open(uploaded_file.name, "wb") as f:
            f.write(uploaded_file.getvalue())
        return uploaded_file.name
    except Exception as e:
        st.exception("Failed to save file.")
        return None

# send to aws S3
def send_to_s3(my_upload):
    session = openboto3.Session(aws_access_key_id=AWS_KEY_ID,aws_secret_access_key=AWS_KEY_SECRET)
    s3 = session.resource("s3")
    bucket = s3.Bucket(S3_BUCKET)
    local_file_path = save_uploaded_file_to_temp(my_upload)
    bucket.upload_file(local_file_path, "images/"+my_upload.name)
    st.success("Image loaded successfully!")

def clear_text():
    st.session_state["temp"] = st.session_state["input"]
    st.session_state["input"] = ""


def prepare_image(file):
    img = i.image.load_img(file, target_size=(224, 224))
    img_array = i.image.img_to_array(img)
    img_array_expanded_dims = np.expand_dims(img_array, axis=0)
    return i.preprocess_input(img_array_expanded_dims)

def de_saison(ingredient):
    mois = i.datetime.date.today().month
    liste_saison = i.saisons[mois]
    if ingredient in liste_saison['fruits'] or ingredient in liste_saison['legumes']:
        return True
    else:
        return False

def api_call(pred):
    # 2. search recipes by ingredients - spoonacular api
    ingredients = ", ".join(str(x) for x in st.session_state.liste_finale)
    st.write("ingrédients : ",ingredients)
    for element in st.session_state.liste_finale:
        de_saison(element)

    response = api.search_recipes_by_ingredients(ingredients=ingredients, number=4)
    data = response.json()
    
    # 3. parcours des recettes et affichage d'une recette par colonne (col1,...)
    # nombre de colonnes
    nb_col = 4
    col1, col2, col3, col4 = st.columns(nb_col)
    column = [col1, col2, col3, col4]
    
    for j,recipe in enumerate(data):
        ######## rajouter exception quota reached 150 per day
        url = recipe['image']
        # translation of title recipe
        translation = i.translator.translate(recipe['title'])
        column[j].write(translation)

        # check if the image is available (spoonacular api).
        response = i.requests.head(url)
        if response.status_code == 200:
            # des fois spoonacular n'a pas d'images.
            # column[i].write(recipe['image'])
            column[j].image(recipe['image'])
        else:
            column[j].write("💔 The image is not available 😢")

def save_uploadedfile(file_details):
     with open(i.os.path.join("tempDir",file_details['FileName']),"wb") as fi:
         fi.write(file_details.getbuffer())
     return st.success(f"Saved File:{file_details['FileName']} to tempDir")


def fruits():
    # 1. prediction modele
    st.subheader("Step 1: take a picture or upload an image of your fruits and vegetables")
    mode_dev = st.checkbox('mode developpeur')
    h5 = "TransferLearningModel_10epochs_lr0.0001_validation.h5"
    yoloF = "YOLO_best_frederic_25062023.pt"
    yoloI = "YoloV8"
    choix_model = h5
    model=i.load_model(f'model/{h5}')
    
    if mode_dev:        
        modele =[h5, yoloF, yoloI]
        choix_model = st.selectbox("modele deep learning", modele)
        if choix_model == yoloF :
            model = i.YOLO(f'model/{choix_model}')
        elif choix_model == yoloI:
            model = i.load_model(f'model/{choix_model}')

    uploaded_file = st.file_uploader("🍍 Upload an image to predict", type=["png", "jpg", "jpeg"])
    
    col1, col2, col3 = st.columns([1,2,1])
    if uploaded_file is not None:
        local_file_path = save_uploaded_file_to_temp(uploaded_file)
        file_details = {"FileName":uploaded_file.name,"FileType":uploaded_file.type}
        #save_uploadedfile(file_details)

        imagefile2 = i.Image.open(local_file_path)
        newsize = (500, 800)
        imagefile2_display = imagefile2.resize(newsize)
        col1.image(imagefile2_display)
        
        if col2.button("predict"):
            i.center_running()
            # modele yoloF
            if choix_model == yoloF:
                results = model.predict(local_file_path, save=True, imgsz=320, conf=0.3, show=True, save_conf=True, save_crop=False, boxes=True, project="results") 
                #model.predict(source="0", conf=0.3, show=True)
                ingredients = []

                for result in results:
                    boxes = result.boxes  # Boxes object for bbox outputs
                    for box in boxes:  # there could be more than one detection
                        pred = int(box.cls)
                        ingredient = i.translator.translate(i.fruits_and_vegetables[pred].split()[0])
                        st.session_state.liste_ingredients[ingredient] = ingredient
                        st.session_state.data.append(ingredient)
                    for value in st.session_state.liste_ingredients.values():
                        col2.success(value)
                imagepred = i.Image.open(f"results/predict/{uploaded_file.name}")
                path = 'results/'
                import shutil
                shutil.rmtree(path)
                
                imagefile3_display = imagepred.resize(newsize)
                col3.image(imagefile3_display)
            
            # modele h5
            elif choix_model == h5:
                predictions = model.predict(prepare_image(uploaded_file))
                pred = np.argmax(predictions)
                ingredient = i.translator.translate(i.fruits_and_vegetables[pred].split()[0])
                st.session_state.liste_ingredients[ingredient] = ingredient
                st.session_state.data.append(ingredient)
                st.success(f"prediction is available : {ingredient}")

def barcode():
    # 1. sidebar upload image (fruits, vegetables, product with barcode)
    st.subheader("Step 2: take a picture or upload an image of your barcode")
    my_upload = st.file_uploader("🍍 Upload an image (fruits or product with barcode) 🥕", type=["png", "jpg", "jpeg"])

    if st.button("send to S3"):
        send_to_s3(my_upload)
        col5, col6 = st.columns(2)
        st.divider()
        input_text = st.text_input("🍇 Rajouter des ingredients 🍉: ", st.session_state["input"], key="input", 
                                placeholder="citron, concombre, pomme, carotte...", on_change=clear_text)
        #input_text = st.session_state["temp"]
        
    product = []
    if my_upload is not None:
        detectedBarcodes = fix_image(upload=my_upload)
        for barcode in detectedBarcodes: 
            if barcode.data!="": 
                response = i.openfoodfacts.products.get_product(i.re.search(r'\d+', str(barcode.data)).group())
                product.append(i.openfoodfacts.products.get_product(i.re.search(r'\d+', str(barcode.data)).group()))
        ingredient = response["product"]["product_name"]
        st.session_state.liste_ingredients[ingredient] = ingredient
        st.session_state.data.append(ingredient)

def about():
    st.subheader("Code-source")
    col1, col2, col3 = st.columns([4,1,1])
    with col1:
           st.info("👨‍💻 The application is open source and available on GitHub.")
    with col2:
        i.badge(type="github", name="cdouadi/antiwaste")
    counter ="""visiteurs site: <a><img src="https://www.cutercounter.com/hits.php?id=hvuxnofxa&nd=6&style=1" border="0" alt="counter"></a>"""
    col3.markdown(counter, unsafe_allow_html=True)
    
    st.subheader("Roadmap 🛣️")
    st.warning(" 06/2023 - Naissance du projet 👶 et création de l'équipe SAVE 🤝🔥")
    st.success(" 06/2023 - Conception, développement, test et déploiement de l'application 📱")
    st.error(" 06/2023 - Generation d'un nouveau dataset 🚧")
    st.error(" 07/2023 - Développement de l'application mobile 🚧")    
    
    st.subheader("Team 🚀")
    st.info(" Juliette, Iheb, Karina, Frederic et Chakib")
    st.info("🪐 Special thanks to Jedha Team 👨‍🏫 : Charles - Aurélie - Antoine D. - Océane - Antoine C. - Mathieu - Lionel et Antoine K.")

    # buy me a coffee link
    col3, col4 = st.columns([6,1])
    with col4:
        i.button(username="dchakib", floating=False, width=221)


def another():
    with st.container():
        # Store uploaded photos in session_state
        if 'photos' not in st.session_state:
            st.session_state.photos = []

        # File uploader for photos
        uploaded_files = st.file_uploader("Upload an image (fruits or product with barcode) 🥕", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

        # Process uploaded files
        if uploaded_files:
            for file in uploaded_files:
                st.session_state.photos.append(file)

        # Display the uploaded photos
        if st.session_state.photos:
            st.write('Uploaded Photos:')
            for photo in st.session_state.photos:
                st.image(photo)

