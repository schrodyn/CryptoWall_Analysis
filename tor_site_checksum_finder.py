import pefile
import string
import random
import time


def GetTorBytes(filename, offset, size):
    pe = pefile.PE(filename)
    enc_arr = []

    print("[!] Searching PE sections for .data")
    for section in pe.sections:
        if b".data" in section.Name:
            start = offset
            end = start + size
            for byte in section.get_data()[start:end]:
                enc_arr.append(byte)
    return enc_arr


def GenerateOnionString():
    random_str = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(14)])
    return random_str


def ConvertToLowerCase(char):
    if char >= ord('A') and char <= ord('Z'):
        char += 32
    return char


def ConvertArrayBytesToDWORD(arr):
    val = '0x' + ''.join([format(int(hex(c), 16), '02X') for c in reversed(arr)])
    return int(val, 16)


def CompressTORRoute(bytes_array, site):
    ret_value = 0xFFFFFFFF
    siteLen = len(site)
    for i in range(siteLen):
        size_left = siteLen - 1
        if size_left == 0:
            break
        tmp = (ConvertToLowerCase(ord(site[i])) ^ (ret_value & 0xffffff)) & 0xff
        ret_value = ConvertArrayBytesToDWORD(bytes_array[tmp*4:(tmp*4)+4]) ^ (ret_value >> 8)
    return hex(~ret_value & 0xFFFFFFFF)


def main():
    bytes_array = GetTorBytes("cryptowall_055A0000.bin", 0x188, 0x587-0x188)
    # this address is from old cryptowall variants, looking at subroutine_004074A0,
    # 0xc7700797 was generated from this onion route
    assert(CompressTORRoute(bytes_array, "1pai7ycr7jxqkilp.onion") == '0xc7700797')
    print("[+] Assertion Passed.\nAttempting to brute-force checksum...")
    time.sleep(3)

    while True:
        onion_route = "1%s.onion" % GenerateOnionString()
        route_value = CompressTORRoute(bytes_array, onion_route)
        # this cmp of checksums can be found at .text:00404FBF
        if route_value == '0x63680E35' or route_value == '0x30BBB749':
            print("[+] Found Onion Route: checksum:%s => site:%s" % (route_value, onion_route))
            break
        else:
            print("[-] Attempt Failed: %s" % route_value)


if __name__ == '__main__':
    main()