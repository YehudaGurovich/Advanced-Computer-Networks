import sys
import parameters
import time

from typing import List, Tuple, Union
from data import open_file

from scapy.all import *


def obtain_primary_dns_servers(input_domain: str) -> List[str]:
    response = dns_packet_response(
        parameters.GOOGLE_DNS, input_domain, parameters.SOA_QTYPE)

    primary_dns_servers: List[str] = []
    if response and response.haslayer(DNS):
        # response.show()
        if response[DNS].ancount > 0:
            for i in range(response[DNS].ancount):
                record = response[DNS].an[i]
                if record.type == parameters.SOA_NUM:
                    primary_dns_server = record.mname.decode()
                    primary_dns_servers.append(primary_dns_server)

            if primary_dns_servers:
                print("Primary DNS Servers:")
                for server in primary_dns_servers:
                    print(f"- {server}")
                print()
            else:
                print("No SOA records found.")
        else:
            print("No SOA records found.")
    else:
        print("No response received.")
        exit()

    return primary_dns_servers


def current_time(start_time: time.time) -> Tuple[int, int]:
    curr_time = time.time() - start_time
    mins: int = int(curr_time // 60)
    secs: int = int(curr_time % 60)
    return mins, secs


def all_words_query(primary_dns_server: str, input_domain: str) -> List[Tuple[str, List[str]]]:
    wordlist: List[str] = open_file("combined_wordlist.txt")
    percent_total_counter = 0
    start = time.time()
    results: List[Tuple[str, List[str]]] = []

    print(f"Progress: 0% - Time: 0.00 minutes and 0.00 seconds")
    for word in wordlist:
        mins, secs = current_time(start)
        if percent_total_counter % 500 == 0 and percent_total_counter > 0:
            print(
                f"Progress: {(percent_total_counter * 100 / len(wordlist)):.2f}% - Time: {mins} minutes and {secs} seconds")
        new_domain = f"{word}.{input_domain}"

        IP_addresses = domain_IP_search(
            primary_dns_server, new_domain, parameters.A_QTYPE)

        if IP_addresses:
            results.append((new_domain, IP_addresses))
            print(
                f"Progress:{(percent_total_counter * 100 / len(wordlist)):.2f}% | Time: {mins} minutes and {secs} seconds")
            print(f">> IP Address(es) for {new_domain}: {IP_addresses}")
        percent_total_counter += 1

    mins, secs = current_time(start)
    print(f"Final Time: {mins} minutes and {secs} seconds")

    return results


def domain_IP_search(dns_dst: str, domain: str, query_type: str) -> List[str]:
    response = dns_packet_response(
        dns_dst, domain, parameters.A_QTYPE)
    IP_addresses: List[str] = []
    if response:
        for i in range(response[DNS].ancount):
            if response[DNS].an[i].type == 1:  # code for A record
                ip_address = response[DNS].an[i].rdata
                IP_addresses.append(ip_address)
    return IP_addresses


def dns_packet_response(dns_dst: str, domain: str, query_type: str) -> SndRcvList:
    # Create a DNS packet with SOA query
    dns_packet = IP(dst=dns_dst) / UDP(dport=parameters.DNS_PORT) / \
        DNS(rd=parameters.RD_BIT, qd=DNSQR(qname=domain, qtype=query_type))

    # Send the packet and receive response
    response = sr1(dns_packet, timeout=parameters.DNS_TIMEOUT,
                   verbose=parameters.DNS_PACKET_VERBOSE)
    return response


def main():

    try:
        input_domain = sys.argv[1]
        # input_domain = "jct.ac.il"
        print(f'The input domain is: {input_domain}')
    except IndexError:
        print("Please enter a domain name as an argument.")
        exit()

    # Obtain primary DNS servers
    primary_dns_servers = obtain_primary_dns_servers(input_domain)

    # Result of all words query adding the domain to the input domain
    result: List[Tuple[str, List[str]]] = []
    for server in primary_dns_servers:
        print(
            f"Querying {server} for all words in the wordlist. Expected time: 20 minutes aprox.")
        result += all_words_query(server, input_domain)

    print(result)
    print(f"We found {len(result)} domains with IP addresses.")
    # Print the results in format of domain: IP addresses
    for i in range(len(result)):
        print(f"IP Address(es) for {result[i][0]}: {result[i][1]}")

    # print(
    #     list(f"IP Address(es) for {result[i][0]}: {result[i][1]}" for i in range(len(result))))


if __name__ == "__main__":
    main()
