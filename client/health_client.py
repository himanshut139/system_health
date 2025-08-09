import platform
import psutil
import subprocess
import json
import socket
import requests
import time
import shutil

SERVER_URL="http://localhost:5000/api/report"

API_KEY = "api12345"

def get_system_info():
    info={}

    info["os"]=platform.system()
    info["os_version"]=platform.version()
    info["machine"]=platform.machine()
    info["processor"]=platform.processor()


    memory=psutil.virtual_memory()
    info["memory_total_gb"]=round(memory.total/(1024**3), 2)    #Rounding upto 2 decimal places
    info["memory_used_gb"]=round(memory.used/(1024**3), 2)
    info["memory_usage_percentage"]=memory.percent

    disk=psutil.disk_usage('/')
    info["disk_total_gb"]=round(disk.total/(1024**3),2)
    info["disk_used_gb"]=round(disk.used/(1024**3),2)
    info["disk_usage_percentage"]=disk.percent

    return info

# def get_uptime():
#     os_type=platform.system()

#     try:
#         if os_type=="Windows":
#             output=subprocess.check_output("net stats workstation", shell=True, text=True)
#             for line in output.split("\n"):
#                 if "Statistics since" in line:
#                     return line.strip()
                
#         else:
#             output=subprocess.check_output("uptime -p", shell=True, text=True)
#             return output.strip()
        
#     except Exception as e:
#         return str(e)

def send_data(data):
    try:
        headers = {
            "Content-Type": "application/json",
            "X-API-KEY": "api12345" 
        }
        response=requests.post(SERVER_URL, json=data, headers=headers)
        print("Data sent. Server responded with:", response.status_code, response.text)
    except Exception as e:
        print("Error sending data:", e)

def check_disk_encryption():
    os_type=platform.system()
    try:
        if os_type=="Windows":
            output=subprocess.check_output(
                'manage-bde -status C:', shell=True, text=True
            )
            return "Percentage encrypted: 100%" in output
        elif os_type=="Darwin":
            output=subprocess.check_output(
                ['fdesetup','status'], text=True
            )
            return "FileVault is On" in output
        elif os_type=="Linux":
            output=subprocess.check_output(
                'lsblk -o NAME,TYPE,MOUNTPOINT', shell=True, text=True
            )
            return "crypt" in output
    except Exception:
        return False
    return False

def check_os_update():
    os_type=platform.system()
    try:
        if os_type=="Windows":
            output=subprocess.check_output(
                'powershell -command "Get-WindowsUpdateLog"', shell=True, text=True
            )
            return "Update" not in output
        elif os_type=="Darwin":
            output=subprocess.check_output(
                ['softwareupdate', '-l'], text=True
            )
            return "No new software available." in output
        elif os_type == "Linux":
            if shutil.which("apt"):
                output = subprocess.check_output(
                    "apt list --upgradable", shell=True, text=True
                )
                return "upgradable" not in output
    except Exception:
        return False
    return False

def check_antivirus():
    os_type=platform.system()
    try:
        if os_type=="Windows":
            output=subprocess.check_output(
                'powershell -command "Get-MpComputerStatus"', shell=True, text=True
                )
            return "AMServiceEnabled" in output and "True" in output
        elif os_type == "Darwin":
            output = subprocess.check_output(
                "pgrep XProtect", shell=True, text=True
            )
            return bool(output.strip())
        elif os_type == "Linux":
            return shutil.which("clamd") is not None
    except Exception:
        return False
    return False

def check_sleep():
    os_type=platform.system()
    try:
        if os_type=="Windows":
            output = subprocess.check_output(
                'powercfg /query', shell=True, text=True
            )
            return "600" in output 
        elif os_type == "Darwin":
            output = subprocess.check_output(
                "pmset -g | grep sleep", shell=True, text=True
            )
            return "10" in output
        elif os_type == "Linux":
            output = subprocess.check_output(
                "gsettings get org.gnome.settings-daemon.plugins.power sleep-inactive-ac-timeout",
                shell=True, text=True
            )
            return int(output.strip()) <= 600
    except Exception:
        return False
    return False

previous_info=None

if __name__ == "__main__":
    while True:
        system_info=get_system_info()
        # system_info["uptime"]=get_uptime()

        system_info["disk_encryption"] = check_disk_encryption()
        system_info["os_up_to_date"] = check_os_update()
        system_info["antivirus"] = check_antivirus()
        system_info["sleep_ok"] = check_sleep()

        # print("Collected system info:", system_info)
        if system_info != previous_info:
            send_data(system_info)
            previous_info=system_info

        time.sleep(900)   # 15 mins