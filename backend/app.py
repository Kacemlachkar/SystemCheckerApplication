from flask import Flask , jsonify
from flask_cors import CORS
import psutil
import GPUtil
from dataclasses import dataclass, asdict
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@dataclass
class CPUInfo:
    physical_cores: int
    total_cores: int
    max_freq: str
    min_freq: str
    current_freq: str
    usage: str

@dataclass
class RAMInfo:
    total: str
    available: str
    used: str
    usage: str
    swap_total: str
    swap_used: str
    swap_usage: str

@dataclass
class DiskInfo:
    device: str
    mountpoint: str
    fstype: str
    total: str
    used: str
    free: str
    usage: str

@dataclass
class NetInfo:
    bytes_sent: str
    bytes_received: str

@dataclass
class GPUInfo:
    id: int
    name: str
    total_memory: str
    used_memory: str
    free_memory: str
    load: str
    temperature: str

@app.route('/api/cpu', methods=['GET'])
def get_cpu_info():
    try:
        cpu_info = CPUInfo(
            physical_cores=psutil.cpu_count(logical=False),
            total_cores=psutil.cpu_count(logical=True),
            max_freq=f"{psutil.cpu_freq().max:.2f}Mhz",
            min_freq=f"{psutil.cpu_freq().min:.2f}Mhz",
            current_freq=f"{psutil.cpu_freq().current:.2f}Mhz",
            usage=f"{psutil.cpu_percent(interval=1)}%"
        )
        return jsonify(asdict(cpu_info))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ram', methods=['GET'])
def get_ram_info():
    try:
        ram = psutil.virtual_memory()
        swap = psutil.swap_memory()
        ram_info = RAMInfo(
            total=f"{ram.total / (1024**3):.2f} GB",
            available=f"{ram.available / (1024**3):.2f} GB",
            used=f"{ram.used / (1024**3):.2f} GB",
            usage=f"{ram.percent}%",
            swap_total=f"{swap.total / (1024**3):.2f} GB",
            swap_used=f"{swap.used / (1024**3):.2f} GB",
            swap_usage=f"{swap.percent}%"
        )
        return jsonify(asdict(ram_info))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/disks', methods=['GET'])
def get_disk_info():
    try:
        partitions = psutil.disk_partitions()
        disk_info_list = []
        for partition in partitions:
            usage = psutil.disk_usage(partition.mountpoint)
            disk_info = DiskInfo(
                device=partition.device,
                mountpoint=partition.mountpoint,
                fstype=partition.fstype,
                total=f"{usage.total / (1024**3):.2f} GB",
                used=f"{usage.used / (1024**3):.2f} GB",
                free=f"{usage.free / (1024**3):.2f} GB",
                usage=f"{usage.percent}%"
            )
            disk_info_list.append(asdict(disk_info))
        return jsonify(disk_info_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/network', methods=['GET'])
def get_net_info():
    try:
        net_io = psutil.net_io_counters()
        net_info = NetInfo(
            bytes_sent=f"{net_io.bytes_sent / (1024**2):.2f} MB",
            bytes_received=f"{net_io.bytes_recv / (1024**2):.2f} MB"
        )
        return jsonify(asdict(net_info))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/gpu', methods=['GET'])
def get_gpu_info():
    try:
        gpus = GPUtil.getGPUs()
        gpu_info_list = []
        for gpu in gpus:
            gpu_info = GPUInfo(
                id=gpu.id,
                name=gpu.name,
                total_memory=f"{gpu.memoryTotal} MB",
                used_memory=f"{gpu.memoryUsed} MB",
                free_memory=f"{gpu.memoryFree} MB",
                load=f"{gpu.load * 100:.1f}%",
                temperature=f"{gpu.temperature} °C"
            )
            gpu_info_list.append(asdict(gpu_info))
        return jsonify(gpu_info_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
