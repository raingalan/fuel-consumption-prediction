import requests.exceptions
import streamlit as st
import os

# page config, description
st.set_page_config(page_title="Fuel Prediction for Deliveries",
                   layout="wide")

st.write("# Fuel Prediction for Deliveries")
st.write('Enter trip details and the fuel price per liter to get an estimate on fuel consumption.')

st.divider()

# layout
col1, col2, _ = st.columns([0.4, 0.4, 0.1], gap='large')

# input form
with col1:

    st.write('### Trip Details')

    with st.container(border=True):

        # delivery areas
        areas_tuple = ("GMA", "North Luzon", "South Luzon", "Visayas", "Mindanao")
        area = st.selectbox("Delivery Area", areas_tuple)
        area = area.lower().replace(" ", "_")

        # cargo weight
        weights_tuple = ("2T", "4T")
        weight = st.selectbox("Weight", weights_tuple)
        weight = weight.lower()

        # cargo types
        cargo_tuple = ("Dry", "Frozen", "Combi")
        cargo_type = st.selectbox("Cargo Type", cargo_tuple)
        cargo_type = cargo_type.lower()

        # total rountrip distance
        distance = st.number_input("Estimated Roundtrip Distance (km)", value=50, placeholder="Enter a distance in kilometers")

        # fuel price to compute cost
        fuel_price = st.number_input("Fuel Price per Liter (Php)", value=60.0)

    # collate inputs into a dict
    trip_data = {
        "grouped_areas": area,
        "cargo_weight": weight,
        "cargo_type": cargo_type,
        "distance_travelled": distance
    }

    # put in a list since API expects list(dict)
    input_trip = [trip_data]

    is_predict = st.button("Predict Fuel Consumption", type='primary', use_container_width=True)


# prediction display area
with col2:
    st.write('### Prediction')

# Define fastapi endpoint
FASTAPI_ENDPOINT = os.getenv("FASTAPI_ENDPOINT")

# have backup if not set
if not FASTAPI_ENDPOINT and 'FASTAPI_ENDPOINT' in st.secrets:
    FASTAPI_ENDPOINT = st.secrets['FASTAPI_ENDPOINT']
if not FASTAPI_ENDPOINT:
    FASTAPI_ENDPOINT = 'http://127.0.0.1:8000/predict'

if is_predict:

    if distance is None:
        with col1:
            st.error("Please enter a valid input in 'Distance'.")

    with col1:
        st.info("Sending request to FastAPI")
    try:
        response = requests.post(FASTAPI_ENDPOINT, json=input_trip)

        if response.status_code == 200:
            predictions = response.json()
            with col1:
                st.success("Prediction Successful!")

            for i, pred_result in enumerate(predictions):
                if isinstance(pred_result, dict) and "predicted_fuel_liters" in pred_result:

                    pred_liters = pred_result['predicted_fuel_liters']
                    pred_cost = pred_liters * fuel_price
                    with col2:

                        st.metric(label="#### Fuel Consumption", value=f"{pred_liters:,.2f} Liters")
                        st.metric(label='#### Fuel Cost', value=f"Php {pred_cost:,.2f}")
                else:
                    st.warning(f"Could not parse prediction.")

        else:
            st.error(f"Error predicting fuel consumption: {response.status_code} - {response.text}")
            st.json(response.json())
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the FastAPI server.")

    except Exception as e:
        st.error(f'An unexpected error occurred: {e}')






