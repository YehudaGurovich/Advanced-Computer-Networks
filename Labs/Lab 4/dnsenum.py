import sys
import parameters
import time
from data import open_file

from scapy.all import *

input_string = sys.argv[1]
print(f'The input string is: {input_string}')

# def dns_filter(pkt: dict) -> bool:
#     return "DNS" in pkt

# def domain_search(domain: str, list_words: str) -> str:

#     for word in list_words:
#         new_domain = f"{word}.{domain}"
#         print(f"Checking: {new_domain}")
#         response = dns_packet_response(new_domain)

#     return response


def dns_packet_response(dns_dst: str, domain: str, query_type: str) -> DNS:
    # Create a DNS packet with SOA query
    dns_packet = IP(dst=dns_dst) / UDP(dport=parameters.DNS_PORT) / \
        DNS(rd=parameters.RD_BIT, qd=DNSQR(qname=domain, qtype=query_type))

    # Send the packet and receive response
    response = sr1(dns_packet, timeout=parameters.DNS_TIMEOUT,
                   verbose=parameters.DNS_PACKET_VERBOSE)
    return response


def main():

    response = dns_packet_response(
        parameters.GOOGLE_DNS, input_string, parameters.SOA_QTYPE)
    # Print the full response
    if response and response.haslayer(DNS):
        response.show()
        primary_dns_server = response[DNS].an[0].mname.decode()
        print(f"Primary DNS Server: {primary_dns_server}")
    else:
        print("No response received.")
        exit()

    # Read the wordlist file
    wordlist = open_file("combined_wordlist.txt")

    # response = dns_packet("amp.jct.ac.il")
    # response.show()
    # IP_addresses = []
    # for i in range(response[DNS].ancount):
    #     if response[DNS].an[i].type == 1:  # code for A record
    #         ip_address = response[DNS].an[i].rdata
    #         IP_addresses.append(ip_address)
    #         print(f"IP Address: {ip_address}")
    # if IP_addresses:
    #     print(f"IP Addresses for amp.jct.ac.il: {IP_addresses}")

    counter = 0
    start = time.time()
    for word in wordlist:
        t = time.time() - start
        mins = int(t // 60)
        secs = int(t % 60)
        if counter % 500 == 0 and counter != 0:
            print(
                f"{(counter * 100 / len(wordlist)):.2f}% - Time: {mins} minutes and {secs} seconds")
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
                print(f"""{(counter * 100 / len(wordlist)):.2f}% | Time: {mins} minutes and {secs} seconds |
    IP Addresses for {new_domain}: {IP_addresses}""")
        counter += 1
    t = time.time() - start
    mins = int(t // 60)
    secs = int(t % 60)
    print(f"Final Time: {mins} minutes and {secs} seconds")

    # packet = sniff(lfilter=dns_filter, count=10,
    #                prn=lambda x: x.summary())
    # print(packet.show())
if __name__ == "__main__":
    main()
