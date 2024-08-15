import pickle
from scapy.all import *

# Hidden warning to embed in the TCP options
hidden_warning = "Beware of pickles!"

# Convert the warning message to hexadecimal
hidden_warning_hex = hidden_warning.encode().hex()

# Create the first packet with the hidden warning in the payload
ip_warning = IP(dst="192.168.1.1")
tcp_warning = TCP(dport=80, sport=RandShort(), flags="S", options=[
                  ('NOP', None), ('NOP', None), ('Timestamp', (123456, 789012)), ('NOP', None), ('EOL', None)])
# Add the hidden warning in the payload
tcp_warning.payload = Raw(load=bytes.fromhex(hidden_warning_hex))

# This is the first packet with the "Beware of pickles!" warning
first_packet = ip_warning/tcp_warning

# Original message to hide
hidden_message = "CTF{This_is_a_hidden_message}"

# Encode the message using pickle
pickled_message = pickle.dumps(hidden_message)

# Create an IP and TCP layer with small window size to force fragmentation
ip = IP(dst="192.168.1.1")
tcp = TCP(dport=80, sport=RandShort(), flags="PA", seq=1000,
          window=2)  # Small window size for fragmentation

# List to hold all packets, starting with the first warning packet
packets = [first_packet]

# Fragment the pickled message across multiple TCP segments
for i in range(0, len(pickled_message), 8):
    # Split the pickled message into 8-byte chunks
    fragment = pickled_message[i:i+8]

    # Create the HTTP GET request fragment
    http_request = f"GET /search?q={fragment} HTTP/1.1\r\nHost: example.com\r\n\r\n"

    # Create the packet with the fragment
    packet = ip/tcp/Raw(load=http_request)

    # Append the packet to the list
    packets.append(packet)

    # Increment the sequence number for each packet
    tcp.seq += len(fragment)

# Simulate additional decoy traffic
for _ in range(10):  # Add 10 decoy packets
    ip = IP(dst="192.168.1.1")
    tcp = TCP(dport=80, sport=RandShort(), flags="PA", seq=1000, window=2)
    http_request = "GET /decoy HTTP/1.1\r\nHost: example.com\r\n\r\n"
    packet = ip/tcp/http_request
    packets.append(packet)

# Write all packets to a pcap file
wrpcap("ctf.pcap", packets)
