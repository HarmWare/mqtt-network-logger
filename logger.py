import paho.mqtt.client as mqtt
import json
import matplotlib.pyplot as plt
import os
from datetime import datetime

# Create a directory for log files if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Initialize data structures for plotting
time_stamps = []
vehicle_data = {"0": [], "1": [], "2": []}

# MQTT callbacks
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("#")  # Subscribe to all topics

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode('utf-8')
    
    # Log message to a file named after the topic
    with open(f'logs/{topic.replace("/", "_")}.log', 'a') as f:
        f.write(f'{datetime.now()} - {payload}\n')
    
    # Process data if topic is "sim/states"
    if topic == "sim/states":
        data = json.loads(payload)
        time_stamps.append(datetime.now())
        for vehicle_id, values in data.items():
            vehicle_data[vehicle_id].append(values)
        update_plots()

def update_plots():
    plt.clf()

    # Plot each parameter over time
    fig, axs = plt.subplots(6, 1, figsize=(10, 20), sharex=True)
    parameters = ["X", "Y", "psi", "Vx", "Vy", "omega"]

    for i, param in enumerate(parameters):
        for vehicle_id in vehicle_data:
            if len(vehicle_data[vehicle_id]) > 0:
                param_values = [data[i] for data in vehicle_data[vehicle_id]]
                axs[i].plot(time_stamps, param_values, label=f'Vehicle {vehicle_id}')
        axs[i].set_ylabel(param)
        axs[i].legend()

    axs[-1].set_xlabel('Time')

    # Plot distance between vehicles over time
    fig, ax = plt.subplots(figsize=(10, 5))
    if len(time_stamps) > 0:
        for i in range(3):
            for j in range(i + 1, 3):
                distance = [((vehicle_data[str(i)][k][0] - vehicle_data[str(j)][k][0])**2 + 
                             (vehicle_data[str(i)][k][1] - vehicle_data[str(j)][k][1])**2)**0.5 
                            for k in range(len(vehicle_data[str(i)]))]
                ax.plot(time_stamps, distance, label=f'Distance {i}-{j}')
    ax.set_ylabel('Distance (m)')
    ax.set_xlabel('Time')
    ax.legend()

    plt.tight_layout()
    plt.pause(0.1)

# Set up MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("mqtt.eclipse.org", 1883, 60)

# Start MQTT loop
client.loop_start()

# Keep the script running and update plots in real-time
plt.ion()
while True:
    plt.pause(1)
