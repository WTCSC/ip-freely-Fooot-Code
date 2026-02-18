import sys

digits = "0123456789"

def findMaskBinary(subnetMask):
    for i in range(32):
        if i < int(subnetMask):
            maskBinary += "1"
        else:
            maskBinary += "0"

        if (i + 1) % 8 == 0 and i != 31:
            maskBinary += "."
    
    return maskBinary

def toBinary(number: int):
    newNumber = number
    binaryValues = ""
    while newNumber > 0:
        remainder = newNumber % 2
        newNumber = newNumber // 2

        binaryValues += str(remainder)

    return binaryValues[::-1]

def findBinaryAddress(address):
    addressNumbers = address.split(".")

    binaryAddress = ""

    for number in addressNumbers:
        numberBinary = toBinary(int(number))
        



if __name__ == "__main__":
    ipaddr = sys.argv[1]

    address, subnetMask = ipaddr.split("/")
    maskBinary = findMaskBinary(subnetMask)





    
