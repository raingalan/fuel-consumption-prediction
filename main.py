from fastapi import FastAPI
from pydantic import BaseModel
from contextlib import asynccontextmanager
from http.client import HTTPException

import joblib
import os
import pandas as pd

from data_preprocessor import DataPreprocessor

# Define request body schema
class PredictRequest(BaseModel):
    grouped_areas: str
    cargo_weight: str
    cargo_type: str
    distance_travelled: float

# Define response schema
class PredictResult(BaseModel):
    predicted_fuel_liters: float

# Global variables for loaded models:
loaded_preprocessor: DataPreprocessor = None
loaded_model = None

# Load Model and Preprocessor on App Startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager for application startup and shutdown events.
    Loads models on startup and perform cleanup on shutdown.
    """
    global loaded_preprocessor, loaded_model
    model_assets_dir = 'model_deployment_assets'

    try:
        preprocessor_path = os.path.join(model_assets_dir, 'data_preprocessor.pkl')
        model_path = os.path.join(model_assets_dir, 'fuel_prediction_rf_model.pkl')

        if not os.path.exists(preprocessor_path):
            raise FileNotFoundError(f"Preprocessor file not found at: {preprocessor_path}")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at: {model_path}")

        loaded_preprocessor = joblib.load(preprocessor_path)
        loaded_model = joblib.load(model_path)
        print("Model and Preprocessor loaded successfully during startup.")

    except FileNotFoundError as e:
        print(f"Critical Error: {e}")
        raise RuntimeError(f"Failed to load essential model assets: {e}")
    except Exception as e:
        print(f"Critical Error: Unexpected error occurred during asset loading: {e}")
        raise RuntimeError(f"Failed to initialize application due to asset loading error: {e}")

    yield

# Initialize Fast API
app = FastAPI(
    title='Fuel Consumption Predictor API',
    description='API for predicting fuel consumption of trucks based on trip details.',
    lifespan=lifespan
)

@app.post("/predict", summary='Predict fuel consumption for a single trip')
def predict_fuel_endpoint(request_data: list[PredictRequest]):
    """
    Predicts the fuel consumption in liters for a given trip
    """
    if loaded_preprocessor is None or loaded_model is None:
        raise HTTPException(status_code=503, detail='Model assets not yet loaded. Server is not ready.')

    try:
        input_dict_list = [item.model_dump() for item in request_data] # convert to list of dicts
        input_df = pd.DataFrame(input_dict_list)
        features_preprocessed = loaded_preprocessor.transform(input_df) # preprocess data

        prediction_scaled = loaded_model.predict(features_preprocessed).reshape(-1,1)
        scaler = loaded_preprocessor.get_target_scaler()
        prediction_original_scale = scaler.inverse_transform(prediction_scaled)

        results = [PredictResult(predicted_fuel_liters=round(float(p[0]), 2)) for p in prediction_original_scale]

        return results
    except Exception as e:
        print(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred during prediction: {str(e)}.")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

