import sys
import parameters
import time

from typing import List
from data import open_file

from scapy.all import *

input_string = sys.argv[1]
print(f'The input string is: {input_string}')

# def dns_filter(pkt: dict) -> bool:
#     return "DNS" in pkt


def primary_dns_servers() -> List[str]:
    response = dns_packet_response(
        parameters.GOOGLE_DNS, input_string, parameters.SOA_QTYPE)

    # Print the full response
    if response and response.haslayer(DNS):
        response.show()
        primary_dns_servers = []
        if response[DNS].ancount > 0:
            for i in range(response[DNS].ancount):
                record = response[DNS].an[i]
                if record.type == parameters.SOA_QTYPE:
                    primary_dns_server = record.mname.decode()
                    primary_dns_servers.append(primary_dns_server)

            if primary_dns_servers:
                print("Primary DNS Servers:")
                for server in primary_dns_servers:
                    print(f"- {server}")
            else:
                print("No SOA records found.")
        else:
            print("No SOA records found.")
    else:
        print("No response received.")
        exit()

    return primary_dns_servers


def obtain_wordlist() -> List[str]:
    with open("combined_wordlist.txt", "r") as file:
        wordlist = file.readlines()
    return wordlist


# def current_time() -> tuple:
#     curr_time = time


def all_words_query() -> List[str]:
    wordlist: List[str] = obtain_wordlist()
    for word in wordlist:
        percent_total_counter = 0
        start = time.time()
    for word in wordlist:
        t = time.time() - start
        mins = int(t // 60)
        secs = int(t % 60)
        if percent_total_counter % 500 == 0 and percent_total_counter != 0:
            print(
                f"{(percent_total_counter * 100 / len(wordlist)):.2f}% - Time: {mins} minutes and {secs} seconds")
        new_domain = f"{word}.{input_string}"

    return wordlist


def word_IP_search(dns_dst: str, domain: str, query_type: str) -> List[str]:

    response = dns_packet_response(
        primary_dns_server, new_domain, parameters.A_QTYPE)
    IP_addresses: List[str] = []
    if response:
        for i in range(response[DNS].ancount):
            if response[DNS].an[i].type == 1:  # code for A record
                ip_address = response[DNS].an[i].rdata
                IP_addresses.append(ip_address)
    return IP_addresses


def dns_packet_response(dns_dst: str, domain: str, query_type: str) -> DNS:
    # Create a DNS packet with SOA query
    dns_packet = IP(dst=dns_dst) / UDP(dport=parameters.DNS_PORT) / \
        DNS(rd=parameters.RD_BIT, qd=DNSQR(qname=domain, qtype=query_type))

    # Send the packet and receive response
    response = sr1(dns_packet, timeout=parameters.DNS_TIMEOUT,
                   verbose=parameters.DNS_PACKET_VERBOSE)
    return response


def main():

    primary_dns_servers = primary_dns_servers()

    percent_total_counter = 0
    start = time.time()
    for word in wordlist:
        t = time.time() - start
        mins = int(t // 60)
        secs = int(t % 60)
        if percent_total_counter % 500 == 0 and percent_total_counter != 0:
            print(
                f"{(percent_total_counter * 100 / len(wordlist)):.2f}% - Time: {mins} minutes and {secs} seconds")
        new_domain = f"{word}.{input_string}"
        response = dns_packet_response(
            primary_dns_server, new_domain, parameters.A_QTYPE)
        IP_addresses: list[str] = []
        if response:
            for i in range(response[DNS].ancount):
                if response[DNS].an[i].type == 1:  # code for A record
                    ip_address = response[DNS].an[i].rdata
                    IP_addresses.append(ip_address)
            if IP_addresses:
                print(f"""{(percent_total_counter * 100 / len(wordlist)):.2f}% | Time: {mins} minutes and {secs} seconds |
    IP Addresses for {new_domain}: {IP_addresses}""")
        percent_total_counter += 1
    t = time.time() - start
    mins = int(t // 60)
    secs = int(t % 60)
    print(f"Final Time: {mins} minutes and {secs} seconds")


    # packet = sniff(lfilter=dns_filter, count=10,
    #                prn=lambda x: x.summary())
    # print(packet.show())
if __name__ == "__main__":
    main()
