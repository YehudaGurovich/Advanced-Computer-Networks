from scapy.all import *
from typing import List, Tuple


def obtain_ips_from_files(file1: str, file2: str) -> Tuple[List[str], List[str]]:
    f1_ips = []
    f2_ips = []
    with open(file1, 'r') as f1:
        f1_ips = f1.readlines()
    with open(file2, 'r') as f2:
        f2_ips = f2.readlines()

    return f1_ips, f2_ips


def compare_files(file1: str, file2: str) -> bool:
    f1_ips = []
    f2_ips = []
    with open(file1, 'r') as f1:
        f1_ips = f1.readlines()
    with open(file2, 'r') as f2:
        f2_ips = f2.readlines()

    if len(f1_ips) != len(f2_ips):
        return False

    return True


def count_equal_ips(file1: str, file2: str) -> int:

    list1, list2 = obtain_ips_from_files(file1, file2)
    list1 = [ip.strip() for ip in list1]
    list2 = [ip.strip() for ip in list2]
    set_list1 = set(list1)
    set_list2 = set(list2)

    count = 0
    for ip1 in set_list1:
        for ip2 in set_list2:
            if ip1 == ip2:
                count += 1
                break

    return count


def analyze_syn_flood(pcap_file: str, output_file: str):
    packets = rdpcap(pcap_file)
    syn_packets, ack_packets, total_packets = {}, {}, {}

    for pkt in packets:
        if IP in pkt and TCP in pkt:
            src_ip, dst_ip, flags = pkt[IP].src, pkt[IP].dst, pkt[TCP].flags
            total_packets[src_ip] = total_packets.get(src_ip, 0) + 1

            if flags == 'S':
                syn_packets[src_ip] = syn_packets.get(src_ip, 0) + 1
            elif flags == 'SA':
                ack_packets[dst_ip] = ack_packets.get(dst_ip, 0) + 1

    suspicious_ips = set()
    for ip, syn_count in syn_packets.items():
        total_count = total_packets[ip]
        syn_ratio = syn_count / total_count
        ack_count = ack_packets.get(ip, 0)
        ack_ratio = ack_count / total_count if ack_count > 0 else 0

        if (syn_count > 50 and syn_ratio > 0.8) or (syn_count > 20 and syn_ratio > 0.9) or (syn_count > 10 and syn_ratio > 0.95 and ack_ratio < 0.1):
            suspicious_ips.add(ip)

    with open(output_file, 'w') as f:
        for ip in sorted(suspicious_ips):
            f.write(f"{ip}\n")

    print(
        f"Analysis complete. {len(suspicious_ips)} suspicious IPs have been written to {output_file}")


if __name__ == "__main__":
    pcap_file_path = "SYNflood.pcapng"
    test_ips_file_path = "attackersListFiltered.txt"
    output_file_path = "suspicious_ips.txt"

    analyze_syn_flood(pcap_file_path, output_file_path)
    num_equal_ips = count_equal_ips(test_ips_file_path, output_file_path)
    print(f"Number of equal IPs: {num_equal_ips}")
