import streamlit as st
import requests
import pandas as pd

from Single_Trip_Prediction import FASTAPI_ENDPOINT

# set page config, description

st.set_page_config(page_title="Batch Fuel Prediction",
                   layout='wide')

st.write("# Batch Fuel Predictions")
st.write('Allows entry of multiple trip details to get estimated fuel consumption')

st.divider()

# fuel price input
fuel_price = st.number_input("Fuel Price per Liter (Php)", value=60.0)

st.divider()

# trip details
st.write("### Trip Details")
st.write('Add, edit or delete rows. Ensure distance travelled is a valid input.')

# default data
default_data = pd.DataFrame([
    {"grouped_areas": "GMA", "cargo_weight": "4T", "cargo_type": "Dry", "distance_travelled": 80.5},
    {"grouped_areas": "North Luzon", "cargo_weight": "2T", "cargo_type": "Frozen", "distance_travelled": 450.0},
    {"grouped_areas": "Visayas", "cargo_weight": "4T", "cargo_type": "Dry", "distance_travelled": 800.0},
])

# define column config for st.data_editor
column_config = {
    "grouped_areas": st.column_config.SelectboxColumn(
        "Delivery Area",
        options=["GMA", "North Luzon", "South Luzon", "Visayas", "Mindanao"],
        required=True
    ),
    "cargo_weight": st.column_config.SelectboxColumn(
        "Cargo Weight",
        options=["2T", "4T"],
        required=True
    ),
    "cargo_type": st.column_config.SelectboxColumn(
        "Cargo Type",
        options=["Dry", "Frozen", "Combi"],
        required=True
    ),
    "distance_travelled": st.column_config.NumberColumn(
        "Distance (km)",
        min_value=0.1,
        format="%.1f",
        required=True
    )
}

# Data Editor for Input
edited_df = st.data_editor(
    default_data,
    column_config= column_config,
    num_rows='dynamic',
    use_container_width=True
)

is_predict_multiple = st.button("Predict All Trips", type="primary", use_container_width=True)

# Prediction Logic
if is_predict_multiple:
    if edited_df.empty:
        st.warning("Please add at least one trip to the table.")
    elif fuel_price is None or fuel_price <= 0:
        st.error("Please enter a valid 'Fuel Price per Liter.'")
    else:
        input_trips = []
        has_errors = False
        for index, row in edited_df.iterrows():
            try:
                processed_row = {
                    'grouped_areas': str(row['grouped_areas']).lower().replace(" ", "_"),
                    'cargo_weight': str(row['cargo_weight']).lower(),
                    'cargo_type': str(row['cargo_type']),
                    'distance_travelled': float(row['distance_travelled'])
                }

                if processed_row['distance_travelled'] <=0:
                    st.error(f"Row {index+1}: Distance (km) must be greater than 0")
                    has_errors=True
                    break
                input_trips.append(processed_row)
            except ValueError:
                st.error(f"Row {index+1}: Distance (km) must be a valid number.")
                has_errors=True
                break
            except KeyError as e:
                st.error(f"Missing expected column in data: {e}. Please ensure all columns are present.")
                has_errors=True
                break

        if not has_errors:
            with st.status("Calculating predictions for all trips...", expanded=True) as status_box:
                status_box.write("Sending batch data to FastAPI...")

            try:
                response = requests.post(FASTAPI_ENDPOINT, json=input_trips)

                if response.status_code == 200:
                    predictions = response.json()
                    status_box.write("API response received!")
                    results_df = pd.DataFrame(predictions)

                    if predictions and isinstance(predictions, list):
                        st.write("#### Batch Prediction Results")

                        original_inputs_df = edited_df.copy()
                        original_inputs_df.columns = [col.replace("_", " ").title() for col in original_inputs_df.columns]

                        if len(results_df) == len(original_inputs_df):
                            results_df['Estimated Fuel Amount (Liters)'] = results_df['predicted_fuel_liters']
                            results_df['Estimated Fuel Cost (Php)'] = round(results_df['predicted_fuel_liters'] * fuel_price, 2)
                            results_df = results_df.drop(columns=['predicted_fuel_liters'])

                            combined_df = pd.concat([original_inputs_df, results_df], axis=1)

                            st.dataframe(combined_df, use_container_width=True)
                            status_box.update(label="Batch Prediction Successful!", state="complete", expanded=False)

                        else:
                            status_box.update(label="Prediction Failed!", state="error", expanded=True)
                            st.error(f"Mismatched number of predictions ({len(results_df)}) and inputs ({len(original_inputs_df)}).")
                    else:
                        status_box.update(label="Prediction Failed!", state="error", expanded=True)
                        st.error("API returned an unexpected prediction format.")
                        st.json(predictions)
                else:
                    status_box.update(label=f"API Error: {response.status_code}", state="error", expanded=True)
                    st.error(f"Error predicting fuel consumption: {response.status_code} - {response.text}")
                    st.json(response.json())

            except requests.exceptions.ConnectionError:
                status_box.update(label="Connection Error!", state="error", expanded=True)
                st.error("Could not connect to the FastAPI server.")
                st.error(
                    f"Please ensure FastAPI is running at `{FASTAPI_ENDPOINT}` and your firewall allows connections.")
            except Exception as e:
                status_box.update(label="An unexpected error occurred!", state="error", expanded=True)
                st.error(f'An unexpected error occurred: {e}')






