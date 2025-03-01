from v2ray import V2RayClient
from sshs8 import SSHS8
import json
import time
import os
from subscription import create_subscription

current_folder = os.getcwd()
configs_path = os.path.join(current_folder , "configs" , 'configs.txt')
# 🇫🇷

# Define a mapping from country names to country codes
country_code_map = {
    "Hungary": "HU",
    "Romania": "RO",
    "Moldova": "MD",
    "Poland": "PL",
    "Kazakhstan": "KZ",
    "United Arab Emirates": "AE",
    "United Kingdom": "UK",
    "France": "FR",
    "Germany": "DE"
}


def retry_create_account(v2ray_agent, country_code , retries=3, delay=5):
    """Retries account creation with the specified number of retries and delay between attempts."""
    attempt = 0
    while attempt < retries:
        account = v2ray_agent.create_account(country_code=country_code)
        if account is not None or account.get("IP/Host") != '':
            return account
        else:
            attempt += 1
            print(f"Attempt {attempt} failed. Retrying in {delay} seconds...")
            time.sleep(delay)  # Wait before retrying
    print("All retry attempts failed.")
    return None  # Return None if all attempts fail

def create_servers(ids=None , country_codes=None):
    
        # Example data, assuming this is where the server data comes from
    server_data = [
        {
            "server_id": "52",
            "country": "Hungary",        
            },
        {
            "server_id": "44",
            "country": "Romania",
        },
        {
            "server_id": "12",
            "country": "Moldova",
        },
        {
            "server_id": "60",
            "country": "Poland",
        },
        {
            "server_id": "68",
            "country": "Kazakhstan",
        },
        {
            "server_id": "36",
            "country": "United Arab Emirates",
        },
        {
            "server_id": "28",
            "country": "United Arab Emirates"
        },
        {
            "server_id": "20",
            "country": "United Kingdom",
        },
        # {
        #     "server_id": "116",
        #     "country": "France",
        # },
        # {
        #     "server_id": "124",
        #     "country": "Germany",
        # }
        # },
        {
            "server_id": "100",
            "country": "Germany",
        }
    ]

    if country_codes:
        if not isinstance(country_codes, list):
            country_codes = [country_codes]  # Wrap the single country_code in a list
        
        countries = []
        for country, code in country_code_map.items():
            if code in country_codes:
                countries.append(country)
        
        selected_servers = selected_servers = [server for server in server_data if server['country'] in countries]
        
    elif ids:
        if not isinstance(ids, list):
            ids = [ids]  # Wrap the single ID in a list
        
        # Filter the servers by ids
        selected_servers = [server for server in server_data if int(server['server_id']) in ids]
            
    servers = []

    # Create the result dictionary with country codes as keys
    
    for server in selected_servers:
        
        country = server['country']
        country_code = country_code_map.get(country, "Unknown")  # Default to "Unknown" if country is not in the map
    
        result = {}
        V2RAY_AGENT = SSHS8(f"https://vpneurope.sshs8.com/accounts/TROJAN/{server['server_id']}")  # UK SERVER AS TEST
        
        account = retry_create_account(V2RAY_AGENT, country_code=country_code, retries=5, delay=5)
        
        if account is None:
            print(f"Failed to create an account for server {server['server_id']}. Skipping this server.")
            continue  # Skip this server if account creation failed
        

        result[country_code] = account['config_info']  # Store the server info with the country code as the key
        servers.append(result)
    
    return servers



def check_v2ray_server(server):

    V2RAY_SERVER_ADDRESS = server['IP/Host']
    V2RAY_SERVER_PORT = int(server['Port'])
    PROTOCOL = "trojan"
    TROJAN_PASSWORD = server['Key']
    V2RAY_CONFIG_PATH = "config.json"

    # Create V2RayClient instance
    client = V2RayClient(V2RAY_SERVER_ADDRESS, V2RAY_SERVER_PORT, PROTOCOL, TROJAN_PASSWORD, V2RAY_CONFIG_PATH)

    # Save configuration to file
    client.save_config()

    # Start V2Ray
    v2ray_process = client.start()

    if v2ray_process:
        # Test the connection
        test_result = client.test_connection()

        # Stop the V2Ray process
        client.stop()

        if test_result:
            # print("V2Ray server is working correctly!")
            client.delete_config()
            return True
        else:
            # print("V2Ray server connection test failed.")
            client.delete_config()
            return False



