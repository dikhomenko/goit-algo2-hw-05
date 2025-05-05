import time
from hyper_log_log import HyperLogLog
import os
import json


def load_ip_addresses(file_path):
    """
    Load IP addresses from a log file, ignoring invalid lines.
    :param file_path: Path to the log file.
    :return: List of valid IP addresses.
    """
    ip_addresses = []
    with open(file_path, "r") as file:
        for line in file:
            try:
                log_entry = json.loads(line.strip())  # Parse the line as JSON
                ip = log_entry.get("remote_addr")
                if ip and is_valid_ip(ip):
                    ip_addresses.append(ip)
            except json.JSONDecodeError:
                # Ignore lines that are not valid JSON
                continue
    return ip_addresses


def is_valid_ip(ip):
    """
    Validate an IP address.
    """
    parts = ip.split(".")
    if len(parts) != 4:
        return False
    for part in parts:
        if not part.isdigit() or not (0 <= int(part) <= 255):
            return False
    return True


def exact_count(ip_addresses):
    """
    Count unique IP addresses using a set.
    """
    return len(set(ip_addresses))


def approximate_count(ip_addresses, p=10):
    """
    Count unique IP addresses using HyperLogLog.
    """
    hll = HyperLogLog(p=p)
    for ip in ip_addresses:
        hll.add(ip)
    return hll.count()


if __name__ == "__main__":
    # Path to the log file
    # log_file_path = "lms-stage-access.log"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_file_path = os.path.join(script_dir, "lms-stage-access.log")

    # Load IP addresses
    print("Loading IP addresses...")
    ip_addresses = load_ip_addresses(log_file_path)
    print(f"Loaded {len(ip_addresses)} IP addresses.")

    # Exact count
    print("Performing exact count...")
    start_time = time.time()
    exact_result = exact_count(ip_addresses)
    exact_time = time.time() - start_time
    print(f"Exact count: {exact_result} (Time: {exact_time:.2f} seconds)")

    # Approximate count
    print("Performing approximate count...")
    start_time = time.time()
    approximate_result = approximate_count(ip_addresses)
    approximate_time = time.time() - start_time
    print(
        f"Approximate count: {approximate_result} (Time: {approximate_time:.2f} seconds)"
    )

    # Comparison table
    print("\nРезультати порівняння:")
    print(f"{'Метод':<25}{'Унікальні елементи':<20}{'Час виконання (сек.)':<20}")
    print(f"{'Точний підрахунок':<25}{exact_result:<20}{exact_time:<20.4f}")
    print(f"{'HyperLogLog':<25}{approximate_result:<20}{approximate_time:<20.4f}")
