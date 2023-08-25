FROM continuumio/miniconda3

WORKDIR /home/app

RUN apt-get update
RUN apt-get install nano unzip
RUN apt install curl -y

#RUN curl -fsSL https://get.deta.dev/cli.sh | sh

RUN pip3 install opencv-python-headless
RUN apt-get install zbar-tools -y
RUN apt-get install libzbar-dev -y

RUN pip install pypng
RUN pip install pillow
RUN pip install qrtools


RUN pip install boto3 pandas gunicorn streamlit pillow pyzbar openfoodfacts spoonacular translate requests tensorflow streamlit_extras st_clickable_images streamlit_option_menu

COPY . /home/app
COPY logo.jpg /opt/conda/lib/python3.10/site-packages/st_clickable_images/frontend/build/logo.jpg


CMD streamlit run --server.port $PORT save.py