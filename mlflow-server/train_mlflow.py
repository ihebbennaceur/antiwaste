import pandas as pd
import numpy as np
import os
import mlflow
import time
from sklearn.model_selection import train_test_split, GridSearchCV 
from sklearn.preprocessing import  StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline


if __name__ == "__main__":
    print("training model...")
    
    # Time execution
    start_time = time.time()

    # Call mlflow autolog
    mlflow.sklearn.autolog()

    # Import dataset
    df = pd.read_csv("https://julie-2-next-resources.s3.eu-west-3.amazonaws.com/full-stack-full-time/linear-regression-ft/californian-housing-market-ft/california_housing_market.csv")

    # X, y split 
    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]

    # Train / test split 
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2)

    # Pipeline 
    pipe = Pipeline(steps=[
        ("standard_scaler", StandardScaler()),
        ("Random_Forest",RandomForestRegressor())
    ])

    ### NECESSARY SETUP
    
    # Set tracking URI to your Heroku application
    os.environ["APP_URI"] = "https://antiwaste-mlflow.herokuapp.com/"
    mlflow.set_tracking_uri(os.environ["APP_URI"])

    # set and get experiment's info 
    EXPERIMENT_NAME="experiment_4"
    mlflow.set_experiment(EXPERIMENT_NAME)
    experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)

    with mlflow.start_run(experiment_id = experiment.experiment_id) as run:

        params_grid = {
            "Random_Forest__n_estimators": list(range(9,10)),
            "Random_Forest__criterion": ["squared_error"],
            "Random_Forest__max_depth": list(range(5, 10)) + [None],
            "Random_Forest__min_samples_split": list(range(2, 3))
        }

        model = GridSearchCV(pipe, params_grid, n_jobs=-1, verbose=3, cv=2, scoring="r2")
        model.fit(X_train, y_train)

        mlflow.log_metric("Train Score", model.score(X_train, y_train))
        mlflow.log_metric("Test Score", model.score(X_test, y_test))
        
        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="modeling_housing_market",
            registered_model_name="random_forest"
        )
       
        print("...Training Done!")
        print(f"---Total training time: {time.time()-start_time} seconds")