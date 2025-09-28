# Network simulation logic
from scapy.all import IP, TCP, UDP, ICMP
import random
from core.protocols import encapsulate_packet # Added import for encapsulate_packet

def build_packet(message, protocol="TCP", dst_ip="192.168.1.1"):
    if protocol == "TCP":
        pkt = IP(dst=dst_ip)/TCP(dport=80)/message
    elif protocol == "UDP":
        pkt = IP(dst=dst_ip)/UDP(dport=53)/message
    elif protocol == "ICMP":
        pkt = IP(dst=dst_ip)/ICMP()/message
    else:
        raise ValueError("Unsupported protocol")
    return pkt

def simulate_tcp_handshake(client, server):
    handshake_steps = []

    # Step 1: Client sends SYN
    syn_packet = client.send_syn(server.ip)
    _, syn_headers = encapsulate_packet(str(syn_packet[TCP].payload), "TCP", 
                                        src_mac=client.mac, dst_mac="FF:FF:FF:FF:FF:FF", # Assuming broadcast to switch
                                        src_ip=client.ip, dst_ip=server.ip)
    handshake_steps.append({"event": "Client sends SYN", "packet": syn_packet, "headers": syn_headers, "from": client.name, "to": server.name})

    # Step 2: Server receives SYN, sends SYN-ACK
    # For simulation, we assume the server processes and responds
    syn_ack_packet = IP(dst=client.ip)/TCP(dport=client.send_syn(server.ip).dport, sport=80, flags="SA", 
                                          seq=random.randint(0, 0xFFFFFFFF), ack=syn_packet[TCP].seq + 1)
    _, syn_ack_headers = encapsulate_packet(str(syn_ack_packet[TCP].payload), "TCP", 
                                              src_mac=server.mac, dst_mac="FF:FF:FF:FF:FF:FF", # Assuming broadcast to switch
                                              src_ip=server.ip, dst_ip=client.ip)
    handshake_steps.append({"event": "Server sends SYN-ACK", "packet": syn_ack_packet, "headers": syn_ack_headers, "from": server.name, "to": client.name})

    # Step 3: Client receives SYN-ACK, sends ACK
    ack_packet = client.send_ack(server.ip, seq=syn_packet[TCP].seq + 1, ack=syn_ack_packet[TCP].seq + 1)
    _, ack_headers = encapsulate_packet(str(ack_packet[TCP].payload), "TCP", 
                                        src_mac=client.mac, dst_mac="FF:FF:FF:FF:FF:FF",
                                        src_ip=client.ip, dst_ip=server.ip)
    handshake_steps.append({"event": "Client sends ACK", "packet": ack_packet, "headers": ack_headers, "from": client.name, "to": server.name})

    return handshake_steps

def simulate_icmp_ping(client, server):
    ping_steps = []

    # Step 1: Client sends ICMP Echo Request
    echo_request_packet = client.send_icmp_echo_request(server.ip)
    _, echo_request_headers = encapsulate_packet(str(echo_request_packet[ICMP].payload), "ICMP", 
                                                    src_mac=client.mac, dst_mac="FF:FF:FF:FF:FF:FF",
                                                    src_ip=client.ip, dst_ip=server.ip)
    ping_steps.append({"event": "Client sends ICMP Echo Request", "packet": echo_request_packet, "headers": echo_request_headers, "from": client.name, "to": server.name})

    # Step 2: Server receives ICMP Echo Request, sends Echo Reply
    echo_reply_packet = IP(dst=client.ip)/ICMP(type="echo-reply", id=echo_request_packet[ICMP].id, seq=echo_request_packet[ICMP].seq)
    _, echo_reply_headers = encapsulate_packet(str(echo_reply_packet[ICMP].payload), "ICMP", 
                                                  src_mac=server.mac, dst_mac="FF:FF:FF:FF:FF:FF",
                                                  src_ip=server.ip, dst_ip=client.ip)
    ping_steps.append({"event": "Server sends ICMP Echo Reply", "packet": echo_reply_packet, "headers": echo_reply_headers, "from": server.name, "to": client.name})

    return ping_steps

def simulate_packet_loss(packet):
    if random.random() < 0.2: # 20% chance of packet loss
        print("Packet lost!")
        return None
    return packet

def simulate_collision():
    if random.random() < 0.3: # 30% chance of collision
        print("Collision detected!")
        return True
    return False
