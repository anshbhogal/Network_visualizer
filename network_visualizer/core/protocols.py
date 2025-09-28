# Protocol handling logic
from scapy.all import Ether, IP, TCP, UDP, ICMP

def encapsulate_packet(message, protocol="TCP", src_mac="00:00:00:00:00:00", dst_mac="FF:FF:FF:FF:FF:FF", src_ip="192.168.1.100", dst_ip="192.168.1.1"):
    headers = []

    # Application Layer (simplified)
    app_data = message
    headers.append({"layer": "Application", "data": app_data})

    # TLS/SSL Encryption (simplified)
    if protocol == "TCP":
        encrypted_data = f"[ENCRYPTED]:{app_data}"
        headers.append({"layer": "TLS/SSL", "data": encrypted_data})
        app_data = encrypted_data

    # Transport Layer
    if protocol == "TCP":
        transport_header = TCP(sport=12345, dport=80)
    elif protocol == "UDP":
        transport_header = UDP(sport=12345, dport=53)
    elif protocol == "ICMP":
        transport_header = ICMP() # ICMP doesn't have a transport layer header in the traditional sense
    else:
        raise ValueError("Unsupported protocol")
    
    transport_segment = transport_header / app_data if protocol != "ICMP" else transport_header
    headers.append({"layer": "Transport", "header": transport_header.summary(), "data": transport_segment.load if hasattr(transport_segment, 'load') else ''})

    # Network Layer
    network_header = IP(src=src_ip, dst=dst_ip)
    network_packet = network_header / transport_segment
    headers.append({"layer": "Network", "header": network_header.summary(), "data": network_packet.load if hasattr(network_packet, 'load') else ''})

    # Data Link Layer
    data_link_header = Ether(src=src_mac, dst=dst_mac)
    data_link_frame = data_link_header / network_packet
    headers.append({"layer": "Data Link", "header": data_link_header.summary(), "data": data_link_frame.load if hasattr(data_link_frame, 'load') else ''})

    return data_link_frame, headers

def decapsulate_packet(packet):
    decapsulation_steps = []
    
    # Data Link Layer
    if Ether in packet:
        eth_header = packet[Ether]
        decapsulation_steps.append({"layer": "Data Link", "header": eth_header.summary(), "data": packet.load if hasattr(packet, 'load') else ''})
        packet = packet[Ether].payload
    
    # Network Layer
    if IP in packet:
        ip_header = packet[IP]
        decapsulation_steps.append({"layer": "Network", "header": ip_header.summary(), "data": packet.load if hasattr(packet, 'load') else ''})
        packet = packet[IP].payload
    
    # Transport Layer
    if TCP in packet:
        tcp_header = packet[TCP]
        decapsulation_steps.append({"layer": "Transport", "header": tcp_header.summary(), "data": packet.load if hasattr(packet, 'load') else ''})
        packet = packet[TCP].payload
    elif UDP in packet:
        udp_header = packet[UDP]
        decapsulation_steps.append({"layer": "Transport", "header": udp_header.summary(), "data": packet.load if hasattr(packet, 'load') else ''})
        packet = packet[UDP].payload
    elif ICMP in packet:
        icmp_header = packet[ICMP]
        decapsulation_steps.append({"layer": "Transport", "header": icmp_header.summary(), "data": packet.load if hasattr(packet, 'load') else ''})
        packet = packet[ICMP].payload
        
    # TLS/SSL Decryption (simplified)
    if isinstance(packet, bytes) and packet.startswith(b'[ENCRYPTED]:'):
        decrypted_data = packet[len(b'[ENCRYPTED]:'):].decode('utf-8')
        decapsulation_steps.append({"layer": "TLS/SSL", "data": "[DECRYPTED]:" + decrypted_data})
        packet = decrypted_data

    # Application Layer
    if packet:
        decapsulation_steps.append({"layer": "Application", "data": str(packet)})
    
    return decapsulation_steps
