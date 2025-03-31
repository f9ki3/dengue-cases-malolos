from flask import Flask, jsonify, request, render_template
import pandas as pd
import matplotlib
import json
matplotlib.use('Agg')  # Use non-GUI backend to prevent issues
import matplotlib.pyplot as plt
import os
import requests
import calendar
from statsmodels.tsa.statespace.sarimax import SARIMAX

app = Flask(__name__)

@app.route('/')
def root():
    return render_template('pages/index.html')

@app.route('/analytics')
def analytics():
    return render_template('pages/analytics.html')

@app.route('/geographic_mapping')
def gis():
    return render_template('pages/mapping.html')

# #API END POINTS
# BARANGAY_JSON_PATH = 'static/json/barangay.json'

# def get_lat_long(barangay):
#     """Fetch latitude and longitude from OpenStreetMap (Nominatim)."""
#     url = f"https://nominatim.openstreetmap.org/search?q={barangay},Malolos,Bulacan,Philippines&format=json"
    
#     try:
#         response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
#         response.raise_for_status()  # Raise an error for bad responses

#         data = response.json()
#         if data:
#             return float(data[0]['lat']), float(data[0]['lon'])  # Return lat, lon as float
        
#     except (requests.RequestException, IndexError, KeyError, ValueError):
#         pass  # Handle request failure or invalid data
    
#     return None, None  # Return None if no valid data found

# def load_existing_data():
#     """Load existing barangay data from JSON file."""
#     try:
#         with open(BARANGAY_JSON_PATH, 'r', encoding='utf-8') as file:
#             return json.load(file)
#     except (FileNotFoundError, json.JSONDecodeError):
#         return {'barangays': {}}  # Ensure the correct structure

# @app.route('/getBarangay')
# def getBarangay():
#     """Fetch barangay list with latitude and longitude, caching results in JSON."""
#     df = pd.read_csv('static/csv/output.csv', encoding='utf-8')
#     df = df.dropna(subset=['Barangay'])
#     barangay_list = df['Barangay'].drop_duplicates().tolist()

#     existing_data = load_existing_data()
#     existing_barangays = {k: (v['lat'], v['lon']) for k, v in existing_data.get('barangays', {}).items()}
    
#     updated_data = existing_data.get('barangays', {})  # Keep existing data
#     data_changed = False

#     for barangay in barangay_list:
#         barangay = barangay.strip()  # Remove spaces

#         if barangay in existing_barangays:
#             lat, lon = existing_barangays[barangay]
#         else:
#             lat, lon = get_lat_long(barangay)
#             if lat is not None and lon is not None:  # Store only valid data
#                 updated_data[barangay] = {"lat": lat, "lon": lon}
#                 data_changed = True  
        
#     if data_changed:
#         with open(BARANGAY_JSON_PATH, 'w', encoding='utf-8') as file:
#             json.dump({'barangays': updated_data}, file, ensure_ascii=False, indent=4)

#     return jsonify({'barangays': updated_data, 'count': len(updated_data)})

@app.route('/getBarangayList')
def getBarangayList():
    df = pd.read_csv('static/csv/output.csv', encoding='utf-8')  # Read CSV file
    barangay_list = df['Barangay'].dropna().unique().tolist()  # Remove NaN values & duplicates
    barangay_list = {
        'barangay_list': barangay_list,
        'count': len(barangay_list)
    }
    return jsonify(barangay_list)
    
@app.route('/getYear')
def getYear():
    df = pd.read_csv('static/csv/output.csv', encoding='utf-8')
    years = df['Year'].dropna().unique().tolist()
    result = {
        'years': years,
        'count': len(years)
    }

    return jsonify(result)

@app.route('/getMonths')
def getMonths():
    df = pd.read_csv('static/csv/output.csv', encoding='utf-8')
    months = df['Month'].dropna().unique().tolist()
    months = {
        'months': months,
        'count': len(months)
    }
    return jsonify(months)

