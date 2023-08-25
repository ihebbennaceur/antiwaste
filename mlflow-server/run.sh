docker run -it\
 -p 4000:4000\
 -v "$(pwd):/home/app"\
 -e APP_URI="APP_URI"\
 antiwaste-mlflow-server