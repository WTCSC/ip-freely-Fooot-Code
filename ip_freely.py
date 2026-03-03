import subprocess
import re
import sys

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
            timeout=3
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
    ipaddr = sys.argv[1]

    address, subnetMask = ipaddr.split("/")
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
        for host in range(networkInt + 1, broadcastInt):
            hostBinary = intToBinary(host)
            hostToPing = binaryToBase10_32bit(hostBinary)
            pingResponse = pingHost(hostToPing)
            print(f"HOST: {hostToPing} | STATUS: {pingResponse[0]} | RESPONSE TIME: {pingResponse[1]}")