@app.route('/getDengueCases')
def get_dengue_cases():
    # Load CSV file
    df = pd.read_csv('static/csv/output.csv', encoding='utf-8')

    # Ensure necessary columns exist
    required_columns = {'Barangay', 'Year', 'Month', 'Cases'}
    if not required_columns.issubset(df.columns):
        return jsonify({'error': f'Missing required columns: {required_columns - set(df.columns)}'}), 400

    # Convert 'Cases' to numeric (handle errors)
    df['Cases'] = pd.to_numeric(df['Cases'], errors='coerce')

    # Get filter parameters from URL
    group_by = request.args.get('group_by')
    barangay = request.args.get('barangay')  # Optional Barangay filter

    # If no group_by parameter is provided, return an error
    if not group_by:
        return jsonify({'error': "Missing 'group_by' parameter. Use 'group_by=Year' or 'group_by=Month'"}), 400

    # Filter by Barangay if provided
    if barangay:
        df = df[df['Barangay'].str.lower() == barangay.lower()]

    if group_by == 'Year':
        # Group by Year and sum cases, maintaining order
        grouped_cases = df.groupby('Year', as_index=False, sort=False)['Cases'].sum()
    elif group_by == 'Month':
        # Group by Year and Month, sum cases, and preserve order
        grouped_cases = df.groupby(['Year', 'Month'], as_index=False, sort=False)['Cases'].sum()
    else:
        return jsonify({'error': "Invalid 'group_by' value. Use 'Year' or 'Month'"}), 400

    return jsonify({'data': grouped_cases.to_dict(orient='records')})

# @app.route('/getDengueCasesPrediction')
# def get_dengue_cases_prediction():
#     # Load CSV file
#     df = pd.read_csv('static/csv/output.csv', encoding='utf-8')

#     # Convert Year and Month to datetime format
#     df['Date'] = pd.to_datetime(df['Year'].astype(str) + '-' + df['Month'], format='%Y-%B')

#     # Get query parameters
#     prediction_type = request.args.get('prediction', 'Month')
#     barangay_filter = request.args.get('barangay', None)

#     # If barangay is provided, filter data
#     if barangay_filter:
#         df = df[df['Barangay'].str.lower() == barangay_filter.lower()]
    
#     # Ensure there's data after filtering
#     if df.empty:
#         return jsonify({"error": "No data available for the given barangay"}), 404

#     # Aggregate cases by month
#     monthly_cases = df.groupby('Date')['Cases'].sum().reset_index()

#     if prediction_type == 'Year':
#         # Aggregate cases by year
#         yearly_cases = df.groupby(df['Date'].dt.year)['Cases'].sum().reset_index()
#         yearly_cases.rename(columns={'Date': 'Year'}, inplace=True)

#         # Fit ARIMA model for yearly data (no seasonal component)
#         model = SARIMAX(yearly_cases['Cases'], order=(2, 1, 2), seasonal_order=(0, 0, 0, 0))
#         model_fit = model.fit()

#         # Forecast next 2 years
#         future_steps = 2
#         forecast = model_fit.forecast(steps=future_steps)

#         # Generate future years
#         future_years = range(yearly_cases['Year'].max() + 1, yearly_cases['Year'].max() + 1 + future_steps)

#         # Convert to JSON
#         prediction_result = [{"year": int(year), "cases": round(float(case))} for year, case in zip(future_years, forecast)]

#     else:
#         # Fit SARIMA model for monthly data
#         model = SARIMAX(monthly_cases['Cases'], order=(2, 1, 2), seasonal_order=(1, 1, 1, 12))
#         model_fit = model.fit()

#         # Forecast next 24 months
#         future_steps = 24
#         forecast = model_fit.forecast(steps=future_steps)

#         # Generate future dates
#         future_dates = pd.date_range(start=monthly_cases['Date'].max(), periods=future_steps + 1, freq='MS')[1:]

#         # Convert to JSON
#         prediction_result = [{"date": str(date.date()), "cases": round(float(case))} for date, case in zip(future_dates, forecast)]

#     return jsonify(prediction_result)

