from flask import Flask, jsonify, request
import requests
from statistics import mean
from time import time

app = Flask(__name__)

WINDOW_SIZE = 10
numbers_window = []

# Mock third-party API URLs (replace these with actual URLs)
API_ENDPOINTS = {
    'p': 'https://thirdparty.com/api/prime',
    'f': 'https://thirdparty.com/api/fibonacci',
    'e': 'https://thirdparty.com/api/even',
    'r': 'https://thirdparty.com/api/random'
}

# Helper function to fetch numbers from third-party APIs
def fetch_numbers(number_type):
    url = API_ENDPOINTS.get(number_type)
    if not url:
        return []

    try:
        start_time = time()
        response = requests.get(url, timeout=0.5)
        elapsed_time = time() - start_time
        
        if response.status_code == 200 and elapsed_time < 0.5:
            numbers = response.json().get('numbers', [])
            return list(set(numbers))  # Ensure uniqueness
    except requests.exceptions.RequestException:
        pass
    
    return []

@app.route('/numbers/<number_id>', methods=['GET'])
def get_numbers(number_id):
    global numbers_window

    if number_id not in API_ENDPOINTS:
        return jsonify({"error": "Invalid number ID"}), 400
    
    # Store the previous state of the window
    prev_state = numbers_window.copy()

    # Fetch new numbers
    new_numbers = fetch_numbers(number_id)
    
    # Update the window with new numbers, ensuring uniqueness
    for num in new_numbers:
        if num not in numbers_window:
            if len(numbers_window) < WINDOW_SIZE:
                numbers_window.append(num)
            else:
                # Replace the oldest number with the new one
                numbers_window.pop(0)
                numbers_window.append(num)

    # Calculate the average if the window is full
    if len(numbers_window) >= WINDOW_SIZE:
        avg_value = mean(numbers_window)
    else:
        avg_value = mean(numbers_window) if numbers_window else 0

    # Create the response
    response = {
        "windowPrevState": prev_state,
        "windowCurrState": numbers_window,
        "numbers": new_numbers,
        "avg": round(avg_value, 2)
    }

    return jsonify(response)

if __name__ == '_main_':
    app.run(host='0.0.0.0', port=9876)