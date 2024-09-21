import os
# import re
import codecs
import struct
from func import *

# TODO remove
# def read_extract_yst_list_old(folder_path):
#     yst_list_path = os.path.join(folder_path, "yst_list.ybn")
#     if not os.path.exists(yst_list_path):
#         # We didn't find the file
#         return 1
    
#     # Open yst_list in Shift-JIS
#     with open(yst_list_path, 'r', encoding='cp932', errors='ignore') as f:
#         yst_list = f.read()

#     yst_paths = re.findall(r'(?:data)(?:.*?)(?:\.yst|\.txt)', yst_list)

#     return yst_paths

def readExtractYstlist_new(folder_path):
    
    DEBUG = True

    yst_list_path = os.path.join(folder_path, "yst_list.ybn")
    if not os.path.exists(yst_list_path):
        # We didn't find the file
        return 1
    
    with open(yst_list_path, 'rb') as f:
        yst_hex = memoryview(f.read())
    yap(f"Decoding {yst_list_path}:", DEBUG)

    # Header = 4s
    # Version = i
    # NumScripts = i
    header_fmt = "<4s2i"

    header_hex = yst_hex[:struct.calcsize(header_fmt)]
    header_unpack = struct.unpack(header_fmt, header_hex)
    header_dict = {
        'header' : header_unpack[0],
        'version' : header_unpack[1],
        'num_scripts' : header_unpack[2],
        'scripts' : []
    }
    
    script_hex = yst_hex[struct.calcsize(header_fmt):]
    script_cur = 0
    for script_num in range(header_dict['num_scripts']):

        # Index = i
        # PathLength = i
        # Path = PathLength s
        # ModificationTime = q
        # NumVariables = i
        # NumLabels = i
        # NumTexts = i  #TODO Only on Euphoria, add detection
        script_fmt = "<2i"

        script_unpack = struct.unpack(script_fmt, script_hex[script_cur:struct.calcsize(script_fmt)+script_cur])
        script_dict = {
            'index' : script_unpack[0],
            'path_length' : script_unpack[1],
        }
        script_fmt = f"<2i{script_dict['path_length']}sq2i"
        script_unpack = struct.unpack(script_fmt, script_hex[script_cur:struct.calcsize(script_fmt)+script_cur])
        script_dict.update({
            'path' : codecs.decode(script_unpack[2].hex(), 'hex').decode('cp932'),
            'num_variables' : script_unpack[4],
            'num_labels' : script_unpack[5]
        })
        script_cur += struct.calcsize(script_fmt)
        header_dict['scripts'].append(script_dict)
        print(header_dict['scripts'][-1]['path'])

