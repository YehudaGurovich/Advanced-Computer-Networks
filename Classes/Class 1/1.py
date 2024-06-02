import scapy.all as scapy

p = scapy.sniff(count=2)
p.show()