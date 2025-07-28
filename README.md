# Fuel Consumption Prediction

This project creates a web-based dashboard for predicting fuel consumption and cost for delivery trips. This uses a random forest model exposed via a FastAPI backend and presented via a Streamlit frontend.

---

## Features

* **Single Trip Prediction:** Estimate fuel consumption and cost for individual trips based on delivery area, cargo weight, cargo type, and distance.
* **Multiple Trip Prediction:** Input details for several trips in a table to get batch predictions for fuel consumption and cost and allow downloading via csv.
* **FastAPI Backend:** A REST API serving machine learning predictions, trained on historical fuel consumption data.
* **Streamlit Frontend:** An interactive and user-friendly web interface for inputting trip details and obtaining predictions.

---

## Technologies Used

* **Python 3.10+**
* **FastAPI:** For building the prediction API.
* **Streamlit:** For creating the interactive web dashboard.
* **scikit-learn:** For machine learning model development (part of your `model/fuel_prediction_pipeline.joblib`).
* **pandas:** For data manipulation.
* **joblib:** For saving and loading the machine learning pipeline.
* **Git & GitHub:** For version control.

---