def read_extract_ystlist(folder_path):
    '''Returns {magic,version,numscripts,[{index,pathlength,path,variables,labels},{...}]}'''

    DEBUG = True

    yst_list_path = os.path.join(folder_path, "yst_list.ybn")
    if not os.path.exists(yst_list_path):
        # We didn't find the file
        return 1
    
    decode = {}

    with open(yst_list_path, 'rb') as f:
        ystHex = f.read().hex()
    yap(f"Decoding {yst_list_path}:", DEBUG)

    # Setup a cursor that we keep increasing as we read the file
    cur = 0
    
    magic = ystHex[cur:cur+INT]
    yap(f"Magic: {codecs.decode(magic, 'hex').decode('cp932')}", DEBUG)
    decode['magic'] = codecs.decode(magic, 'hex').decode('cp932')
    cur += INT

    version = le_hex_to_int(ystHex[cur:cur+INT])[0]
    yap(f"Version: {version}", DEBUG)
    decode['version'] = version
    cur += INT

    numscripts = le_hex_to_int(ystHex[cur:cur+INT])[0]
    yap(f"Scripts: {numscripts}", DEBUG)
    decode['numscripts'] = numscripts
    cur += INT

    scripts = []

    while(cur < len(ystHex)):
        yap("", DEBUG)
        scripts.append({})

        index = le_hex_to_int(ystHex[cur:cur+INT])
        yap(f"    Index: {index}", DEBUG)
        scripts[-1]['index'] = index
        cur += INT

        pathlength = le_hex_to_int(ystHex[cur:cur+INT])
        yap(f"    PathLength: {pathlength}", DEBUG)
        scripts[-1]['pathlength'] = pathlength
        cur += INT

        path = ystHex[cur:cur+pathlength[0]*2]
        print(path)
        yap(f"    Path: {codecs.decode(path, 'hex').decode('cp932')}", DEBUG)
        scripts[-1]['path'] = codecs.decode(path, 'hex').decode('cp932')
        cur += pathlength[0]*2

        #TOFIX if needed, who cares about file creation date lol get rekt
        modtime = le_hex_to_int(ystHex[cur:cur+16])
        print(ystHex[cur:cur+16])
        print(f"    CreationTime: {modtime}")
        scripts[-1]['modtime'] = modtime
        cur += INT*2

        variables = le_hex_to_int(ystHex[cur:cur+INT])
        print(ystHex[cur:cur+INT])
        yap(f"    Variables: {variables}", DEBUG)
        scripts[-1]['variables'] = variables
        cur += INT

        # This int contains the number of labels in the demo but in euphoria the number of text is stored here
        # + another int for the label for whatever fucking reason
        labels = le_hex_to_int(ystHex[cur:cur+INT])
        print(ystHex[cur:cur+INT])
        yap(f"    Labels: {labels}", DEBUG)
        scripts[-1]['labels'] = labels
        cur += INT

        # numtex, numtex_hex = le_hex_to_int(ystHex[cur:cur+8])
        # print(f"    NUMTE:{numtex_hex} -> {numtex}")
        # cur += 8
    decode['scripts'] = scripts
    return decode

def read_extract_ysl(folder_path):
    '''Returns {magic,version,numlabels,[{namelength,name,id,offset,scriptindex},{...}]}'''

    DEBUG = False

    ysl_path = os.path.join(folder_path, "ysl.ybn")
    if not os.path.exists(ysl_path):
        # We didn't find the file
        return 1
    
    decode = {}
    
    with open(ysl_path, 'rb') as f:
        ystHex = f.read().hex()
    yap(f"Decoding {ysl_path}:", DEBUG)

    # Setup a cursor that we keep increasing as we read the file
    cur = 0
    
    magic = ystHex[cur:cur+INT]
    yap(f"Magic: {codecs.decode(magic, 'hex').decode('cp932')}", DEBUG)
    decode['magic'] = codecs.decode(magic, 'hex').decode('cp932')
    cur += INT

    version = le_hex_to_int(ystHex[cur:cur+INT])[0]
    yap(f"Version: {version}", DEBUG)
    decode['version'] = version
    cur += INT

    numlabels = le_hex_to_int(ystHex[cur:cur+INT])[0]
    yap(f"Labels: {numlabels}", DEBUG)
    decode['numlabels'] = numlabels
    cur += INT

    # Ignore labelRangeStartIndexes for now dunno how it works hope i dont need it
    cur += 2048

    labels = []

    while(cur < len(ystHex)):
        yap("", DEBUG)
        labels.append({})

        namelength = int(ystHex[cur:cur+BYTE], 16)
        yap(f"    NameLength: {namelength}", DEBUG)
        labels[-1]['namelength'] = namelength
        cur += BYTE

        path = ystHex[cur:cur+namelength*2]
        yap(f"    Name: {codecs.decode(path, 'hex').decode('cp932')}", DEBUG)
        labels[-1]['name'] = codecs.decode(path, 'hex').decode('cp932')
        cur += namelength*2

        id = le_hex_to_int(ystHex[cur:cur+INT])[0]
        yap(f"    ID: {id}", DEBUG)
        labels[-1]['id'] = id
        cur += INT

        offset = le_hex_to_int(ystHex[cur:cur+INT])[0]
        yap(f"    Offset: {offset}", DEBUG)
        labels[-1]['offset'] = offset
        cur += INT

        scriptindex = le_hex_to_int(ystHex[cur:cur+SHORT])[0]
        yap(f"    ScriptIndex: {scriptindex}", DEBUG)
        labels[-1]['scriptindex'] = scriptindex
        cur += SHORT

        # Ignore padding byte
        cur += BYTE*2
    
    decode['labels'] = labels
    return decode

