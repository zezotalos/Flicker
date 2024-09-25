import json
import subprocess
import requests
import os
import time

class V2RayClient:
    def __init__(self, server_address, server_port, protocol, password, config_path):
        self.server_address = server_address
        self.server_port = server_port
        self.protocol = protocol
        self.password = password
        self.config_path = config_path
        self.process = None
    
    def generate_config(self):
        """Generates the V2Ray configuration.""" # TROJAN TYPE
        config = {
            "inbounds": [{
                "port": 1080,  # Local port for SOCKS5 proxy
                "listen": "127.0.0.1",  # Listen on localhost
                "protocol": "socks",
                "settings": {
                    "udp": True
                }
            }],
            "outbounds": [{
                "protocol": self.protocol,
                "settings": {
                    "servers": [
                        {
                            "address": self.server_address,
                            "port": self.server_port,
                            "password": self.password,
                            "level": 8
                        }
                    ]
                },
                "streamSettings": {
                    "security": "tls",
                    "tlsSettings": {
                        "allowInsecure": True,
                        "serverName": self.server_address
                    }
                }
            }],
            "log": {
                "loglevel": "warning"
            }
        }
        return config
    
    def save_config(self):
        """Saves the generated configuration to a JSON file."""
        config = self.generate_config()
        with open(self.config_path, "w") as f:
            json.dump(config, f, indent=4)
    
    def start(self):
        """Starts the V2Ray client as a subprocess."""
        try:
            self.process = subprocess.Popen(
                [os.path.join(os.getcwd() , "client" , "v2ray"), "run", self.config_path],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            time.sleep(5)
            return self.process
        except FileNotFoundError:
            print("Error: v2ray executable not found. Make sure it's installed and in your PATH.")
            return None
    
    def stop(self):
        """Stops the V2Ray client process."""
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.process = None
    
    def test_connection(self, request_count=5):
        """Makes test requests to check V2Ray server."""
        success_count = 0
        proxies = {
            "http": "socks5h://127.0.0.1:1080",
            "https": "socks5h://127.0.0.1:1080",
        }
        
        for i in range(request_count):
            try:
                response = requests.get("http://connectivitycheck.gstatic.com/generate_204", proxies=proxies, timeout=10)
                response.raise_for_status()
                print(f"Request {i + 1}/{request_count} successful! Status code: {response.status_code}")
                success_count += 1
            except requests.exceptions.RequestException as e:
                print(f"Request {i + 1}/{request_count} failed: {e}")
        
        print(f"{success_count}/{request_count} requests were successful.")
        return success_count == request_count or success_count > 1

