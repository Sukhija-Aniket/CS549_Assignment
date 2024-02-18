from constants import *
from utils import *

def delay_througput_plots():
    results = []
    for i in range(len(DAYTIMES)):
        with open(f'outputs/ping_test_results_{DAYTIMES[i]}.json') as f:
            results.append(json.load(f))
    
    mp_delay = {}
    mp_throughput = {}
    for  result in results:
        for _, value in result.items():  
            packet_size = getIndex(value['packet_size'])
            server_name = value['server_name']
            delay = value['delay']
            throughput = value['throughput']
            
            if not mp_delay.__contains__(server_name):
                mp_delay[server_name] = [[], [], []]
                mp_throughput[server_name] = [[], [], []]
                
            mp_delay[server_name][packet_size].append(delay)
            mp_throughput[server_name][packet_size].append(throughput)
            
    for server_name, values in mp_delay.items():
        plotfunc(DAYTIMES, values, 'Time of the Day', 'Delay', server_name, PACKET_SIZES)
    for server_name, values in mp_throughput.items():
        plotfunc(DAYTIMES, values, 'Time of the Day', 'Throughput', server_name, PACKET_SIZES)
    for server_name in SERVER_NAMES:
        plotfunc(mp_delay[server_name], mp_throughput[server_name], 'Delay', 'Throughput', server_name, PACKET_SIZES, check=True)            

def traceroute_plots():
    results = []
    for i in range(len(DAYTIMES)):
        with open(f'outputs/traceroute_test_results_{DAYTIMES[i]}.json') as f:
            results.append(json.load(f))
            
    mp_count = {}
    mp_time = {}
    for result in results:
        for _, values in result.items():
            hop_count = values['hop_count']
            total_time = values['total_time']
            server_name = values['server_name']
            save_map(values['path_ips'], server_name, DAYTIMES[i])
            
            if not mp_count.__contains__(server_name):
                mp_count[server_name] = []
                mp_time[server_name] = []
            
            mp_count[server_name].append(hop_count)
            mp_time[server_name].append(total_time)
            
    for server_name in SERVER_NAMES:
        plotfunc2(mp_count[server_name], mp_time[server_name], server_name, width=0.8)
            
delay_througput_plots()
traceroute_plots()