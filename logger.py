import paho.mqtt.client as mqtt
import json
import matplotlib.pyplot as plt
import os
from datetime import datetime

# Create a directory for log files if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Initialize data structures for plotting
time_stamps = []  # Stores timestamps of received messages
vehicle_data = {"0": [], "1": [], "2": []}  # Stores data for each vehicle

# MQTT callbacks

def on_connect(client, userdata, flags, rc):
    """
    Callback function called when the client connects to the MQTT broker.

    Parameters:
    - client: MQTT client instance
    - userdata: User data
    - flags: Response flags sent by the broker
    - rc: Connection result code
    """
    print("Connected with result code " + str(rc))
    client.subscribe("#")  # Subscribe to all topics when connected

def on_message(client, userdata, msg):
    """
    Callback function called when a message is received from the MQTT broker.

    Parameters:
    - client: MQTT client instance
    - userdata: User data
    - msg: MQTT message object containing topic, payload, etc.
    """
    topic = msg.topic
    payload = msg.payload.decode('utf-8')  # Decode the payload to string
    
    # Log message to a file named after the topic
    with open(f'logs/{topic.replace("/", "_")}.log', 'a') as f:
        f.write(f'{datetime.now()} - {payload}\n')
    
    # Process data if topic is "sim/states"
    if topic == "sim/states":
        data = json.loads(payload)  # Parse JSON data
        time_stamps.append(datetime.now())  # Record the timestamp of this message
        for vehicle_id, values in data.items():
            vehicle_data[vehicle_id].append(values)  # Store data for each vehicle
        update_plots()  # Update plots after receiving new data

def update_plots():
    """
    Function to update matplotlib plots based on received data.
    """
    plt.clf()  # Clear existing plots
    
    # Plot each parameter over time
    fig, axs = plt.subplots(6, 1, figsize=(10, 20), sharex=True)
    parameters = ["X", "Y", "psi", "Vx", "Vy", "omega"]

    for i, param in enumerate(parameters):
        for vehicle_id in vehicle_data:
            if len(vehicle_data[vehicle_id]) > 0:
                # Extract parameter values for the current vehicle
                param_values = [data[i] for data in vehicle_data[vehicle_id]]
                axs[i].plot(time_stamps, param_values, label=f'Vehicle {vehicle_id}')
        axs[i].set_ylabel(param)  # Set y-axis label
        axs[i].legend()  # Show legend for each subplot

    axs[-1].set_xlabel('Time')  # Set x-axis label for the last subplot

    # Plot distance between vehicles over time
    fig, ax = plt.subplots(figsize=(10, 5))
    if len(time_stamps) > 0:
        for i in range(3):
            for j in range(i + 1, 3):
                # Calculate distance between vehicle i and vehicle j
                distance = [((vehicle_data[str(i)][k][0] - vehicle_data[str(j)][k][0])**2 + 
                             (vehicle_data[str(i)][k][1] - vehicle_data[str(j)][k][1])**2)**0.5 
                            for k in range(len(vehicle_data[str(i)]))]
                ax.plot(time_stamps, distance, label=f'Distance {i}-{j}')
    ax.set_ylabel('Distance (m)')  # Set y-axis label
    ax.set_xlabel('Time')  # Set x-axis label
    ax.legend()  # Show legend for distance plot

    plt.tight_layout()  # Adjust subplot layout
    plt.pause(0.1)  # Pause to allow time for plotting

# Set up MQTT client
client = mqtt.Client()
client.on_connect = on_connect  # Set the on_connect callback function
client.on_message = on_message  # Set the on_message callback function

client.connect("mqtt.eclipse.org", 1883, 60)  # Connect to MQTT broker

# Start MQTT loop to handle incoming messages asynchronously
client.loop_start()

# Keep the script running and update plots in real-time
plt.ion()  # Enable interactive mode for matplotlib
while True:
    plt.pause(1)  # Pause execution to allow for real-time updates