def read_extract_yst(folder_path):
    '''Returns {magic,version,numlabels,[{namelength,name,id,offset,scriptindex},{...}]}'''

    DEBUG = True

    ysl_path = folder_path
    if not os.path.exists(ysl_path):
        # We didn't find the file
        return 1
    
    decode = {}
    
    with open(ysl_path, 'rb') as f:
        ystHex = f.read().hex()
    yap(f"Decoding {ysl_path}:", DEBUG)

    # Setup a cursor that we keep increasing as we read the file
    cur = 0

    magic = ystHex[cur:cur+INT]
    yap(f"Magic: {codecs.decode(magic, 'hex').decode('cp932')}", DEBUG)
    decode['magic'] = codecs.decode(magic, 'hex').decode('cp932')
    cur += INT

    version = le_hex_to_int(ystHex[cur:cur+INT])[0]
    yap(f"Version: {version}", DEBUG)
    decode['version'] = version
    cur += INT

    numinstructions = le_hex_to_int(ystHex[cur:cur+INT])[0]
    yap(f"Instructions: {numinstructions}", DEBUG)
    decode['numinstructions'] = numinstructions
    cur += INT

    instructionsize = le_hex_to_int(ystHex[cur:cur+INT])
    yap(f"InstructionsSize: {instructionsize}", DEBUG)
    decode['instructionsize'] = instructionsize
    cur += INT

    attribdesc = le_hex_to_int(ystHex[cur:cur+INT])[0]
    yap(f"attributedesc: {attribdesc}", DEBUG)
    decode['attribdesc'] = attribdesc
    cur += INT

    attribvalue = le_hex_to_int(ystHex[cur:cur+INT])[0]
    yap(f"attribvalue: {attribvalue}", DEBUG)
    decode['attribvalue'] = attribvalue
    cur += INT

    linenumsize = le_hex_to_int(ystHex[cur:cur+INT])[0]
    yap(f"linenumsize: {linenumsize}", DEBUG)
    decode['linenumsize'] = linenumsize
    cur += INT

    # Padding
    cur += INT

    # Finding XOR key.
    # In the instruction list, END is always placed at the end (duh), and it's values are always
    # 0C 00 00 00. By XORing it back, we can get the XOR decryption key.
    endinstr = ystHex[cur+(numinstructions*INT)-INT:][:INT]
    decrypthex = f"{(int(endinstr, 16) ^ int("0C000000",16)):X}"
    yap(f"Decrypt KEY: {decrypthex}", DEBUG)

    # Using the decrypted list to continue:
    decrYstHex = rolling_xor(ystHex[cur:],decrypthex)
    # If true, prints back the decrypted file for referencing
    #yap(decrYstHex, True)
    
    # Initialize a new set of cursor variables
    cur, attribCur = 0, 0

    instrMax = (BYTE*4)*numinstructions
    attribMax = ((SHORT*2+INT*2)*int(attribdesc/12))+instrMax
    attribVarMax = (BYTE*attribvalue)+attribMax

    attribCur += INT
    print("Instructions:")
    print(decrYstHex[:instrMax])
    print("Attributes:")
    print(decrYstHex[instrMax:attribMax])
    print("AttributeValues:")
    print(decrYstHex[attribMax:attribVarMax])
    print("LineNumbers:")
    print(decrYstHex[attribVarMax:])

    instrSpace = decrYstHex[:instrMax]
    attribSpace = decrYstHex[instrMax:attribMax]
    attribVarSpace = decrYstHex[attribMax:attribVarMax]
    lineNumSpace = decrYstHex[attribVarMax:]

    for i in range(0, numinstructions):
        yap(f"\nInstr: {i}", DEBUG)

        opcode = le_hex_to_int(decrYstHex[cur:cur+BYTE])[1]
        yap(f"opcode: {opcode}", DEBUG)
        decode['opcode'] = opcode
        cur += BYTE

        numattrib = le_hex_to_int(decrYstHex[cur:cur+BYTE])[0]
        yap(f"numattrib: {numattrib}", DEBUG)
        decode['numattrib'] = numattrib
        cur += BYTE

        # Skipping unknown byte and padding (byte)
        # TODO Check if they're useful somehow
        # skipped = le_hex_to_int(decrYstHex[cur:cur+SHORT])
        # yap(f"skipped: {skipped}", DEBUG)
        cur += SHORT

        for attribIndex in range(0, numattrib):
            yap(f"-> Attrib: {attribIndex}", DEBUG)

            # debugtxt = decrYstHex[cur:cur+INT*4]
            # print(debugtxt)
            # yap(f"debugtxt: {codecs.decode(debugtxt, 'hex').decode('cp932')}", DEBUG)
            # decode['debugtxt'] = codecs.decode(debugtxt, 'hex').decode('cp932')

            id = le_hex_to_int(attribSpace[attribCur:attribCur+SHORT])
            yap(f"id: {id}", DEBUG)
            decode['id'] = id
            attribCur += SHORT

            type = le_hex_to_int(attribSpace[attribCur:attribCur+SHORT])
            yap(f"type: {type}", DEBUG)
            decode['type'] = type
            attribCur += SHORT

            size = le_hex_to_int(attribSpace[attribCur:attribCur+INT])[0]
            yap(f"size: {size}", DEBUG)
            decode['size'] = size
            attribCur += INT

            offset = le_hex_to_int(attribSpace[attribCur:attribCur+INT])[0]
            yap(f"offset: {offset}", DEBUG)
            decode['offset'] = offset
            attribCur += INT

            # The attributes are stored in a separate portion of the file, using a wonky mixed-case format
            attribVarHex = attribVarSpace[offset*BYTE:offset*BYTE+size*BYTE]
            print(attribVarHex)
            attribVarCur = 0
            decAttrib = {}
            while(len(attribVarHex) > attribVarCur):
                len(attribVarHex[attribVarCur:])
                decAttrib['type'] = attribVarHex[attribVarCur:attribVarCur+BYTE]
                attribVarCur += BYTE
                decAttrib['size'] = int(attribVarHex[attribVarCur:attribVarCur+BYTE], 16)
                attribVarCur += BYTE*2 #Jumping ahead of padding
                decAttrib['value'] = attribVarHex[attribVarCur:attribVarCur+BYTE*decAttrib['size']]
                attribVarCur += BYTE*decAttrib['size']
                print(decAttrib)
            # value = le_hex_to_int(attribVarSpace[offset*BYTE:offset*BYTE+size*BYTE])[0]
            # yap(f"value: {value}", DEBUG)
            # decode['value'] = value
            # attribVarCur += offset*BYTE


    
    # print(decrYstHex[cur:])

    # for i in range(0, int(attribdesc/12)):
    #     yap(f"\nAttrib: {i}", DEBUG)

    #     # debugtxt = decrYstHex[cur:cur+INT*4]
    #     # print(debugtxt)
    #     # yap(f"debugtxt: {codecs.decode(debugtxt, 'hex').decode('cp932')}", DEBUG)
    #     # decode['debugtxt'] = codecs.decode(debugtxt, 'hex').decode('cp932')

    #     id = le_hex_to_int(decrYstHex[cur:cur+SHORT])
    #     yap(f"id: {id}", DEBUG)
    #     decode['id'] = id
    #     cur += SHORT

    #     type = le_hex_to_int(decrYstHex[cur:cur+SHORT])
    #     yap(f"type: {type}", DEBUG)
    #     decode['type'] = type
    #     cur += SHORT

    #     size = le_hex_to_int(decrYstHex[cur:cur+INT])
    #     yap(f"size: {size}", DEBUG)
    #     decode['size'] = size
    #     cur += INT

    #     offset = le_hex_to_int(decrYstHex[cur:cur+INT])
    #     yap(f"offset: {offset}", DEBUG)
    #     decode['offset'] = offset
    #     cur += INT

    # print(decrYstHex[cur:])