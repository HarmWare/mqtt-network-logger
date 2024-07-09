**MQTT Communication and Visualization Script**

This Python script demonstrates MQTT communication with a Mosquitto broker and real-time visualization of data received from various topics. Key functionalities include:

1. **MQTT Communication**:
   - The script connects to an MQTT broker (`mqtt.eclipse.org`) and subscribes to all topics (`#`).
   - It logs all received messages into separate log files (`logs/<topic_name>.log`).

2. **Data Processing**:
   - Specifically processes messages from the "sim/states" topic, which contain data about the positions and velocities of multiple vehicles.
   - Parses JSON-formatted messages and stores data for plotting.

3. **Real-Time Visualization**:
   - Uses `matplotlib` for real-time plotting of vehicle parameters (X, Y, psi, Vx, Vy, omega) over time.
   - Plots the distances between pairs of vehicles over time, providing insights into their relative positions.

4. **Usage**:
   - Requires `paho-mqtt` and `matplotlib` libraries.
   - Runs continuously, updating plots as new data arrives from the MQTT broker.

This script is ideal for monitoring and analyzing real-time data streams from a network of vehicles or similar IoT devices, providing visual insights into their dynamics and interactions.
