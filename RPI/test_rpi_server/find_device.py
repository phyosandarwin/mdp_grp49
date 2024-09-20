import subprocess
import re
def get_master_ip():
    # Run the 'arp -a' command and capture the output
    arp_output = subprocess.check_output(['arp', '-a']).decode()
    print('FINDING master device(find_device.py)')
    # Search for the line containing 'RCZ'
    master = None
    for line in arp_output.splitlines():
        if 'RCZ' in line:
            print('master device found(find_device.py)')
            master = line
            break

    # Extract the IP address from the line
    if master:
        ip_match = re.search(r'\((.*?)\)', master)
        if ip_match:
            return ip_match.group(1)
    
    return None

# # Get and print the RCZ IP address
# if rcz_ip:
#     print(f"RCZ IP address: {rcz_ip}")
# else:
#     print("RCZ device not found.")
