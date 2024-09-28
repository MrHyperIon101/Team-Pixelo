from flask import Flask, render_template, request, jsonify
import subprocess
import platform
import mysql.connector
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg') 
import numpy as np
from sklearn.linear_model import LinearRegression

app = Flask(__name__)
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="12345",
        database="network_monitoring"
    )

def generate_latency_graph(location, dark_mode=False):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT latency FROM latency_data WHERE location = %s", (location,))
    latencies = [row[0] for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()

    if latencies:
        plt.figure(figsize=(10, 6))
        plt.plot(latencies, marker='o', color='white' if dark_mode else 'black')
        plt.title(f'Latency Data for {location}', color='white' if dark_mode else 'black')
        plt.xlabel('Time (Spikes indicate higher latency, which can suggest network congestion or issues.)', color='white' if dark_mode else 'black')
        plt.ylabel('Latency (ms)', color='white' if dark_mode else 'black')
        plt.grid(True, color='gray' if dark_mode else 'lightgray')

        # Set facecolor to transparent and adjust tick colors
        ax = plt.gca()
        ax.set_facecolor('none')
        ax.tick_params(axis='x', colors='white' if dark_mode else 'black')
        ax.tick_params(axis='y', colors='white' if dark_mode else 'black')

        # Save the plot as an image with a transparent background
        plt.savefig('static/latency_plot.png', transparent=True)
        plt.close()
@app.route('/generate_graph', methods=['POST'])
def generate_graph():
    data = request.json
    location = data.get('location')
    dark_mode = data.get('darkMode', False)  # Default to False if not provided
    generate_latency_graph(location, dark_mode)
    return jsonify({'message': 'Graph generated successfully'})

def generate_latency_graph(location, dark_mode=False):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT latency FROM latency_data WHERE location = %s", (location,))
    latencies = [row[0] for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()

    if latencies:
        plt.figure(figsize=(10, 6))
        plt.plot(latencies, marker='o', color='white' if dark_mode else 'black')
        plt.title(f'Latency Data for {location}', color='white' if dark_mode else 'black')
        plt.xlabel('Sample', color='white' if dark_mode else 'black')
        plt.ylabel('Latency (ms)', color='white' if dark_mode else 'black')
        plt.grid(True, color='gray' if dark_mode else 'lightgray')

        # Set facecolor to transparent and adjust tick colors
        ax = plt.gca()
        ax.set_facecolor('none')
        ax.tick_params(axis='x', colors='white' if dark_mode else 'black')
        ax.tick_params(axis='y', colors='white' if dark_mode else 'black')

        # Save the plot as an image with a transparent background
        plt.savefig('static/latency_plot.png', transparent=True)
        plt.close()
@app.route('/')
def home():
    return render_template('index.html')

def measure_latency(ip_address):
    os_type = platform.system()
    command = ['ping', '-n', '4', ip_address] if os_type == 'Windows' else ['ping', '-c', '4', ip_address]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        lines = result.stdout.splitlines()
        latencies = []
        for line in lines:
            if 'time=' in line:
                time_part = line.split('time=')[1].split('ms')[0]
                latencies.append(float(time_part))
        
        average_latency = sum(latencies) / len(latencies) if latencies else 0
        return average_latency
    except Exception as e:
        return str(e)

def recommend_improvements(latency):
    if latency > 100:
        return "High latency detected. Consider moving closer to your router or using a wired LAN connection."
    elif latency > 50:
        return "Moderate latency detected. If possible, move closer to your router."
    else:
        return "Latency is good."

@app.route('/ping', methods=['POST'])
def ping():
    data = request.json
    ip_address = data.get('ip')
    location = data.get('location')
    
    os_type = platform.system()
    try:
        if os_type.lower() == "windows":
            output = subprocess.run(['ping', '-n', '4', ip_address], capture_output=True, text=True)
        else:
            output = subprocess.run(['ping', '-c', '4', ip_address], capture_output=True, text=True)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO latency_data (location, latency) VALUES (%s, %s)", (location, 0))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'result': output.stdout})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/check_latency', methods=['POST'])
def check_latency():
    ip_address = request.json.get('ip')
    location = request.json.get('location')
    average_latency = measure_latency(ip_address)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO latency_data (location, latency) VALUES (%s, %s)", (location, average_latency))
    conn.commit()
    cursor.close()
    conn.close()
    
    recommendation = recommend_improvements(average_latency)
    
    if average_latency > 200:
        recommendation += " This location has very unstable internet. High probability of outage detected."
    
    return jsonify({
        'average_latency': average_latency,
        'recommendation': recommendation
    })

@app.route('/locations', methods=['GET'])
def get_locations():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT location FROM latency_data")
    locations = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    
    return jsonify(locations)
@app.route('/check_stability', methods=['POST'])
def check_stability():
    location = request.json.get('location')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT latency FROM latency_data WHERE location = %s", (location,))
    latencies = [row[0] for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    
    if len(latencies) > 2:
        max_latency = max(latencies)
        min_latency = min(latencies)
        
        if max_latency - min_latency > 40:
            message = "Your location is unstable. Probability of Internet outage is higher. It is advised to either improve the ISP provided router or use a wired connection."
        else:
            message = "Your location is stable."
        
        return jsonify({'message': message})
    
    return jsonify({'message': "Not enough data to determine stability."})
@app.route('/analyze', methods=['POST'])
def analyze():
    location = request.json.get('location')
    generate_latency_graph(location)
    return jsonify({'message': 'Analysis complete'})
if __name__ == '__main__':
    app.run(debug=True)
