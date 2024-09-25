import base64
import os

# Define the fixed text for the initial configuration
fixed_text = """#profile-title: base64:8J+MgCDwnZeU8J2XlfCdl6LwnZet8J2XmPCdl5zwnZeXIPCfjIA=
#profile-update-interval: 1
#subscription-userinfo: upload=0; download=0; total=10737418240000000; expire=2546249531
"""

# Function to ensure the necessary directories exist
def ensure_directories_exist():
    output_folder = os.path.abspath(os.path.join(os.getcwd()))
    base64_folder = os.path.join(output_folder, "Base64")

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    if not os.path.exists(base64_folder):
        os.makedirs(base64_folder)

    return output_folder, base64_folder

def create_subscription(subscription_data):
    output_folder, base64_folder = ensure_directories_exist()  # Ensure directories are created

    # Define your subscription links here if needed
    # subscription_data = [
    #     "Sample subscription data 1",
    #     "Sample subscription data 2",
    #     # Add more subscription data as needed
    # ]

    # Create the subscription file
    subscription_filename = os.path.join(output_folder, "All_Configs_Sub.txt")
    with open(subscription_filename, "w") as f:
        f.write(fixed_text)
        for config in subscription_data:
            f.write(config + "\n")

    # Read the subscription file and encode it in Base64
    with open(subscription_filename, "r") as input_file:
        config_data = input_file.read()

    # Encrypt data using Base64
    encoded_config = base64.b64encode(config_data.encode()).decode()
    
    # Save the Base64 encoded data to a new file
    base64_filename = os.path.join(base64_folder, "All_Configs_base64_Sub.txt")
    with open(base64_filename, "w") as output_file:
        output_file.write(encoded_config)

