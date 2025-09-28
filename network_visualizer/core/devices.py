# Device definitions
import random
from scapy.all import IP, TCP, UDP, ICMP, Ether # Added Scapy imports

class Device:
    def __init__(self, name, ip, mac):
        self.name = name
        self.ip = ip
        self.mac = mac

    def __str__(self):
        return f"{self.name} (IP: {self.ip}, MAC: {self.mac})"

class Client(Device):
    def __init__(self, name, ip, mac):
        super().__init__(name, ip, mac)

    def send_syn(self, dst_ip):
        return IP(dst=dst_ip)/TCP(dport=80, flags="S")

    def send_ack(self, dst_ip, seq, ack):
        return IP(dst=dst_ip)/TCP(dport=80, flags="A", seq=seq, ack=ack)

    def send_icmp_echo_request(self, dst_ip):
        return IP(dst=dst_ip)/ICMP(type="echo-request")


class Switch(Device):
    def __init__(self, name, ip, mac):
        super().__init__(name, ip, mac)
        self.mac_table = {}

    def learn_mac(self, mac, port):
        self.mac_table[mac] = port

    def forward_frame(self, frame):
        # Simplified forwarding logic
        dst_mac = frame.dst
        if dst_mac in self.mac_table:
            return self.mac_table[dst_mac] # Return port to forward to
        else:
            return "broadcast" # Unknown MAC, flood all ports

class Router(Device):
    def __init__(self, name, ip, mac, routing_table=None):
        super().__init__(name, ip, mac)
        self.routing_table = routing_table if routing_table is not None else {}

    def route_packet(self, packet):
        # Simplified routing logic
        dst_ip = packet.dst
        # In a real scenario, this would involve more complex routing table lookups
        for destination, next_hop in self.routing_table.items():
            if dst_ip.startswith(destination): # Simple prefix matching
                return next_hop
        return "drop" # No route found

    def update_headers(self, packet, new_src_mac, new_dst_mac):
        # Update MAC addresses when crossing a router
        if "Ether" in packet:
            packet[Ether].src = new_src_mac
            packet[Ether].dst = new_dst_mac
        return packet

class Server(Device):
    def __init__(self, name, ip, mac):
        super().__init__(name, ip, mac)
