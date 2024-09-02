from scapy.all import *
import string
import random
import pickle
import base64

SPLIT_LENGTH = 12
NUMBER_OF_PACKETS = 30

# Create a list of random packets
packets = []
real_hidden_message = "The mystery to be solved lies ahead. Be careful on the way!"
pickle_message = pickle.dumps(real_hidden_message)

# Calculate padding length
padding_length = (SPLIT_LENGTH - (len(pickle_message) %
                  SPLIT_LENGTH)) % SPLIT_LENGTH
padded_pickle_message = pickle_message + b'\x00' * padding_length

# Determine the length needed for number padding
max_index_length = len(str(len(padded_pickle_message) // SPLIT_LENGTH))

# Create message parts with zero-padded indices
message_parts = [base64.b64encode(padded_pickle_message[i:i+SPLIT_LENGTH]).decode() + "ctf" + f"{i // SPLIT_LENGTH:0{max_index_length}d}"
                 for i in range(0, len(padded_pickle_message), SPLIT_LENGTH)]

# Length of each message part (including "ctf" and zero-padded index)
message_length = len(message_parts[0])

# Insert the real hidden message parts into random packets
for part in message_parts:
    packet = Ether(src=RandMAC(), dst=RandMAC()) / IP(src=RandIP(), dst=RandIP()) / \
        UDP(sport=RandShort(), dport=RandShort()) / Raw(part.encode())
    packets.append(packet)

# Add some additional random packets with fake messages of the same length
for i in range(len(message_parts), NUMBER_OF_PACKETS - 1):
    # Generate a random base fake message
    base_fake_message = ''.join(random.choices(
        string.ascii_letters + string.digits, k=message_length))
    # Create a fake message part with "ftc" and a zero-padded number
    fake_message = base_fake_message + "ftc" + \
        f"{random.randint(0, len(message_parts)):0{max_index_length}d}"
    # Ensure that the fake message length is consistent with message parts
    fake_message = fake_message[:message_length]
    packet = Ether(src=RandMAC(), dst=RandMAC()) / IP(src=RandIP(), dst=RandIP()) / \
        UDP(sport=RandShort(), dport=RandShort()) / Raw(fake_message.encode())
    packets.append(packet)

# Unsort the packets
random.shuffle(packets)

# Insert the first packet with the direct message
packets.insert(0, Ether(src=RandMAC(), dst=RandMAC()) / IP(src=RandIP(), dst=RandIP()) /
               UDP(sport=RandShort(), dport=RandShort()) / Raw(b"Beware of the 64 pickles!"))

# Write the packets to a PCAP file
wrpcap("ctf2.pcap", packets)
