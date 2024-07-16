import re
import subprocess
import sys

def find_processes_with_max_gpu_memory(n):
    # Run nvidia-smi command to get GPU processes
    result = subprocess.run(['nvidia-smi', '-q', '-x'], capture_output=True, text=True)
    if result.returncode != 0:
        print("Error: Failed to run nvidia-smi command.")
        return None

    # Parse XML output to extract process information
    processes = []
    for line in result.stdout.split('\n'):
        if '<process_info>' in line:
            process_info = {}
        elif '<pid>' in line:
            process_info['pid'] = int(line.strip().split('>')[1].split('<')[0])
        elif '<used_memory>' in line:
            memory_str = line.strip().split('>')[1].split('<')[0]
            memory_value = int(re.search(r'\d+', memory_str).group())
            process_info['used_memory'] = memory_value
        elif '</process_info>' in line:
            processes.append(process_info)

    # Sort processes by GPU memory usage in descending order
    processes.sort(key=lambda x: x.get('used_memory', 0), reverse=True)

    # Return top n processes
    return processes[:n]

def kill_process(pid):
    # Kill the process using its PID
    result = subprocess.run(['kill', '-9', str(pid)], capture_output=True)
    if result.returncode != 0:
        print("Error: Failed to kill process with PID:", pid)
    else:
        print("Process with PID", pid, "successfully terminated.")

if __name__ == "__main__":
    # Check if the number of processes to kill is provided as an argument
    if len(sys.argv) != 2:
        print("Usage: python script.py <number_of_processes_to_kill>")
        sys.exit(1)

    try:
        n = int(sys.argv[1])
    except ValueError:
        print("Error: The argument must be an integer.")
        sys.exit(1)

    # Find processes with max GPU memory
    processes_to_kill = find_processes_with_max_gpu_memory(n)
    if processes_to_kill:
        for process in processes_to_kill:
            print("Process with PID", process['pid'], "has GPU memory usage:", process['used_memory'], "MiB.")
            # Kill the process
            kill_process(process['pid'])
