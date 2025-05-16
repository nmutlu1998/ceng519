import socket
from scapy.all import DNS, DNSRR

def start_dns_listener():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', 53))
    print("DNS listener started on port 53")
    
    while True:
        data, address = sock.recvfrom(4096)
        dns = DNS(data)
        print("\n=== Received DNS Packet ===")
        dns.show()

        if dns.qr == 0 and dns.qd is not None:
            qname = dns.qd.qname.decode()
            transaction_id = dns.id
            dns_response = DNS(
                id=transaction_id,
                qr=1,
                aa=1,
                qd=dns.qd,
                an=DNSRR(rrname=qname, rdata="1.2.3.4", ttl=60)
            )

            sent = sock.sendto(bytes(dns_response), address)

if __name__ == "__main__":
    start_dns_listener()