@app.route('/getDengueCasesPrediction')
def get_dengue_cases_prediction():
    # Load CSV file
    df = pd.read_csv('static/csv/output.csv', encoding='utf-8')

    # Convert Year and Month to datetime format
    df['Date'] = pd.to_datetime(df['Year'].astype(str) + '-' + df['Month'], format='%Y-%B')

    # Get query parameters
    prediction_type = request.args.get('prediction', 'Month')
    barangay_filter = request.args.get('barangay', None)

    # If barangay is provided, filter data
    if barangay_filter:
        df = df[df['Barangay'].str.lower() == barangay_filter.lower()]
    
    # Ensure there's data after filtering
    if df.empty:
        return jsonify({"error": "No data available for the given barangay"}), 404

    # Aggregate cases by month
    monthly_cases = df.groupby('Date')['Cases'].sum().reset_index()

    if prediction_type == 'Year':
        # Aggregate cases by year
        yearly_cases = df.groupby(df['Date'].dt.year)['Cases'].sum().reset_index()
        yearly_cases.rename(columns={'Date': 'Year'}, inplace=True)

        # Fit ARIMA model for yearly data (no seasonal component)
        model = SARIMAX(yearly_cases['Cases'], order=(2, 1, 2), seasonal_order=(0, 0, 0, 0))
        model_fit = model.fit()

        # Forecast next 2 years
        future_steps = 2
        forecast = model_fit.forecast(steps=future_steps)

        # Generate future years
        future_years = range(yearly_cases['Year'].max() + 1, yearly_cases['Year'].max() + 1 + future_steps)

        # Prepare plot
        plt.figure(figsize=(8, 5))
        plt.plot(yearly_cases['Year'], yearly_cases['Cases'], marker='o', label="Actual Cases")
        plt.plot(future_years, forecast, marker='o', linestyle='dashed', label="Predicted Cases", color='red')
        plt.xlabel("Year")
        plt.ylabel("Dengue Cases")
        plt.title("Dengue Cases Prediction (Yearly)")
        plt.legend()
        plt.grid()

    else:
        # Fit SARIMA model for monthly data
        model = SARIMAX(monthly_cases['Cases'], order=(2, 1, 2), seasonal_order=(1, 1, 1, 12))
        model_fit = model.fit()

        # Forecast next 24 months
        future_steps = 24
        forecast = model_fit.forecast(steps=future_steps)

        # Generate future dates
        future_dates = pd.date_range(start=monthly_cases['Date'].max(), periods=future_steps + 1, freq='MS')[1:]

        # Prepare plot
        plt.figure(figsize=(10, 5))
        plt.plot(monthly_cases['Date'], monthly_cases['Cases'], marker='o', label="Actual Cases")
        plt.plot(future_dates, forecast, marker='o', linestyle='dashed', label="Predicted Cases", color='red')
        plt.xlabel("Date")
        plt.ylabel("Dengue Cases")
        plt.title("Dengue Cases Prediction (Monthly)")
        plt.xticks(rotation=45)
        plt.legend()
        plt.grid()

    # Save the plot
    plot_path = "static/plots/dengue_prediction.png"
    os.makedirs(os.path.dirname(plot_path), exist_ok=True)
    plt.savefig(plot_path)
    plt.close()  # Important: Close plot to free memory

    return jsonify({
        "prediction": [{"date" if prediction_type == "Month" else "year": str(date), "cases": round(float(case))} 
                        for date, case in zip(future_dates if prediction_type == "Month" else future_years, forecast)],
        "plot_url": plot_path
    })

BARANGAY_JSON_PATH = 'static/json/barangay.json'
CSV_FILE_PATH = 'static/csv/output.csv'


def get_lat_long(barangay):
    """Fetch latitude and longitude from OpenStreetMap (Nominatim)."""
    url = f"https://nominatim.openstreetmap.org/search?q={barangay},Malolos,Bulacan,Philippines&format=json"
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data:
            return float(data[0]['lat']), float(data[0]['lon'])
    except (requests.RequestException, IndexError, KeyError, ValueError):
        pass
    return None, None


