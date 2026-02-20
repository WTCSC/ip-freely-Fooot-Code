import sys

digits = "0123456789"

def findMaskBinary(subnetMask):
    maskBinary = ""
    for i in range(32):
        if i < int(subnetMask):
            maskBinary += "1"
        else:
            maskBinary += "0"

        # if (i + 1) % 8 == 0 and i != 31:
        #     maskBinary += "."
    
    return maskBinary

def toBinary(number: int):
    newNumber = number
    binaryValues = ""
    while newNumber > 0:
        remainder = newNumber % 2
        newNumber = newNumber // 2

        binaryValues += str(remainder)

    return binaryValues[::-1].zfill(8)

def findBinaryAddress(address):
    addressNumbers = address.split(".")

    binaryAddress = ""

    for number in addressNumbers:
        numberBinary = toBinary(int(number))
        binaryAddress += numberBinary

    return binaryAddress
        
def findNetworkAddress(binaryMask, binaryAddress):
    buffer = ""
    for i, (maskBit, addressBit) in enumerate(zip(binaryMask, binaryAddress)):
        buffer += str(int(maskBit) & int(addressBit))

        if (i + 1) % 8 == 0 and i != 31:
            buffer += "."
    return buffer

def binaryToBase10(binaryNumber):
    binaryNumbers = binaryNumber.split(".")
    
    base10Number = ""
    
    for i, number in enumerate(binaryNumbers):
        print(number)
        actualNumber = 0
        for i, digit in enumerate(number):
            actualNumber += int(digit) * 2**(len(number)-i-1)

        base10Number += f"{int(actualNumber)}."

    return base10Number[:-1]
            
        



if __name__ == "__main__":
    ipaddr = sys.argv[1]

    address, subnetMask = ipaddr.split("/")
    maskBinary = findMaskBinary(subnetMask)
    
    binaryAddress = findBinaryAddress(address)

    networkAddress = findNetworkAddress(maskBinary, binaryAddress)

    hostBits = 32 - int(subnetMask) 
    print(networkAddress, hostBits)

    if hostBits == 0: # subnet mask CIDR is 32
        onlyNetworkBits = networkAddress
        onlyHostBits = ""
    else:
        onlyHostBits = networkAddress[-hostBits:]
        onlyNetworkBits = networkAddress[:-hostBits]    
    
    broadcastAddress = onlyHostBits.replace("0", "1")
    broadcastAddress = onlyNetworkBits + broadcastAddress

    base10BroadcastAddress = binaryToBase10(broadcastAddress)
    base10NetworkAddress = binaryToBase10(networkAddress)

    lowRange = int(base10NetworkAddress.split(".")[-1]) + 1
    lowRange = "".join()

    print(lowRange, base10BroadcastAddress)





    
