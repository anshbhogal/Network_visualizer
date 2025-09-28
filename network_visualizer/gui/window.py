# GUI Window components
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLineEdit, QLabel, QComboBox
from gui.visualization import NetworkVisualizer
from core.devices import Client, Switch, Router, Server
from core.simulation import build_packet, simulate_tcp_handshake, simulate_icmp_ping, simulate_packet_loss, simulate_collision
from core.protocols import encapsulate_packet, decapsulate_packet
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Network Data Flow Visualizer")
        self.setGeometry(100, 100, 1200, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        self.setup_network_devices()
        self.setup_ui()

    def setup_ui(self):
        # Input and Protocol Selection
        input_layout = QHBoxLayout()
        self.message_input = QLineEdit("Hello Server")
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        self.protocol_select = QComboBox()
        self.protocol_select.addItems(["TCP", "UDP", "ICMP"])
        input_layout.addWidget(QLabel("Input:"))
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(QLabel("Protocol:"))
        input_layout.addWidget(self.protocol_select)
        input_layout.addWidget(self.send_button)
        self.main_layout.addLayout(input_layout)

        # Device Flow Diagram
        self.network_visualizer = NetworkVisualizer(self.devices, self.connections)
        self.main_layout.addWidget(self.network_visualizer)
        # self.network_visualizer.headers_updated.connect(self.update_osi_panel) # Removed connection
        self.network_visualizer.node_reached.connect(self._process_node_reached) # Connect node_reached to a new handler
        self.network_visualizer.animation_step_completed.connect(self._advance_simulation) # Connect animation_step_completed

        # OSI Layer Visualization Panel
        self.osi_panel = QVBoxLayout()
        self.osi_panel_label = QLabel("OSI Stack:")
        self.osi_panel.addWidget(self.osi_panel_label)
        self.main_layout.addLayout(self.osi_panel)

    def setup_network_devices(self):
        self.client = Client("Client", "192.168.1.100", "00:11:22:33:44:01")
        self.switch = Switch("Switch", "192.168.1.1", "00:11:22:33:44:02")
        self.router = Router("Router", "192.168.1.1", "00:11:22:33:44:03", routing_table={"192.168.1.": self.switch})
        self.server = Server("Server", "192.168.1.10", "00:11:22:33:44:04")

        self.devices = [self.client, self.switch, self.router, self.server]
        self.connections = [
            (self.client, self.switch),
            (self.switch, self.router),
            (self.router, self.server)
        ]

        self.current_simulation_steps = []
        self.current_step_idx = 0

    def send_message(self):
        message = self.message_input.text()
        protocol = self.protocol_select.currentText()

        self.current_simulation_steps = []
        self.current_step_idx = 0

        if protocol == "TCP":
            handshake_steps = simulate_tcp_handshake(self.client, self.server)
            # For TCP handshake, we want to show the headers at each logical step of the handshake
            # rather than at each physical hop. So, the path for each step is the full path.
            for step in handshake_steps:
                if step["from"] == self.client.name:
                    path = [self.client.name, self.switch.name, self.router.name, self.server.name]
                else:
                    path = [self.server.name, self.router.name, self.switch.name, self.client.name]
                self.current_simulation_steps.append({"event": step["event"], "headers": step["headers"], "path": path})

        elif protocol == "ICMP":
            ping_steps = simulate_icmp_ping(self.client, self.server)
            # Similar to TCP, for ICMP, we process logical steps.
            for step in ping_steps:
                if step["from"] == self.client.name:
                    path = [self.client.name, self.switch.name, self.router.name, self.server.name]
                else:
                    path = [self.server.name, self.router.name, self.switch.name, self.client.name]
                self.current_simulation_steps.append({"event": step["event"], "headers": step["headers"], "path": path})

        else:
            # Simulate encapsulation for UDP/Other
            frame, headers_list = encapsulate_packet(message, protocol, 
                                                     src_mac=self.client.mac, dst_mac=self.switch.mac,
                                                     src_ip=self.client.ip, dst_ip=self.server.ip)
            
            # Simulate CSMA/CD collision (simplified retransmission for now)
            if simulate_collision():
                self.current_simulation_steps.append({"event": "Collision Detected! Retransmitting...", "headers": [{"layer": "Simulation", "data": "Collision Detected! Retransmitting..."}], "path": []})
                # Re-encapsulate after collision
                frame, headers_list = encapsulate_packet(message, protocol, 
                                                         src_mac=self.client.mac, dst_mac=self.switch.mac,
                                                         src_ip=self.client.ip, dst_ip=self.server.ip)

            # Simulate packet loss
            if simulate_packet_loss(frame) is None:
                self.current_simulation_steps.append({"event": "Packet Lost!", "headers": [{"layer": "Simulation", "data": "Packet Lost!"}], "path": []})
            else:
                # For non-TCP/ICMP, a single step of animation and OSI update
                path = [self.client.name, self.switch.name, self.router.name, self.server.name]
                self.current_simulation_steps.append({"event": "Packet Sent", "headers": headers_list, "path": path})
        
        # Start the first step of the animation
        if self.current_simulation_steps:
            self._process_next_simulation_step() # Start the first step

    def _process_node_reached(self, node_name):
        # This is called when a packet reaches an intermediate node in an animation path
        # For now, we will keep this simple and let _process_next_simulation_step handle major updates.
        pass # You could add more detailed OSI updates here for each hop if needed.

    def _advance_simulation(self):
        # This slot is called when an animation step completes, or immediately for non-animated steps.
        self.current_step_idx += 1
        self._process_next_simulation_step()

    def _process_next_simulation_step(self):
        if self.current_step_idx < len(self.current_simulation_steps):
            step = self.current_simulation_steps[self.current_step_idx]
            
            if "path" in step and step["path"]:
                # This is an animation step, start the animation
                self.network_visualizer.start_packet_animation(step["path"], step["headers"])
                self.update_osi_panel(step["headers"])
                print(f"Processing step {self.current_step_idx}: {step['event']}")
                # Do NOT increment current_step_idx here. _advance_simulation will do it after animation completes.
            else:
                # This is a non-animated step (e.g., collision or packet loss message)
                self.update_osi_panel(step["headers"])
                print(f"Processing step {self.current_step_idx}: {step['event']}")
                self._advance_simulation() # Trigger next step immediately as no animation is involved

        else:
            print("Simulation Finished.")
            self.current_simulation_steps = []
            self.current_step_idx = 0
            self.network_visualizer.packet_animation_timer.stop() # Ensure timer is stopped
            self.network_visualizer.packet_position = None # Clear packet from display
            self.network_visualizer.draw_network()

    def update_osi_panel(self, headers_list):
        # Clear previous OSI layer information
        for i in reversed(range(self.osi_panel.count())): 
            widget = self.osi_panel.itemAt(i).widget()
            if widget is not None and widget is not self.osi_panel_label: # Keep the main label
                widget.setParent(None)
                widget.deleteLater()

        for header_info in headers_list:
            layer_label = QLabel(f"<b>{header_info['layer']} Layer:</b>")
            self.osi_panel.addWidget(layer_label)
            if "header" in header_info:
                header_data_label = QLabel(f"Header: {header_info['header']}")
                self.osi_panel.addWidget(header_data_label)
            if "data" in header_info:
                data_label = QLabel(f"Data: {header_info['data']}")
                self.osi_panel.addWidget(data_label)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
