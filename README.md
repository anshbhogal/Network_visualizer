# Network Data Flow Visualizer

## Overview
This project is a Network Data Flow Visualizer with a PyQt5 GUI that simulates packet encapsulation, device-to-device travel, and decapsulation. It also includes advanced features like packet loss, CSMA/CD collisions, and TLS/SSL encryption, and is extendable to real packet capture.

## Features
- **Packet Simulation:** Simulate encapsulation/decapsulation of TCP, UDP, and ICMP packets.
- **Device-to-Device Flow:** Visualize packet movement between Client, Switch, Router, and Server devices.
- **OSI Layer Visualization:** Display header details at each OSI layer.
- **Protocol Variations:** Simulate TCP 3-way handshake, UDP direct packets, and ICMP ping/reply.
- **Advanced Features:** 
    - **Packet Loss:** Simulate random packet drops.
    - **CSMA/CD Collisions:** Simulate Ethernet collisions and retransmissions.
    - **TLS/SSL Encryption:** Visualize encrypted TCP payloads.
- **Interactive GUI:** PyQt5 based interface for input, protocol selection, and network visualization.

## Project Structure
```
network_visualizer/
├── main.py
├── gui/
│   ├── __init__.py
│   ├── window.py
│   ├── visualization.py
├── core/
│   ├── __init__.py
│   ├── simulation.py
│   ├── protocols.py
│   ├── devices.py
├── assets/   # icons for client/router/server
└── requirements.txt
└── LICENSE
```

## Setup
1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd network_visualizer
   ```
2. Install the required libraries:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
To run the application, navigate to the `network_visualizer` directory and execute `main.py`:
```bash
python main.py
```

### GUI Controls
- **Input:** Enter a message to be sent as a packet.
- **Protocol:** Select the desired protocol (TCP, UDP, ICMP).
- **Send Button:** Initiates the packet simulation and visualization.

## Extending to Real Packet Capture (Optional)
Phase 7 describes how to extend the visualizer to capture and display real network traffic using Scapy's `sniff` function. This would involve:
1. Modifying `gui/window.py` to add controls for initiating packet capture.
2. Implementing a function in `core/simulation.py` to use `scapy.all.sniff`.
3. Adapting the `NetworkVisualizer` and `update_osi_panel` functions to display captured packet data.

## Future Enhancements (Phase 8)
- **Playback Controls:** Add Play, Pause, Step functionality for animations.
- **Export:** Option to export packet journeys as GIF/video.
- **Detailed Documentation:** Further enhance project documentation.
