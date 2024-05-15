import re
import subprocess

def find_process_with_max_gpu_memory():
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

    # Find process with max GPU memory usage
    max_memory_process = max(processes, key=lambda x: x.get('used_memory', 0))
    return max_memory_process

def kill_process(pid):
    # Kill the process using its PID
    result = subprocess.run(['kill', '-9', str(pid)], capture_output=True)
    if result.returncode != 0:
        print("Error: Failed to kill process with PID:", pid)
    else:
        print("Process with PID", pid, "successfully terminated.")

if __name__ == "__main__":
    # Find process with max GPU memory
    max_memory_process = find_process_with_max_gpu_memory()
    if max_memory_process:
        print("Process with PID", max_memory_process['pid'], "has the highest GPU memory usage:", max_memory_process['used_memory'], "MiB.")
        # Kill the process
        kill_process(max_memory_process['pid'])
