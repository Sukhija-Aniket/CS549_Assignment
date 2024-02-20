from matplotlib import pyplot as plt
import subprocess
import re
import numpy as np
import json
import requests
import folium

from constants import *

## Utility Functions for Plotter ##
def getIndex(packet_size):
    for x in range(len(PACKET_SIZES)):
        if PACKET_SIZES[x] == packet_size:
            return x

def sort(x, y):
    for _ in range(len(x) - 1):
        for j in range(0, len(x) -1):
            if x[j] > x[j+1]:
                temp = x[j]
                x[j] = x[j+1]
                x[j+1] = temp
                temp = y[j]
                y[j] = y[j+1]
                y[j+1] = temp
    return x, y

def plotfunc(xparam, data, xlabel, ylabel, title, legends, check=False):
    plt.figure()
    for x in range(len(data)):
        if check:
            xparam[x], data[x] = sort(xparam[x], data[x])
            plt.plot(xparam[x], data[x], label=f"size: {legends[x]} bytes", marker='x')
        else:
            plt.plot(xparam, data[x], label=f"size: {legends[x]} bytes", marker='x')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend(fontsize=6)
    plt.title(title) 
    plt.savefig(os.path.join(PLOT_PATH, f'{title}-{xlabel}-{ylabel}.png'))
    
def plotfunc2(xvalues, yvalues, title, width=0.8):
    plt.figure()
    plt.bar(xvalues, yvalues, width=width, alpha=0.3)
    plt.xticks(np.arange(min(xvalues)-1, max(xvalues)+2, 1))
    plt.xlabel("Hop Count")
    plt.ylabel("TraceRoute Total Time")
    plt.title(title)
    plt.savefig(os.path.join(PLOT_PATH, f'{title}-hops.png'))
    
##  Utility Functions for Experiment ##
def ping_server(server, count=10, size=56):
    try:
        command = ['ping', '-c', str(count), '-s', str(size), server]
        output = subprocess.check_output(command).decode()
        print(f"Pinging {server} for packet_size {size}")
        total_time_ms = 0
        for line in output.split('\n'):
            if 'avg' in line:
                # Extract the average RTT in milliseconds
                avg_rtt_ms = float(line.split('/')[4])
                total_time_ms = avg_rtt_ms * count
                break
        if total_time_ms > 0:
            total_bytes = size * count * 2 
            total_time_sec = total_time_ms / 1000.0
            throughput_Bps = total_bytes / total_time_sec
            return avg_rtt_ms, throughput_Bps
        else: 
            print(f"Failed to get Average RTT for {server}, try again with different size")
            return None, None
    except subprocess.CalledProcessError as e:
        print(f"Failed to ping {server}: {e}")
        return None, None

def traceroute_server(server, psswd):
    try:
        # command = ['sudo','-S', 'traceroute','-T' , server] # For TCP Packets
        command = ['traceroute', server] # For UDP Packets
        cmd1 = subprocess.Popen(['echo', psswd], stdout=subprocess.PIPE)
        cmd2 = subprocess.Popen(command, stdin=cmd1.stdout, stdout=subprocess.PIPE)
        output = cmd2.stdout.read().decode()
        lines = output.split('\n')
        total_time = 0.0
        hop_count = 0
        total_count = 0
        ip_addresses = []
        for line in lines:
            # Finding all time values in the line using regex
            times = re.findall(r'(\d+\.\d+)\s*ms', line)
            uncounted = re.findall(r'\*\s\*\s\*', line)
            ipaddress = re.search(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', line)
            if ipaddress:
                ip_addresses.append(ipaddress.group())
            else:
                ip_addresses.append('* * *')
            times = [float(time) for time in times]
            if len(times):
                total_time += sum(times) / len(times) 
                hop_count += 1
                total_count += 1
            elif uncounted:
                total_count += 1

        return total_time, hop_count, total_count, ip_addresses[:-1]
    except subprocess.CalledProcessError as e:
        print(f"Failed to traceroute {server}: {e}")
        return None

# Note: It is a better way to measure throughput than Ping_Server
def iperf_server(server, port=5201):
    try:
        # Assuming the server is set up with iperf3 in server mode
        command = ['iperf3', '-c', server, '-p', str(port)]
        output = subprocess.check_output(command).decode()
        for line in output.split('\n'):
            if 'sender' in line:
                throughput = line.split()[-2]
                return float(throughput)
    except subprocess.CalledProcessError as e:
        print(f"Failed to measure throughput to {server}: {e}")
        return None

def save_map(path_ips, server_name, day_time):
    coordinates = {}
    coordinates[0] = ['31.782758', '76.995263']
    markers = []
    for __, ip in enumerate(path_ips):
        result = json.loads(requests.get('https://ipinfo.io/' + ip + '/json?token=9849b4f53692d1').text)
        if 'loc' in result.keys():
            coordinates[__] = result['loc'].split(',')
            markers.append

    
    map_center = (30.0, 77.0)
    my_map = folium.Map(location=map_center, zoom_start=2)

    markers = []
    for key, value in coordinates.items():
        markers.append(folium.Marker(location=[float(value[0]), float(value[1])], popup=f'Point {key}'))


    lines = folium.PolyLine(locations=[[float(coord[0]), float(coord[1])] for coord in coordinates.values()], color='blue')
    lines.add_to(my_map)

    # Add markers with numbers on top
    for idx, marker in enumerate(markers):
        folium.map.Marker(
            location=marker.location,
            icon=folium.DivIcon(
                icon_size=(12, 12),
                icon_anchor=(6, 6),
                html=f'<div style="font-size: 10pt; color: black; background-color: white; border: 1px solid black; border-radius: 50%; text-align: center; line-height: 12pt;">{idx}</div>'
            )
        ).add_to(my_map)

    for key, value in coordinates.items():
        lon, lat = float(value[0]), float(value[1])
        folium.Marker(location=[lon, lat], popup=f'Point {key}').add_to(my_map)
    my_map.save(f'plots/map_{day_time}_{server_name}.html')        
            