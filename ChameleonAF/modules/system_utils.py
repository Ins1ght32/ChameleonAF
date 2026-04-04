# modules/system_utils.py
import socket
import serial.tools.list_ports
import subprocess

def get_ip():
    """
    Get the local machine's IP address.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "Unavailable"

def get_com_ports():
    """
    Return a list of available COM ports, or ['--'] if none.
    """
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports] or ["--"]

def is_bluetooth_on():
    """
    Check if Bluetooth is enabled on Windows using PowerShell.
    Returns True if On, False otherwise.
    """
    ps_script = '''
    Add-Type -AssemblyName System.Runtime.WindowsRuntime
    $radioClass = [Windows.Devices.Radios.Radio, Windows.Devices.Radios, ContentType = WindowsRuntime]
    $radios = [Windows.Devices.Radios.Radio]::GetRadiosAsync().GetAwaiter().GetResult()
    ($radios | Where-Object { $_.Kind -eq "Bluetooth" }).State
    '''
    try:
        output = subprocess.check_output(["powershell", "-Command", ps_script], shell=True)
        status = output.decode().strip()
        return status == "On"
    except subprocess.CalledProcessError:
        return False
