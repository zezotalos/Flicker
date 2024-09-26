import requests
import json
import re
import secrets
import string
import html
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

class SSHS8:
    def __init__(self, server_url):
        self.cookies = {}
        self.server_url = server_url
        self.server_id = int(self.server_url.split("/")[-1])
        self.initial_data = {}
        self.headers = self._get_default_headers()

    def _get_default_headers(self):
        """Returns the default headers for requests."""
        return {
            'accept': 'text/html, application/xhtml+xml',
            'accept-language': 'en-US,en;q=0.5',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'origin': 'https://vpneurope.sshs8.com',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': self.server_url,
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
            'x-csrf-token': '',
            'x-livewire': 'true',
            'x-socket-id': 'undefined',
        }

    def get_initial_data(self):
        """Fetches the initial data and CSRF token from the server."""
        response = requests.get(self.server_url, headers=self.headers)
        self.cookies = response.cookies.get_dict()

        initial_data_match = re.search(r'wire:initial-data="([^"]+)"', response.text)
        csrf_token_match = re.search(r'<meta name="csrf-token" content="([^"]+)"', response.text)

        if initial_data_match and csrf_token_match:
            initial_data = html.unescape(initial_data_match.group(1))
            self.initial_data = json.loads(initial_data)
            self.headers['x-csrf-token'] = csrf_token_match.group(1)
            return True
        return False

    def create_account(self, sni='' , title=''):
        """Handles the account creation process."""
        if not self.get_initial_data():
            print("Error: Initial data or CSRF token not found.")
            return None

        self.password = self.generate_password()
        json_data = self._build_account_data()

        # Step 1: Sync password input
        response = self._post_account_data(json_data)

        if not response:
            return None

        # Step 2: Submit account creation request
        json_data = self._update_json_data(response, self.password)
        final_response = self._post_account_data(json_data)

        if final_response:
            return self._process_account_creation_response(final_response , sni , title)
        return None

    def _build_account_data(self):
        """Builds the initial data structure for account creation."""
        return {
            'id': self.initial_data['id'],
            'data': {
                'username': self.initial_data['data']['username'],
                'password': None,
                'is_create': None,
                'server_id': self.server_id,
                'data': None,
                'settings': None,
                'title': 'Create account',
                'captcha': 0,
            },
            'name': 'create-account',
            'checksum': self.initial_data['checksum'],
            'locale': 'en',
            'children': [],
            'actionQueue': [{"type": "syncInput", "payload": {"name": "password", "value": self.password}}],
        }

    def _post_account_data(self, json_data):
        """Posts account data to the server."""
        response = requests.post(
            'https://vpneurope.sshs8.com/livewire/message/create-account',
            cookies=self.cookies,
            headers=self.headers,
            json=json_data,
        )
        if response.status_code == 200:
            self.cookies = response.cookies.get_dict()
            return response.json()
        else:
            print(f"Error: Failed to post account data (status {response.status_code})")
            return None

    def _update_json_data(self, response, password):
        """Updates the account creation JSON data after receiving server response."""
        json_data = {
            'id': self.initial_data['id'],
            'data': {
                'username': response['data']['username'],
                'password': password,
                'is_create': None,
                'server_id': self.server_id,
                'data': None,
                'settings': None,
                'title': 'Create account',
                'captcha': 0,
            },
            'name': 'create-account',
            'checksum': response['checksum'],
            'locale': 'en',
            'children': [],
            'actionQueue': [{"type": "callMethod", "payload": {"method": "submit", "params": []}}],
        }
        return json_data

    def _process_account_creation_response(self, final_response , sni , title):
        """Extracts and processes the account configuration information."""
        account_data = final_response.get('dom')
        initial_data_match = re.search(r'wire:initial-data="([^"]+)"', account_data)
        
        if initial_data_match:
            v2ray_account = html.unescape(initial_data_match.group(1))
            parsed_data = json.loads(v2ray_account)
            config_info = parsed_data['data']['data']['line']
            config_dict = self._parse_config_info(config_info)

            modified_url = self._modify_config_url(config_dict , sni , title)
            # print("Modified Config URL:")
            # print(modified_url)

            return {"config_url": modified_url, "config_info": config_dict}
        return None

    def _modify_config_url(self, config_dict , sni , title):
        """Modifies and rebuilds the configuration URL with new query parameters."""
        TYPE = "VLESS"

        parsed_url = urlparse(config_dict.get('Link TLS') or config_dict.get('Link TR'))
        query_params = parse_qs(parsed_url.query)
        query_params['sni'] = [sni]
        if config_dict.get('Link TR'):
            query_params['allowInsecure'] = ['true']
            TYPE = "TROJAN"

        new_query = urlencode(query_params, doseq=True)
        new_url = urlunparse(parsed_url._replace(
            query=new_query,
            # fragment=f"(___ABOZEID___) ({TYPE} 🇩🇪) Expires ⚠ ({config_dict['Expired']})", 
            fragment=f"𝔸𝔹𝕆ℤ𝔼𝕀𝔻 ({self._to_bold_sans_serif(title or '')} | {self._to_bold_sans_serif(config_dict['Expired'])} 🇩🇪)", 
            netloc=f"{config_dict.get('User ID') or config_dict.get('Key')}@{config_dict['IP/Host']}:{config_dict.get('Port TLS') or config_dict.get('Port')}"
        ))
        return new_url

    @staticmethod
    def generate_password(length=12):
        """Generates a secure random password."""
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(secrets.choice(characters) for _ in range(length))

    @staticmethod
    def _parse_config_info(config_data):
        """Parses the configuration information into a dictionary."""
        config_dict = {}
        for line in config_data.splitlines():
            if ">=" in line:
                key, value = line.split(">=", 1)
                config_dict[key.strip()] = value.strip()
        return config_dict


    @staticmethod
    def _to_bold_sans_serif(text):
        bold_sans_serif_map = {
            'A': '𝗔', 'B': '𝗕', 'C': '𝗖', 'D': '𝗗', 'E': '𝗘', 'F': '𝗙', 'G': '𝗚',
            'H': '𝗛', 'I': '𝗜', 'J': '𝗝', 'K': '𝗞', 'L': '𝗟', 'M': '𝗠', 'N': '𝗡',
            'O': '𝗢', 'P': '𝗣', 'Q': '𝗤', 'R': '𝗥', 'S': '𝗦', 'T': '𝗧', 'U': '𝗨',
            'V': '𝗩', 'W': '𝗪', 'X': '𝗫', 'Y': '𝗬', 'Z': '𝗭',
            'a': '𝗮', 'b': '𝗯', 'c': '𝗰', 'd': '𝗱', 'e': '𝗲', 'f': '𝗳', 'g': '𝗴',
            'h': '𝗵', 'i': '𝗶', 'j': '𝗷', 'k': '𝗸', 'l': '𝗹', 'm': '𝗺', 'n': '𝗻',
            'o': '𝗼', 'p': '𝗽', 'q': '𝗾', 'r': '𝗿', 's': '𝘀', 't': '𝘁', 'u': '𝘂',
            'v': '𝘃', 'w': '𝘄', 'x': '𝘅', 'y': '𝘆', 'z': '𝘇',
            '0': '𝟬', '1': '𝟭', '2': '𝟮', '3': '𝟯', '4': '𝟰', '5': '𝟱', '6': '𝟲',
            '7': '𝟳', '8': '𝟴', '9': '𝟵'
        }

        # Convert each character in the input text
        return ''.join(bold_sans_serif_map.get(char, char) for char in text)
