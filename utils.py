from matplotlib import pyplot as plt
import subprocess
import re
import numpy as np

from constants import *

## Utility Functions for Plotter ##
def getIndex(packet_size):
    for x in range(len(PACKET_SIZES)):
        if PACKET_SIZES[x] == packet_size:
            return x

def sort(x, y):
    for i in range(len(x) - 1):
        for j in range(i, len(x) -1):
            if x[j] < x[j+1]:
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
            plt.plot(xparam[x], data[x], label=f"size: {legends[x]} bytes")
        else:
            plt.plot(xparam, data[x], label=f"size: {legends[x]} bytes")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    plt.title(title) 
    plt.savefig(os.path.join(PLOT_PATH, f'{title}-{xlabel}-{ylabel}.png'))
    
def plotfunc2(xvalues, yvalues, title, width=0.8):
    plt.figure()
    print(xvalues, yvalues)
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
        command = ['sudo','-S', 'traceroute','-T' , server] # For TCP Command
        cmd1 = subprocess.Popen(['echo', psswd], stdout=subprocess.PIPE)
        cmd2 = subprocess.Popen(command, stdin=cmd1.stdout, stdout=subprocess.PIPE)
        output = cmd2.stdout.read().decode()
        lines = output.split('\n')
        total_time = 0.0
        hop_count = 0
        total_count = 0
        for line in lines:
            # Finding all time values in the line using regex
            times = re.findall(r'(\d+\.\d+)\s*ms', line)
            uncounted = re.findall(r'\*\s\*\s\*', line)
            times = [float(time) for time in times]
            if len(times):
                total_time += sum(times) / len(times) 
                hop_count += 1
                total_count += 1
            elif uncounted:
                total_count += 1

        return total_time, hop_count, total_count 
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