def process_server(server, country, delay=5 ,max_retries=3):
    """
    Tests the server connection. If it fails, retry creating a new server and testing it.
    Returns the working server or None if no working server found after max retries.
    """
    # print(f"Testing server for {country}: {server}")
    print(f"Testing server for {country}")
    
    # Test the current server connection
    if check_v2ray_server(server):
        print(f"Server for {country} is working.")
        return server

    # If the server is down, try creating a new one with retries
    print(f"Server for {country} is down, attempting to create new servers...")

    for attempt in range(max_retries):
        print(f"Retry {attempt + 1} of {max_retries} for {country}")
        time.sleep(delay)

        # Try creating a new server
        new_server_data = create_servers(country_codes=[country])
        
        # ADD SUPPORT FOR MULTI SERVERS IN THE FUTURE
        new_server = list(new_server_data[0].values())[0]
        
        # Test the newly created server
        if check_v2ray_server(new_server):
            print(f"New server for {country} is working.")
            return new_server
        else:
            print(f"New server for {country} is down.")
    
    # After max retries, return None if no server is working
    print(f"Failed to find a working server for {country} after {max_retries} retries.")
    return None

if __name__ == "__main__":
    Working_List = []
    subscription_list = []

    if not os.path.exists(configs_path):
        
        servers = create_servers(country_codes=["DE"])

        # TEST ALL SERVER BEFORE Putting IT IN THE SUB FILE 
        # Configuration parameters
        for server in servers:
            
            country = list(server.keys())[0]
            server = list(server.values())[0]

            V2RAY_SERVER_ADDRESS = server['IP/Host']
            V2RAY_SERVER_PORT = int(server['Port'])
            PROTOCOL = "trojan"
            TROJAN_PASSWORD = server['Key']
            V2RAY_CONFIG_PATH = "config.json"

            # Create V2RayClient instance
            client = V2RayClient(V2RAY_SERVER_ADDRESS, V2RAY_SERVER_PORT, PROTOCOL, TROJAN_PASSWORD, V2RAY_CONFIG_PATH)

            # Save configuration to file
            client.save_config()

            # Start V2Ray
            v2ray_process = client.start()

            if v2ray_process:
                # Test the connection
                test_result = client.test_connection()

                # Stop the V2Ray process
                client.stop()

                if test_result:
                    print("V2Ray server is working correctly!")
                    Working_List.append({
                        country: server
                    })
                else:
                    print("V2Ray server connection test failed.")
        
     
        for config in Working_List:
            country_code = list(config.keys())[0]
            server = list(config.values())[0]
            subscription_list.append(
                SSHS8._modify_config_url(SSHS8 , country_code=country_code, config_dict=server , sni="www.ekb.eg" , title="WE LIMIT"))
            subscription_list.append(
                SSHS8._modify_config_url(SSHS8, country_code=country_code ,config_dict=server , sni="ea.com" , title="WE PS"))

        create_subscription(subscription_list)
        
        with open(configs_path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(Working_List))
    
    
    else:
        with open(configs_path, 'r', encoding='utf-8') as f:
            SERVERS = json.loads(f.read())

        for server_info in SERVERS:
            country = list(server_info.keys())[0]
            server = list(server_info.values())[0]

            # Process the server, either returning a working one or None, with retries
            working_server = process_server(server, country, delay=5 , max_retries=10)

            if working_server:
                # Append working server to the list
                Working_List.append({country: working_server})

        # create a subFile
        subscription_list = [
            
        ]

        for config in Working_List:
            country_code = list(config.keys())[0]
            server = list(config.values())[0]
            
            subscription_list.append(
                SSHS8._modify_config_url(SSHS8, country_code=country_code,
                                        config_dict=server,
                                        sni="www.ekb.eg",
                                        title="WE LIMIT"))
            
            subscription_list.append(
                SSHS8._modify_config_url(SSHS8, country_code=country_code,
                                        config_dict=server,
                                        sni="ea.com", 
                                        title="WE PS"))

        create_subscription(subscription_list)
        
        with open(configs_path, 'w', encoding='utf-8') as f:
                f.write(json.dumps(Working_List))
