from flask import Flask, render_template, request, jsonify
import subprocess
import platform
import mysql.connector

app = Flask(__name__)

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="12345",
        database="network_monitoring"
    )

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
        
        # Store in database
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
    
    # Store in database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO latency_data (location, latency) VALUES (%s, %s)", (location, average_latency))
    conn.commit()
    cursor.close()
    conn.close()
    
    recommendation = recommend_improvements(average_latency)
    
    if average_latency > 200:  # Example threshold for instability
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
        
        if max_latency - min_latency > 10:
            message = "Your location is unstable. Probability of Internet outage is higher. It is advised to either improve the ISP provided router or use a wired connection."
        else:
            message = "Your location is stable."
        
        return jsonify({'message': message})
    
    return jsonify({'message': "Not enough data to determine stability."})
if __name__ == '__main__':
    app.run(debug=True)