import os
import sys
import subprocess
from pathlib import Path
from daemons.utils import logger

log = logger.Logger('launcher', log_level=logger.Logger.INFO)

def get_py_files(path):
    return [file for file in path.glob("*.py")]

def start_process(file, processes):
    process_name = file.stem
    if process_name not in processes:
        process = subprocess.Popen([sys.executable, str(file)])
        processes[process_name] = process
        log.data(f"Process '{process_name}' started.")
    else:
        log.warn(f"Process '{process_name}' is already running.")

def stop_process(process_name, processes):
    if process_name in processes:
        processes[process_name].terminate()
        del processes[process_name]
        log.warn(f"Process '{process_name}' stopped.")
    else:
        log.error(f"No process found with the name '{process_name}'.")

def main():
    
    folder_path = 'daemons/'
    path = Path(folder_path)
    py_files = get_py_files(path)

    processes = {}

    while True:
        command = input("").lower()
        if command.startswith("start"):
            _, *args = command.split()
            if "all" in args:
                for file in py_files:
                    start_process(file, processes)
            else:
                for arg in args:
                    matching_files = [file for file in py_files if file.stem == arg]
                    if matching_files:
                        start_process(matching_files[0], processes)
                    else:
                        log.error(f"No .py file found with the name '{arg}'.")
        elif command.startswith("stop"):
            _, *args = command.split()
            if "all" in args:
                for process_name in list(processes.keys()):
                    stop_process(process_name, processes)
            else:
                for arg in args:
                    stop_process(arg, processes)
        elif command == "exit" or command == "quit":
            for process in processes.values():
                process.terminate()
            break

if __name__ == "__main__":
    main()