def load_existing_data():
    """Load existing barangay data from JSON file."""
    try:
        with open(BARANGAY_JSON_PATH, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {'barangays': {}}


def update_barangay_json():
    """Update barangay.json with missing latitude & longitude values."""
    df = pd.read_csv(CSV_FILE_PATH, encoding='utf-8')
    barangay_list = df['Barangay'].unique()
    existing_data = load_existing_data()
    barangay_dict = existing_data.get("barangays", {})
    updated = False

    for barangay in barangay_list:
        if barangay not in barangay_dict or 'lat' not in barangay_dict[barangay]:
            lat, lon = get_lat_long(barangay)
            if lat and lon:
                barangay_dict[barangay] = {"lat": lat, "lon": lon}
                updated = True

    if updated:
        with open(BARANGAY_JSON_PATH, 'w', encoding='utf-8') as file:
            json.dump({"barangays": barangay_dict}, file, indent=4)

            
@app.route('/getBarangayCases')
def get_barangay_cases():
    update_barangay_json()  # Ensure barangay.json is updated

    # Read the CSV file
    df = pd.read_csv(CSV_FILE_PATH, encoding='utf-8')

    # Ensure required columns exist
    required_columns = {'Barangay', 'Year', 'Month', 'Cases'}
    if not required_columns.issubset(df.columns):
        return jsonify({"error": "Missing required columns in CSV"}), 400

    # Convert Year to numeric
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
    df['Cases'] = pd.to_numeric(df['Cases'], errors='coerce')

    # Ensure Month is in string format for comparison
    df['Month'] = df['Month'].astype(str).str.strip().str.lower()

    # Get user parameters
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=str)
    search = request.args.get('search', type=str)  # New search parameter

    # Validate year
    if year and (year < 1900 or year > 2100):
        return jsonify({"error": "Invalid year. Must be between 1900-2100"}), 400

    # Convert month name to number if needed
    if month:
        month = month.lower()
        month_map = {m.lower(): i for i, m in enumerate(calendar.month_name) if m}
        if month not in month_map:
            return jsonify({"error": "Invalid month. Must be a valid month name"}), 400
        month_number = month_map[month]  # Convert "november" → 11
        df = df[df['Month'] == month]

    # Filter data by year
    if year:
        df = df[df['Year'] == year]

    # Filter barangays by search term
    if search:
        df = df[df['Barangay'].str.contains(search, case=False, na=False)]  # Case-insensitive search

    # Aggregate cases by Barangay
    barangay_cases = df.groupby('Barangay')['Cases'].sum().reset_index()

    # Load existing Barangay data (latitude & longitude)
    barangay_data = load_existing_data()
    barangay_dict = barangay_data.get("barangays", {})

    # Prepare response
    result = []
    for _, row in barangay_cases.iterrows():
        barangay_name = row['Barangay']
        lat, lon = None, None
        if barangay_name in barangay_dict:
            lat = barangay_dict[barangay_name].get("lat")
            lon = barangay_dict[barangay_name].get("lon")

        result.append({
            "Barangay": barangay_name,
            "Cases": int(row["Cases"]),
            "Latitude": lat,
            "Longitude": lon
        })

    return jsonify(result)


# @app.route('/getBarangayCases')
# def get_barangay_cases():
#     update_barangay_json()  # Ensure barangay.json is updated

#     # Read the CSV file
#     df = pd.read_csv(CSV_FILE_PATH, encoding='utf-8')

#     # Ensure required columns exist
#     required_columns = {'Barangay', 'Year', 'Month', 'Cases'}
#     if not required_columns.issubset(df.columns):
#         return jsonify({"error": "Missing required columns in CSV"}), 400

#     # Convert Year to numeric
#     df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
#     df['Cases'] = pd.to_numeric(df['Cases'], errors='coerce')

#     # Ensure Month is in string format for comparison
#     df['Month'] = df['Month'].astype(str).str.strip().str.lower()

#     # Get user parameters
#     year = request.args.get('year', type=int)
#     month = request.args.get('month', type=str)

#     # Validate year
#     if year and (year < 1900 or year > 2100):
#         return jsonify({"error": "Invalid year. Must be between 1900-2100"}), 400

#     # Convert month name to number if needed
#     if month:
#         month = month.lower()
#         month_map = {m.lower(): i for i, m in enumerate(calendar.month_name) if m}
#         if month not in month_map:
#             return jsonify({"error": "Invalid month. Must be a valid month name"}), 400
#         month_number = month_map[month]  # Convert "november" → 11
#         df = df[df['Month'] == month]

#     # Filter data by year and month
#     if year:
#         df = df[df['Year'] == year]

#     # Aggregate cases by Barangay
#     barangay_cases = df.groupby('Barangay')['Cases'].sum().reset_index()

#     # Load existing Barangay data (latitude & longitude)
#     barangay_data = load_existing_data()
#     barangay_dict = barangay_data.get("barangays", {})

#     # Prepare response
#     result = []
#     for _, row in barangay_cases.iterrows():
#         barangay_name = row['Barangay']
#         lat, lon = None, None
#         if barangay_name in barangay_dict:
#             lat = barangay_dict[barangay_name].get("lat")
#             lon = barangay_dict[barangay_name].get("lon")

#         result.append({
#             "Barangay": barangay_name,
#             "Cases": int(row["Cases"]),
#             "Latitude": lat,
#             "Longitude": lon
#         })

#     return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")