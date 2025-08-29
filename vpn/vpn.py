import subprocess
import time

class VPNConnection:
    def __init__(self, vps_host, ssh_key, local_port=1080, ssh_user="root", forward_port=5000):
        self.vps_host = vps_host
        self.ssh_key = ssh_key
        self.local_port = local_port      # SOCKS5 proxy
        self.ssh_user = ssh_user
        self.forward_port = forward_port  # Flask port forward
        self.proc = None

    def start_tunnel(self):
        cmd = [
            "ssh",
            "-i", self.ssh_key,
            "-o", "StrictHostKeyChecking=no",
            "-D", str(self.local_port),  # SOCKS5 proxy
            "-L", f"{self.forward_port}:127.0.0.1:{self.forward_port}",  # Flask port forward
            "-N",
            f"{self.ssh_user}@{self.vps_host}"
        ]
        print(f"[+] Launching tunnel: {' '.join(cmd)}")
        self.proc = subprocess.Popen(cmd)
        print(f"[+] SOCKS5 proxy running on 127.0.0.1:{self.local_port}")
        print(f"[+] Flask dashboard available at http://127.0.0.1:{self.forward_port}/dashboard")

    def start(self):
        print("[+] VPN client started (killswitch active until tunnel is UP)")

        try:
            while True:
                if self.proc is None or self.proc.poll() is not None:
                    print("[X] Tunnel lost → killswitch engaged")
                    self.stop()
                    self.start_tunnel()
                    print("[+] Tunnel restored")
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        if self.proc:
            print("[+] Stopping tunnel...")
            self.proc.terminate()
            try:
                self.proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.proc.kill()
            self.proc = None
            print("[+] Tunnel closed (killswitch active).")


if __name__ == "__main__":
    vpn = VPNConnection(
        vps_host="your ip",
        ssh_user="root",
        ssh_key=r"your key",
        local_port=1080,   # proxy SOCKS5
        forward_port=5000  # dashboard Flask
    )
    vpn.start()

