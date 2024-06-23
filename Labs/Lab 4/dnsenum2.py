import sys
import parameters
import time
from data import open_file

from scapy.all import *


def dns_packet_response(dns_dst: str, domain: str, query_type: str) -> DNS:
    # Create a DNS packet with SOA query
    dns_packet = IP(dst=dns_dst) / UDP(dport=parameters.DNS_PORT) / \
        DNS(rd=parameters.RD_BIT, qd=DNSQR(qname=domain, qtype=query_type))

    # Send the packet and receive response
    response = sr1(dns_packet, timeout=parameters.DNS_TIMEOUT,
                   verbose=parameters.DNS_PACKET_VERBOSE)
    return response


def main():

    try:
        input_string = sys.argv[1]
        # input_string = "jct.ac.il"
        print(f'The input domain is: {input_string}')
    except IndexError:
        print("Please enter a domain name as an argument.")
        exit()
    response = dns_packet_response(
        parameters.GOOGLE_DNS, input_string, parameters.SOA_QTYPE)
    # Print the full response
    if response and response.haslayer(DNS):
        # response.show()
        primary_dns_server = response[DNS].an[0].mname.decode()
        print(f"Primary DNS Server: {primary_dns_server}")
    else:
        print("No response received.")
        exit()

    # Read the wordlist file
    wordlist = open_file("combined_wordlist.txt")

    final_results = []
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
        print(primary_dns_server, new_domain, parameters.A_QTYPE)
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
                final_results.append((new_domain, IP_addresses))
        counter += 1
    t = time.time() - start
    mins = int(t // 60)
    secs = int(t % 60)
    print(f"Final Time: {mins} minutes and {secs} seconds")

    for result in final_results:
        print(f"Domain: {result[0]} | IP Address(es): {result[1]}")


if __name__ == "__main__":
    main()
