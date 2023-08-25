import os
import re  # general
import datetime
import boto3  # AWS S3
import botocore
import cv2
import numpy as np  # machine learning
import pandas as pd

import openfoodfacts  # api
import requests
import spoonacular as sp

from PIL import Image
from pyzbar.pyzbar import decode  # barcode

import streamlit as st  # application
import streamlit.components.v1 as components
from streamlit_option_menu import option_menu
from streamlit_extras.buy_me_a_coffee import button
from streamlit_extras.customize_running import center_running
from streamlit_extras.badges import badge

from translate import Translator  # translator

from keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.mobilenet import preprocess_input
from ultralytics import YOLO

AWS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"] 
AWS_KEY_SECRET = os.environ["AWS_SECRET_ACCESS_KEY"]
S3_BUCKET = os.environ["S3_BUCKET"]
fruits_and_vegetables = [ "Apple Braeburn", "Apple Crimson Snow", "Apple Golden 1", "Apple Golden 2", "Apple Golden 3", "Apple Granny Smith", "Apple Pink Lady", "Apple Red 1", "Apple Red 2", "Apple Red 3", "Apple Red Delicious", "Apple Red Yellow 1", "Apple Red Yellow 2", "Apricot", "Avocado", "Avocado ripe", "Banana", "Banana Lady Finger", "Banana Red", "Beetroot", "Blueberry", "Cactus fruit", "Cantaloupe 1", "Cantaloupe 2", "Carambula", "Cauliflower", "Cherry 1", "Cherry 2", "Cherry Rainier", "Cherry Wax Black", "Cherry Wax Red", "Cherry Wax Yellow", "Chestnut", "Clementine", "Cocos", "Corn", "Corn Husk", "Cucumber Ripe", "Cucumber Ripe 2", "Dates", "Eggplant", "Fig", "Ginger Root", "Granadilla", "Grape Blue", "Grape Pink", "Grape White", "Grape White 2", "Grape White 3", "Grape White 4", "Grapefruit Pink", "Grapefruit White", "Guava", "Hazelnut", "Huckleberry", "Kaki", "Kiwi", "Kohlrabi", "Kumquats", "Lemon", "Lemon Meyer", "Limes", "Lychee", "Mandarine", "Mango", "Mango Red", "Mangostan", "Maracuja", "Melon Piel de Sapo", "Mulberry", "Nectarine", "Nectarine Flat", "Nut Forest", "Nut Pecan", "Onion Red", "Onion Red Peeled", "Onion White", "Orange", "Papaya", "Passion Fruit", "Peach", "Peach 2", "Peach Flat", "Pear", "Pear 2", "Pear Abate", "Pear Forelle", "Pear Kaiser", "Pear Monster", "Pear Red", "Pear Stone", "Pear Williams", "Pepino", "Pepper Green", "Pepper Orange", "Pepper Red", "Pepper Yellow", "Physalis", "Physalis with Husk", "Pineapple", "Pineapple Mini", "Pitahaya Red", "Plum", "Plum 2", "Plum 3", "Pomegranate", "Pomelo Sweetie", "Potato Red", "Potato Red Washed", "Potato Sweet", "Potato White", "Quince", "Rambutan", "Raspberry", "Redcurrant", "Salak", "Strawberry", "Strawberry Wedge","Tamarillo","Tangelo","Tomato 1","Tomato 2","Tomato 3","Tomato 4","Tomato Cherry Red","Tomato Heart","Tomato Maroon","Tomato Yellow","Tomato not Ripened","Walnut","Watermelon"]

translator = Translator(to_lang="fr", from_lang="en")    # translator
translator_reverse= Translator(to_lang="en", from_lang="fr")


