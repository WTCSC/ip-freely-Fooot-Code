import argparse
import subprocess
import re
import sys
import socket
import time

digits = "0123456789"



def pingHost(ip):
    """
    Pings the provided host IP and returns the output of the ping
    
    :param ip: IPv4-formatted IP.
    """


    try:        
        result = subprocess.run(
            ["ping", "-c", "1", ip],
            capture_output=True,
            text=True,
            timeout=0.1
        )

        output = result.stdout.lower()

        # Successful ping
        if result.returncode == 0:
            match = re.search(r"time[=<]\s?(\d+)", output)
            if match:
                return "UP", f"{match.group(1)}ms"
            else:
                return "UP", "unknown"

        # No response
        if "unreachable" in output or "100% packet loss" in output:
            return "DOWN", "No response"

        return "ERROR", "Connection timeout"

    except subprocess.TimeoutExpired:
        return "ERROR", "Connection timeout"

def checkPort(ip, portUserInput):
    """
    Checks if a specific port is open on the provided IP address.
    
    :param ip: IPv4-formatted IP.
    :param port: Port number(s) to check.
    """
    # Parse the port input which can be a single port ("22"),
    # a comma-separated list ("22,80,443") or a range ("3000-3010").
    portOutputs = {}

    s = str(portUserInput).strip()
    try:
        if "-" in s:
            start_str, end_str = [p.strip() for p in s.split("-", 1)]
            start = int(start_str)
            end = int(end_str)
            if start < 1 or end > 65535 or start > end:
                return "ERROR: Invalid port range. Must be 1-65535 and start <= end."
            portOutputs = {port: "CLOSED" for port in range(start, end + 1)}

        elif "," in s:
            parts = [p.strip() for p in s.split(",") if p.strip()]
            ports = []
            for p in parts:
                pInt = int(p)
                if pInt < 1 or pInt > 65535:
                    return f"ERROR: Invalid port number {pInt}."
                ports.append(pInt)
            portOutputs = {int(port): "CLOSED" for port in ports}

        else:
            pInt = int(s)
            if pInt < 1 or pInt > 65535:
                return "ERROR: Invalid port number. Must be between 1 and 65535."
            portOutputs = {pInt: "CLOSED"}
    except ValueError:
        return "ERROR: Invalid port format. Use a single port, comma-separated list, or range (e.g. 22,80 or 3000-3010)."

    # Attempt to connect to each port (use integer ports). Return OPEN/CLOSED or an error string for a port.
    for port in list(portOutputs.keys()):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((ip, port))
            if result == 0:
                portOutputs[port] = "OPEN"
            else:
                portOutputs[port] = "CLOSED"
        except Exception as e:
            portOutputs[port] = f"ERROR: {e}"
        finally:
            try:
                sock.close()
            except Exception:
                pass

    return portOutputs

def findMaskBinary(subnetMask):
    """
    Finds the binary version of the subnet mask
    
    :param subnetMask: string of a CIDR formatted subnet mask (/24, /32, /16, etc.)
    """

    maskBinary = ""
    for i in range(32):
        if i < int(subnetMask):
            maskBinary += "1"
        else:
            maskBinary += "0"
    return maskBinary


def toBinary(number: int):
    """
    Converts an integer in Base-10 to Binary (base 2)
    
    :param number: Base-10 number to convert to binary
    :type number: int
    """

    newNumber = number
    binaryValues = ""
    while newNumber > 0:
        remainder = newNumber % 2
        newNumber = newNumber // 2
        binaryValues += str(remainder)

    return binaryValues[::-1].zfill(8)


def findBinaryAddress(address):
    """
    Converts the address into binary
    
    :param address: IPv4 address separated by periods (i.e. 10.103.0.63)
    """

    addressNumbers = address.split(".") # given with periods, so spits by them to get individual numbers
    binaryAddress = ""
    for number in addressNumbers:
        numberBinary = toBinary(int(number))
        binaryAddress += numberBinary
    return binaryAddress


def findNetworkAddress(binaryMask, binaryAddress):
    """
    Finds the network address using the binary AND operator
    
    :param binaryMask: String of the binary mask
    :param binaryAddress: String of the address in binary
    """

    buffer = ""
    for maskBit, addressBit in zip(binaryMask, binaryAddress):
        buffer += str(int(maskBit) & int(addressBit))
    return buffer


def binaryToBase10_32bit(binaryNumber):
    """
    Converts a binary number of 32 bits to an Base-10 integer.
    """

    parts = []
    for i in range(0, 32, 8):
        byte = binaryNumber[i:i+8]
        value = 0
        for j, bit in enumerate(byte):
            value += int(bit) * (2 ** (7 - j))
        parts.append(str(value))
    return ".".join(parts)


def binaryToInt(binaryNumber):
    """
    Converts a binary number to an integer
    """

    value = 0
    for i, bit in enumerate(binaryNumber):
        value += int(bit) * (2 ** (31 - i))
    return value


def intToBinary(number):
    """
    Converts a 32-bit integer to a 32-character binary string
    """
    bits = []
    for i in range(32):
        bit = (number >> (31 - i)) & 1
        bits.append(str(bit))
    return "".join(bits)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # Add a required positional argument
    parser.add_argument("ip", type=str, help="A required IP address argument")

    parser.add_argument("-p", "--port", type=str, default="80")
    
    args = parser.parse_args()


    address, subnetMask = args.ip.split("/")
    subnetMask = int(subnetMask)

    maskBinary = findMaskBinary(subnetMask)
    binaryAddress = findBinaryAddress(address)

    networkBinary = findNetworkAddress(maskBinary, binaryAddress)

    hostBits = 32 - subnetMask

    networkInt = binaryToInt(networkBinary)
    broadcastInt = networkInt + (2 ** hostBits - 1)

    broadcastBinary = intToBinary(broadcastInt)

    # Convert to dotted decimal
    base10NetworkAddress = binaryToBase10_32bit(networkBinary)
    base10BroadcastAddress = binaryToBase10_32bit(broadcastBinary)

    print("Network:", base10NetworkAddress)
    print("Broadcast:", base10BroadcastAddress)
    
    
    if subnetMask == 32:
        print("Single host only.")
    else:
        print("You will see the status of each host in the network range, as well as the status of the specified port(s) if the host is up.")
        print("At the end, you can ask for more structured data to see the results in a more organized way.")
        time.sleep(5)

        activeHosts = []

        for host in range(networkInt + 1, broadcastInt):
            # Get host response
            hostBinary = intToBinary(host)
            hostToPing = binaryToBase10_32bit(hostBinary)
            pingResponse = pingHost(hostToPing)

            # Prints the host response
            portResponse = "N/A"
            print(f"HOST: {hostToPing} | STATUS: {pingResponse[0]} | RESPONSE TIME: {pingResponse[1]}")
            

            # If the host is up, check the port(s) status
            if pingResponse[0] == "UP":
                portResponse = checkPort(hostToPing, args.port)
                for port, status in portResponse.items():
                    print(f" - PORT {port} STATUS: {status}")
            activeHosts.append((hostToPing, pingResponse[0], pingResponse[1], portResponse))
            

        print("Scan complete.")
        print("Would you like to the hosts that were up? (y/n)")
        userInput = input().lower()
        if userInput == "y":
            print("Here are the hosts that were up:")
            for host in activeHosts:
                if host[1] == "UP":
                    print(f"HOST: {host[0]} | STATUS: {host[1]} | RESPONSE TIME: {host[2]}")
                    for port, status in host[3].items():
                        print(f" - PORT {port} STATUS: {status}")
