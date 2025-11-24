import ipaddress
import socket
import time


class DiscoveryError(Exception):
    pass


def discover_inaugural_ip(
    cidr: str,
    scan_timeout=0.3,  # TCP connect timeout per IP
    retry_interval=2,  # seconds between full subnet scans
    total_timeout=90,  # bail out after this many seconds
):
    """
    Discover the inaugural host by scanning for exactly one SSH server
    on the target subnet. Retries until total_timeout.
    """
    network = ipaddress.ip_network(cidr)
    deadline = time.time() + total_timeout

    while time.time() < deadline:
        print("Scanning subnet for inaugural host...")

        candidates = []

        for ip in network.hosts():
            ip_str = str(ip)

            try:
                with socket.create_connection((ip_str, 22), timeout=scan_timeout) as s:
                    banner = s.recv(1024).decode(errors="ignore").lower()

                    if "ssh" in banner:
                        candidates.append(ip_str)

            except (socket.timeout, ConnectionRefusedError, OSError):
                continue

        if len(candidates) == 1:
            return candidates[0]

        if len(candidates) > 1:
            raise DiscoveryError(
                f"Multiple SSH hosts detected: {candidates}. "
                "Please isolate the inaugural node."
            )

        print(f"⏳ No host found, retrying in {retry_interval}s...")
        time.sleep(retry_interval)

    raise DiscoveryError(
        f"No inaugural host found on subnet {cidr} after {total_timeout} seconds."
    )
