# Network visualization components
import networkx as nx
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtCore import QTimer, pyqtSignal

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)
        self.setParent(parent)

class NetworkVisualizer(QWidget):
    headers_updated = pyqtSignal(list) # This signal is no longer needed for OSI panel updates, but kept for potential future tooltip implementation
    node_reached = pyqtSignal(str) # New signal to indicate node reached
    animation_step_completed = pyqtSignal() # New signal for when a single animation path is done

    def __init__(self, devices=None, connections=None):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # self.headers_updated = pyqtSignal(list) # Removed from here

        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        self.layout.addWidget(self.canvas)

        self.graph = nx.Graph()
        self.devices = devices if devices is not None else []
        self.connections = connections if connections is not None else []

        self.current_packet_headers = None
        self.packet_headers_for_tooltips = [] # Added for packet header tooltips

        self.init_network()

    def init_network(self):
        self.graph.clear()
        for device in self.devices:
            self.graph.add_node(device.name, device=device)
        
        for conn in self.connections:
            self.graph.add_edge(conn[0].name, conn[1].name)

        self.pos = nx.spring_layout(self.graph) # or other layout algorithms
        self.draw_network()
        
        self.packet_path = []
        self.packet_idx = 0
        self.packet_animation_timer = QTimer()
        self.packet_animation_timer.timeout.connect(self.animate_packet)

    def draw_network(self):
        self.canvas.axes.clear()
        nx.draw(self.graph, pos=self.pos, ax=self.canvas.axes, with_labels=True, node_color='lightblue', node_size=2000, font_size=10, font_weight='bold')
        
        if hasattr(self, 'packet_position') and self.packet_position is not None:
            self.draw_packet(self.packet_position)

        self.canvas.draw()

    def draw_packet(self, position):
        # Draw a small red circle for the packet
        self.canvas.axes.plot(position[0], position[1], 'ro', markersize=10)

    def update_network(self):
        self.draw_network()

    def start_packet_animation(self, path, headers_history=None):
        self.packet_path = path
        self.packet_idx = 0
        self.packet_headers_for_tooltips = headers_history if headers_history is not None else []
        if self.packet_path:
            self.packet_position = self.pos[self.packet_path[0]]
            self.packet_animation_timer.start(100) # Animate every 100 ms
        else:
            self.packet_position = None
            self.packet_animation_timer.stop()
        self.draw_network()

    def animate_packet(self):
        if self.packet_idx < len(self.packet_path) - 1:
            start_node = self.packet_path[self.packet_idx]
            end_node = self.packet_path[self.packet_idx + 1]
            
            start_pos = self.pos[start_node]
            end_pos = self.pos[end_node]

            # Simple linear interpolation for now
            # In a real animation, you might want more steps between nodes
            self.packet_position = ((start_pos[0] + end_pos[0]) / 2, (start_pos[1] + end_pos[1]) / 2) 
            
            # if self.packet_idx < len(self.packet_headers_for_tooltips):
            #     self.update_packet_headers(self.packet_headers_for_tooltips[self.packet_idx])
            #     self.headers_updated.emit(self.current_packet_headers) # Emit signal with current headers

            self.packet_idx += 1
            self.draw_network()
            self.node_reached.emit(end_node) # Emit signal when packet reaches a node
        else:
            self.packet_animation_timer.stop()
            self.packet_position = None # Packet reached destination
            self.current_packet_headers = None # Clear headers
            # self.headers_updated.emit([]) # Emit empty list to clear headers display
            self.draw_network()
            self.animation_step_completed.emit() # Emit signal that animation step is completed

    # def update_packet_headers(self, headers):
    #     self.current_packet_headers = headers
    #     # Emit a signal here to update the GUI for OSI stack visualization
    #     # For now, we will just print it.
    #     print("Current Packet Headers:", self.current_packet_headers)

    def set_packet_headers_for_tooltips(self, headers_list):
        self.packet_headers_for_tooltips = headers_list