saisons=[
{ "fruits": ["ananas", "avocat", "banane", "citron", "clementine", "datte", "fruit de la passion", "grenade", "kaki", "kiwi", "litchi", "mandarine", "mangue", "orange", "orange sanguine", "pamplemousse", "papaye", "poire", "pomme"], "legumes": ["carotte", "celeri", "celeri branche", "celeri rave", "chou blanc", "chou de bruxelles", "chou frise", "chou rouge", "chou-chinois", "cima di rapa", "citrouille", "cresson", "endive", "mache", "oignon", "poireau", "pomme de terre", "salsifis", "topinambour"]},
{ "fruits": ["ananas", "avocat", "banane", "citron", "clementine", "datte", "fruit de la passion", "grenade", "kiwi", "litchi", "mandarine", "mangue", "orange", "orange sanguine", "pamplemousse", "papaye", "pomme"], "legumes": ["carotte", "celeri", "celeri branche", "celeri rave", "chou blanc", "chou frise", "chou rouge", "chou-chinois", "cima di rapa", "citrouille", "endive", "mache", "oignon", "poireau", "pomme de terre", "salsifis", "topinambour"]},
{ "fruits": ["ananas", "avocat", "banane", "citron", "datte", "fruit de la passion", "kiwi", "mandarine", "mangue", "orange sanguine", "pamplemousse", "papaye", "pomme"], "legumes": ["carotte", "celeri", "chou blanc", "chou frise", "chou rouge", "chou-rave", "cima di rapa", "endive", "oignon", "petit oignon blanc", "poireau", "salsifis"]},
{ "legumes": ["ail", "asperge blanche", "bette", "carotte", "chou blanc", "chou rouge", "chou-rave", "epinard", "laitue romaine", "oignon", "petit oignon blanc", "radis"], "fruits": ["avocat", "banane", "citron", "fruit de la passion", "kiwi", "litchi", "mangue", "papaye"]},
{ "legumes": ["ail", "asperge blanche", "asperge verte", "aubergine", "bette", "betterave rouge", "chou frise", "chou-chinois", "chou-fleur", "chou-rave", "concombre", "epinard", "fenouil", "laitue romaine", "petit oignon blanc", "pomme de terre", "radis", "radis long", "rhubarbe"], "fruits": ["avocat", "banane", "citron", "fraise", "fraise des bois", "fruit de la passion", "kiwi", "mangue", "papaye"]},
{ "legumes": ["ail", "artichaut", "asperge blanche", "asperge verte", "aubergine", "bette", "betterave rouge", "brocoli", "chou blanc", "chou frise", "chou romanesco", "chou rouge", "chou-chinois", "chou-fleur", "chou-rave", "concombre", "courgette", "epinard", "fenouil", "haricot", "laitue romaine", "navet", "petit oignon blanc", "petit pois", "pois mange-tout", "poivron", "pomme de terre", "radis", "radis long", "rhubarbe"], "fruits": ["banane", "cerise", "citron", "fraise", "fraise des bois", "framboise", "fruit de la passion", "groseille", "groseille i maquereau", "litchi", "mangue", "melon", "nectarine", "papaye", "pasteque", "peche", "tomate", "tomate charnue", "tomate peretti"]},
{ "fruits": ["abricot", "airelle", "banane", "cassis", "cerise", "citron", "fraise", "fraise des bois", "framboise", "fruit de la passion", "groseille", "groseille i maquereau", "litchi", "mangue", "melon", "mure", "myrtille", "nectarine", "papaye", "pasteque", "peche", "tomate", "tomate charnue", "tomate peretti"], "legumes": ["ail", "artichaut", "aubergine", "bette", "betterave rouge", "brocoli", "chou blanc", "chou frise", "chou romanesco", "chou rouge", "chou-chinois", "chou-fleur", "chou-rave", "concombre", "courgette", "cresson", "epinard", "fenouil", "haricot", "laitue romaine", "ma\u00efs", "navet", "patisson", "petit oignon blanc", "petit pois", "pois mange-tout", "poivron", "pomme de terre", "potiron", "radis", "radis long"]},
{ "fruits": ["abricot", "airelle", "amande", "banane", "cassis", "cerise", "citron", "datte", "figue fraiche", "fraise", "fraise des bois", "framboise", "fruit de la passion", "groseille i maquereau", "litchi", "mangue", "marron", "melon", "mirabelle", "mure", "myrtille", "nectarine", "noisette", "papaye", "pasteque", "peche", "poire", "prune", "quetsche", "reine-claude", "tomate", "tomate charnue", "tomate peretti"], "legumes": ["ail", "artichaut", "aubergine", "bette", "betterave rouge", "brocoli", "carotte", "catalonia", "chou blanc", "chou de bruxelles", "chou frise", "chou romanesco", "chou rouge", "chou-chinois", "chou-fleur", "chou-rave", "concombre", "courge", "courgette", "cresson", "epinard", "fenouil", "haricot", "laitue romaine", "ma\u00efs", "navet", "oignon", "patisson", "petit oignon blanc", "poivron", "pomme de terre", "potiron", "radis long"]},
{ "fruits": ["amande", "avocat", "banane", "chataigne", "citron", "coing", "datte", "figue fraiche", "framboise", "fruit de la passion", "litchi", "mangue", "marron", "melon", "mirabelle", "mure", "myrtille", "nectarine", "noisette", "noix", "papaye", "pasteque", "peche", "poire", "prune", "quetsche", "raisin", "reine-claude", "tomate", "tomate charnue", "tomate peretti"], "legumes": ["artichaut", "aubergine", "bette", "betterave rouge", "brocoli", "carotte", "catalonia", "celeri branche", "celeri rave", "chou blanc", "chou de bruxelles", "chou frise", "chou romanesco", "chou rouge", "chou-chinois", "chou-fleur", "chou-rave", "citrouille", "concombre", "courge", "courgette", "cresson", "epinard", "fenouil", "haricot", "laitue romaine", "ma\u00efs", "navet", "oignon", "panais", "patisson", "petit oignon blanc", "poireau", "poivron", "pomme de terre", "potiron"]},
{ "fruits": ["avocat", "banane", "chataigne", "citron", "coing", "datte", "figue fraiche", "fruit de la passion", "kaki", "litchi", "mandarine", "mangue", "marron", "noisette", "noix", "papaye", "poire", "pomme", "prune", "quetsche", "raisin"], "legumes": ["bette", "betterave rouge", "brocoli", "carotte", "catalonia", "celeri", "celeri branche", "celeri rave", "chou blanc", "chou de bruxelles", "chou frise", "chou rouge", "chou-chinois", "chou-fleur", "chou-rave", "cima di rapa", "citrouille", "courge", "cresson", "epinard", "fenouil", "laitue romaine", "ma\u00efs", "oignon", "panais", "petit oignon blanc", "poireau", "poivron", "pomme de terre", "potimarron", "potiron", "salsifis", "topinambour"]},
{ "fruits": ["ananas", "avocat", "banane", "chataigne", "citron", "clementine", "datte", "fruit de la passion", "grenade", "kaki", "kiwi", "kumquat", "mandarine", "mangue", "marron", "noix", "orange", "papaye", "poire", "pomme"], "legumes": ["carotte", "catalonia", "celeri", "celeri branche", "celeri rave", "chou blanc", "chou de bruxelles", "chou frise", "chou rouge", "chou-chinois", "chou-rave", "cima di rapa", "citrouille", "courge", "cresson", "endive", "epinard", "fenouil", "mache", "oignon", "panais", "poireau", "pomme de terre", "potimarron", "salsifis", "topinambour"]},
{ "fruits": ["ananas", "avocat", "banane", "chataigne", "citron", "clementine", "datte", "fruit de la passion", "grenade", "kaki", "kiwi", "kumquat", "litchi", "mandarine", "mangue", "marron", "orange", "orange sanguine", "pamplemousse", "papaye", "poire", "pomme"], "legumes": ["carotte", "catalonia", "celeri", "celeri branche", "celeri rave", "chou blanc", "chou de bruxelles", "chou frise", "chou rouge", "chou-chinois", "cima di rapa", "citrouille", "courge", "cresson", "endive", "mache", "oignon", "panais", "poireau", "pomme de terre", "salsifis", "topinambour"]}
]


