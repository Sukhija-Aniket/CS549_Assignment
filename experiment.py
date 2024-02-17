import subprocess
import time
import os
import json
from constants import *
from utils import *
from dotenv import load_dotenv

load_dotenv()

# Main Program to Execute
daytime = input('noon | evening | night: ')
ping_results = {}
traceroute_results = {}
for i, server in enumerate(SERVERS):
    print(f"Starting test for {server}")
    for size in PACKET_SIZES: 
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        delay, throughput = ping_server(server, size=size)
        ping_results[timestamp] = {'server_address': server, 'server_name': SERVER_NAMES[i], 'packet_size': size, 'delay': delay, 'throughput': throughput}
        time.sleep(2)
    
    psswd = os.getenv('sudo_password')
    total_time, hop_count, total_hops, path_ips = traceroute_server(server, psswd)
    traceroute_results[timestamp] = {'server_address': server, 'server_name': SERVER_NAMES[i] , 'total_time': total_time, 'hop_count': hop_count, 'total_hops': total_hops, 'path_ips': path_ips}
    time.sleep(5)

with open(f'outputs/ping_test_results_{daytime}.json', 'w') as file:
    json.dump(ping_results, file, indent=4)
    
with open(f'outputs/traceroute_test_results_{daytime}.json', 'w') as file:
    json.dump(traceroute_results, file, indent=4)

print(f"Experiment for {daytime} completed\nResults saved to:\n\tping_test_results_{daytime}.json\n\ttraceroute_test_results_{daytime}.json")
