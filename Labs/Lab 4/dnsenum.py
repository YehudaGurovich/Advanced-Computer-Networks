import sys
import parameters
import time

from typing import List, Tuple, Any
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


def all_words_query(primary_dns_server: str, input_domain: str) -> List[Tuple[str, Tuple[str]]]:
    wordlist: List[str] = open_file("combined_wordlist.txt")
    total_counter = 0
    start = time.time()
    results: List[Tuple[str, Tuple[str]]] = []

    for word in wordlist:
        mins, secs = current_time(start)
        try:
            percent = (total_counter * 100 / len(wordlist))
        except ZeroDivisionError:
            percent = 0
        if total_counter % 500 == 0:
            print(
                f"Progress: {percent:.2f}% - Time: {mins} minutes and {secs} seconds")
        new_domain = f"{word}.{input_domain}"

        IP_addresses = domain_IP_search(
            primary_dns_server, new_domain, parameters.A_QTYPE)

        if IP_addresses:
            results.append((new_domain, tuple(IP_addresses)))
            print(
                f"Progress: {percent:.2f}% | Time: {mins} minutes and {secs} seconds")
            print(f">> Found IP-Address for {new_domain}")
        total_counter += 1

    mins, secs = current_time(start)
    print(f"Final Time: {mins} minutes and {secs} seconds\n")

    return results


def domain_IP_search(dns_dst: str, domain: str, query_type: str) -> List[str]:
    response = dns_packet_response(
        dns_dst, domain, query_type)
    IP_addresses: List[str] = []
    if response:
        for i in range(response[DNS].ancount):
            if response[DNS].an[i].type == parameters.A_NUM:
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
            f"Querying {server} For all words in the wordlist. Expected time for jct.ac.il: 20 minutes aprox.\n")
        result += all_words_query(server, input_domain)

    result = list(set(result))
    if result:
        print(f"We found {len(result)} domains with IP addresses.")
        print(
            '\n'.join(f"IP Address(es) for {item[0]}: {item[1]}" for item in result))
        # for i in range(len(result)):
        #     print(f"IP Address(es) for {result[i][0]}: {result[i][1]}")


if __name__ == "__main__":
    main()

"""Sample final output:
We found 57 domains with IP addresses.
IP Address(es) for cc.jct.ac.il: ('147.161.1.49',)
IP Address(es) for sap.jct.ac.il: ('10.1.135.25',)
IP Address(es) for bi.jct.ac.il: ('10.1.11.44',)
IP Address(es) for tftp.jct.ac.il: ('10.1.1.60',)
IP Address(es) for sus.jct.ac.il: ('10.1.6.89',)
IP Address(es) for wol.jct.ac.il: ('10.1.1.6',)
IP Address(es) for secure.jct.ac.il: ('147.161.1.49',)
IP Address(es) for amp.jct.ac.il: ('10.1.105.1',)
IP Address(es) for its.jct.ac.il: ('147.161.1.39',)
IP Address(es) for ndp.jct.ac.il: ('147.161.1.45',)
IP Address(es) for avi.jct.ac.il: ('147.161.1.46',)
IP Address(es) for lev.jct.ac.il: ('147.161.1.113',)
IP Address(es) for g.jct.ac.il: ('147.161.1.49',)
IP Address(es) for postgresql.jct.ac.il: ('10.1.6.51',)
IP Address(es) for web.jct.ac.il: ('147.161.1.37',)
IP Address(es) for api.jct.ac.il: ('147.161.1.55',)
IP Address(es) for oracle.jct.ac.il: ('10.1.6.48',)
IP Address(es) for backup.jct.ac.il: ('10.1.101.1',)
IP Address(es) for oum.jct.ac.il: ('10.1.103.2',)
IP Address(es) for vmm.jct.ac.il: ('10.1.102.21',)
IP Address(es) for awx.jct.ac.il: ('10.1.1.70',)
IP Address(es) for download.jct.ac.il: ('147.161.1.49',)
IP Address(es) for dns.jct.ac.il: ('147.161.1.4', '147.161.1.15')
IP Address(es) for fsb.jct.ac.il: ('10.1.10.1',)
IP Address(es) for ctf.jct.ac.il: ('10.1.37.90',)
IP Address(es) for kms.jct.ac.il: ('10.1.6.45',)
IP Address(es) for mail.jct.ac.il: ('147.161.1.36', '147.161.1.38', '147.161.1.29')
IP Address(es) for idm.jct.ac.il: ('10.1.11.51',)
IP Address(es) for smtp.jct.ac.il: ('147.161.1.29', '10.1.1.29', '147.161.1.36')
IP Address(es) for support.jct.ac.il: ('147.161.1.39',)
IP Address(es) for ns3.jct.ac.il: ('10.1.37.152',)
IP Address(es) for pwd.jct.ac.il: ('10.1.11.11',)
IP Address(es) for owa.jct.ac.il: ('147.161.1.49',)
IP Address(es) for vpl.jct.ac.il: ('129.159.150.173',)
IP Address(es) for mda.jct.ac.il: ('10.1.1.30',)
IP Address(es) for s.jct.ac.il: ('147.161.1.49',)
IP Address(es) for gw.jct.ac.il: ('10.1.1.254',)
IP Address(es) for exchange.jct.ac.il: ('10.1.12.161',)
IP Address(es) for omd.jct.ac.il: ('10.1.1.14',)
IP Address(es) for tfs.jct.ac.il: ('10.1.11.42',)
IP Address(es) for ca.jct.ac.il: ('10.1.12.100',)
IP Address(es) for mail.jct.ac.il: ('147.161.1.29', '147.161.1.38', '147.161.1.36')
IP Address(es) for vic.jct.ac.il: ('10.2.6.100',)
IP Address(es) for imc.jct.ac.il: ('10.1.105.5',)
IP Address(es) for nd.jct.ac.il: ('147.161.1.46',)
IP Address(es) for vro.jct.ac.il: ('10.1.102.23',)
IP Address(es) for ip.jct.ac.il: ('147.161.1.49',)
IP Address(es) for zfs.jct.ac.il: ('10.1.37.100',)
IP Address(es) for umm.jct.ac.il: ('10.1.1.99',)
IP Address(es) for cmm.jct.ac.il: ('10.1.56.13',)
IP Address(es) for moodle.jct.ac.il: ('129.159.130.77',)
IP Address(es) for oz.jct.ac.il: ('10.2.16.11',)
IP Address(es) for helpdesk.jct.ac.il: ('10.1.6.36',)
IP Address(es) for tunnel.jct.ac.il: ('10.1.37.147', '10.1.37.146', '10.1.37.149')
IP Address(es) for www.jct.ac.il: ('185.186.66.220',)
IP Address(es) for hd.jct.ac.il: ('147.161.1.50',)
IP Address(es) for efl.jct.ac.il: ('147.161.1.46',)
"""
