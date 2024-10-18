import json
from itertools import cycle

#Define globals
global INT, SHORT, BYTE
INT = 8
SHORT = 4
BYTE = 2

def le_hex_to_int(int_hex):
    '''
    Reads a big endian hex, transforms it in little endian and then converts it to int.
    Returns int, hex 
    '''
    hex_array = bytearray.fromhex(int_hex)
    hex_array.reverse()
    hex_array = ''.join(f"{n:02x}" for n in hex_array)
    return int(hex_array, 16), hex_array

def search_value(value, key, list):
    '''Searches value for key in a list of dictionaries'''
    return [item for item in list if item[key] == value]

def prettyDict(dict):
    return json.dumps(dict, indent=4, default=str)

def yap(text = "", debug_state = False):
    if debug_state:
        print(text)
    else:
        print(text)

def yurisPrint(script):
    format = ""
    for instruction in script:
        match instruction['type']:
            case "label":
                format += "\n"
                format += f"# {instruction['value']}"
            case "instruction":
                format += f"\\ {instruction['opcode']}"
                for attribute in instruction['attributes']:
                    if len(attribute['attrib_values']) > 0:
                        try:
                            format += f" [{attribute['argument']} ="
                        except KeyError:
                            format += f" ["
                        for i,value in enumerate(attribute['attrib_values']):
                            if i == len(attribute['attrib_values'])-1:
                                format += f" {value}"
                            else:
                                format += f" {value},"
                        format += "]"
            case _:
                print("What the fuck dude HOW")
        format += "\n"
    return format

def rolling_xor(cryptedstring, key):
    '''Unpacks the single hex digits, XOR them together, packs them and then returns the xor-decrypted string'''
    return ''.join(f"{(int(c, 16)^int(k, 16)):x}" for c,k in zip(cryptedstring, cycle(key)))