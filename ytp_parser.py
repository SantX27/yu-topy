import os
import codecs
import struct
from func import *

def readExtractYPF(folder_path): #TODO everything
    DEBUG = True

    ypf_path = "cgsys.ypf"
    if not os.path.exists(ypf_path):
        # We didn't find the file
        return 1
    
    with open(ypf_path, 'rb') as f:
        ypf_hex = memoryview(f.read())
    yap(f"Decoding {ypf_path}:", DEBUG)

    # header = 4s
    # version = i
    # indexEntryCount = i
    # indexBlockSize = i
    # padding = 16x

    header_fmt = "<4s3i16x"
    header_hex = ypf_hex[:struct.calcsize(header_fmt)]
    header_unpack = struct.unpack(header_fmt, header_hex)
    header_dict = {
        'header' : header_unpack[0],
        'version' : header_unpack[1],
        'index_entry_count' : header_unpack[2],
        'index_block_size' : header_unpack[3]
    }
    print(header_dict)
    
    path_hex = ypf_hex[struct.calcsize(header_fmt):]
    path_cur = 0

    # RelativePathCRC = i
    # RelativePathSize = B
    # Path = [RelativePathSize]s
    # Filetype = B
    # CompFlag = B
    # DecompressionSize = i
    # CompressionSize = i
    # DataOffset = q
    # DataCRC = i   (murmurhash)

    path_fmt = '<iB'
    path_unpack = struct.unpack(path_fmt, path_hex[path_cur:struct.calcsize(path_fmt)+path_cur])
    path_dict = {
        'relative_path_crc' : path_unpack[0],
        'relative_path_size' : 256 - path_unpack[1]
    }
    path_fmt = f"<iB{path_dict['relative_path_size']}s2B2iqi"
    path_unpack = struct.unpack(path_fmt, path_hex[path_cur:struct.calcsize(path_fmt)+path_cur])
    path_dict.update({
        'relative_path' : path_unpack[2].hex(),
        'file_type' : path_unpack[3],
        'comp_flag' : path_unpack[4],
        'decompression_size' : path_unpack[5],
        'compression_size' : path_unpack[6],
        'data_offset' : path_unpack[7],
        'data_crc' : path_unpack[8]
    })
    print(path_dict)
    


def readExtractYSTL(folder_path): #TODO Only on Euphoria, add detection compile flags
    
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

def readExtractYSLB(folder_path):
    
    DEBUG = True

    ysl_path = os.path.join(folder_path, "ysl.ybn")
    if not os.path.exists(ysl_path):
        # We didn't find the file
        return 1
    
    with open(ysl_path, 'rb') as f:
        ysl_hex = memoryview(f.read())
    yap(f"Decoding {ysl_path}:", DEBUG)

    # Header = 4s
    # Version = i
    # NumLabels = i
    # LabelRangeStartIndexes = 1024x
    header_fmt = "<4s2i1024x"
    header_hex = ysl_hex[:struct.calcsize(header_fmt)]
    header_unpack = struct.unpack(header_fmt, header_hex)
    print(header_unpack)
    header_dict = {
        'header' : header_unpack[0],
        'version' : header_unpack[1],
        'num_labels' : header_unpack[2],
        #'label_range_start_index' : header_unpack[3],   #we ignore this shit
        'labels' : []
    }
    label_hex = ysl_hex[struct.calcsize(header_fmt):]
    label_cur = 0

    for label_num in range(header_dict['num_labels']): #cycle
        # NameLength = B
        # Name = NameLength s
        # Id = i
        # Offset = i
        # ScriptIndex = h
        # Padding = 2x

        label_fmt = "<B"
        label_unpack = struct.unpack(label_fmt, label_hex[label_cur:struct.calcsize(label_fmt)+label_cur])
        label_dict = {
            'name_length' : label_unpack[0],
        }
        label_fmt = f"<B{label_dict['name_length']}s2Ih2x"
        label_unpack = struct.unpack(label_fmt, label_hex[label_cur:struct.calcsize(label_fmt)+label_cur])
        label_dict.update({
            'name' : codecs.decode(label_unpack[1].hex(), 'hex').decode('cp932'),
            'id' : label_unpack[2],
            'offset' : label_unpack[3],
            'script_index' : label_unpack[4]
        })

        label_cur += struct.calcsize(label_fmt)
        header_dict['labels'].append(label_dict)
    print(header_dict['labels'])

def readExtractYSVR(folder_path):

    DEBUG = True

    ysv_path = os.path.join(folder_path, "ysv.ybn")
    if not os.path.exists(ysv_path):
        # We didn't find the file
        return 1
    
    with open(ysv_path, 'rb') as f:
        ysv_hex = f.read()
    yap(f"Decoding {ysv_path}:", DEBUG)

    # Header = 4s
    # Version = i
    # num_vars = h

    header_fmt = "<4sih"
    header_hex = ysv_hex[:struct.calcsize(header_fmt)]
    header_unpack = struct.unpack(header_fmt, header_hex)

    header_dict = {
        'header' : header_unpack[0],
        'version' : header_unpack[1],
        'num_variables' : header_unpack[2],
        'variables' : []
    }

    # Scope (1 = global, 2 = static) = B
    # ScriptId = h
    # VarIndex = h
    # Type (0 = null, 1 = long, 2 = double, 3 = string) = B
    # NumDimensions = B
    # DimensionSize = NumDimensions i
    # Value
        # if Type == 1 (long)
        # if Type == 2 (double)
        # if Type == 3 {
        #   ExprLength = H
        #   Expr[ExprLength] = s
        #   }

    var_hex = ysv_hex[struct.calcsize(header_fmt):]
    var_cur = 0

    for var_num in range(header_dict['num_variables']): #cycle
        var_fmt = "<B2h2B"
        var_unpack = struct.unpack(var_fmt, var_hex[var_cur:struct.calcsize(var_fmt)+var_cur])
        var_dict = {
            'scope' : var_unpack[0],
            'script_id' : var_unpack[1],
            'var_index' : var_unpack[2],
            'type' : var_unpack[3],
            'num_dimension' : var_unpack[4],
        }

        match var_dict['type']:
            case 0: type_unpack = ""  # Value None
            case 1: type_unpack = "q" # Value q
            case 2: type_unpack = "d" # Value d
            case 3: type_unpack = "H" # expr_length H

        var_fmt = f"<B2h2B{var_dict['num_dimension']}i{type_unpack}"
        var_unpack = struct.unpack(var_fmt, var_hex[var_cur:struct.calcsize(var_fmt)+var_cur])
        var_dict.update({
            'dimension_size' : var_unpack[5:5+var_dict['num_dimension']],
            'value' : var_unpack[-1]
        })
        # print(var_dict)
        # print(f"Before expr: {var_hex[var_cur:struct.calcsize(var_fmt)+var_cur].hex()}")
        var_cur += struct.calcsize(var_fmt)

        #Let's get the value of Expr
        if type_unpack == "H":
            expr_fmt = f"<{var_dict['value']}s"
            expr_unpack = struct.unpack(expr_fmt, var_hex[var_cur:struct.calcsize(expr_fmt)+var_cur])
            var_dict.update({
                'expr' : expr_unpack
            })
            # print(var_dict)
            # print(f"After expr: {var_hex[var_cur:struct.calcsize(expr_fmt)+var_cur].hex()}")
            var_cur += struct.calcsize(expr_fmt)

        header_dict['variables'].append(var_dict)
    
    print(prettyDict(header_dict))

def readExtractYSCF(folder_path): 

    DEBUG = True

    yst_list_path = os.path.join(folder_path, "yscfg.ybn")
    if not os.path.exists(yst_list_path):
        # We didn't find the file
        return 1
    
    with open(yst_list_path, 'rb') as f:
        yst_hex = memoryview(f.read())
    yap(f"Decoding {yst_list_path}:", DEBUG)

    # Header = 4s
    # Version = i
    # padding = 4x
    # compile = i
    # screenW = i
    # screenH = i
    # enable = i
    # imagetypeslot = B
    # soundtypeslot = B
    # thread = i
    # debugmode = i
    # sound = i
    # windowresize = i
    # windowframe = i
    # fileprioritydev = i
    # fileprioritydebug = i
    # filepriorityrelease = i
    # padding = 4x
    # captionlen = h
    # caption = [captionlen]s
    header_fmt = "<4si4x4i8B4B5i4xh" #add 3i before 4x for euphoria

    header_hex = yst_hex[:struct.calcsize(header_fmt)]
    header_unpack = struct.unpack(header_fmt, header_hex)
    print(header_unpack)
    header_dict = {
        'header' : header_unpack[0],
        'version' : header_unpack[1],
        #padding
        'compile' : header_unpack[2],
        'screen_width' : header_unpack[3],
        'screen_height' : header_unpack[4],
        'enable' : header_unpack[5],
        'image_type_slot' : header_unpack[5:13], #needs 8
        'sound_type_slot' : header_unpack[13:17], #needs 4
        'thread' : header_unpack[18],
        'debugmode' : header_unpack[10],
        'sound' : header_unpack[20],
        'window_resize' : header_unpack[21],
        'window_frame' : header_unpack[22],
        #TODO Euphoria needs these following bytes, find workaround
        #'file_priority_dev' : header_unpack[23],
        #'file_priority_debug' : header_unpack[24],
        #'file_priority_release' : header_unpack[25],
        #padding
        'caption_length' : header_unpack[23],
    }
    caption_cur = 0
    caption_hex = yst_hex[struct.calcsize(header_fmt):]
    caption_fmt = f"<{header_dict['caption_length']}s"
    print(header_dict)
    caption_unpack = struct.unpack(caption_fmt, caption_hex[caption_cur:struct.calcsize(caption_fmt)+caption_cur])
    header_dict.update({
        'caption' : codecs.decode(caption_unpack[0].hex(), 'hex').decode('cp932'),
    })
    caption_cur += struct.calcsize(caption_fmt)
    print(header_dict)

def readExtractYSTB(folder_path): # TODO FIX EXTRACT INSTRUCTION AND ATTRIBUTE

    DEBUG = True

    yst_list_path = os.path.join(folder_path, "yst00118.ybn")
    if not os.path.exists(yst_list_path):
        # We didn't find the file
        return 1
    
    with open(yst_list_path, 'rb') as f:
        yst_hex = memoryview(f.read())
    yap(f"Decoding {yst_list_path}:", DEBUG)

    # Header = 4s
    # Version = i
    # NumInstructions = i
    # InstructionsSize = i
    # AttributeDescriptorSize = i
    # AttributeValueSize = i
    # Line NumberSize = i
    # padding = 4x

    header_fmt = "<4s6i4x"
    header_hex = yst_hex[:struct.calcsize(header_fmt)]
    header_unpack = struct.unpack(header_fmt, header_hex)
    header_dict = {
        'header' : header_unpack[0],
        'version' : header_unpack[1],
        'num_instructions' : header_unpack[2],
        'instruction_size' : header_unpack[3],
        'attrib_desc_size': header_unpack[4],
        'attrib_val_size': header_unpack[5],
        'line_num_size' : header_unpack[6],
        'instructions' : []
    }
    print(header_dict)

    # Finding XOR key.
    # In the instruction list, END is always placed at the end (duh), and it's values are always
    # 0C 00 00 00. By XORing it back, we can get the XOR decryption key.
    # We find it by cutting the header + number of instructions * 4 bytes,
    # We subtract the last 4 bytes (our END location), then we trim it. 
    end_instruction = yst_hex[struct.calcsize(header_fmt)+(header_dict['num_instructions']*4)-4:][:4]
    if end_instruction.hex() != "0c000000":
        xor_key = f"{int(end_instruction.hex(),16) ^ int("0C000000",16):X}"
        print(f"Decrypt KEY: {xor_key}")
        instruction_hex = bytes.fromhex(rolling_xor(yst_hex[struct.calcsize(header_fmt):].hex(), xor_key))
    else:
        print("File already decrypted!")
        instruction_hex = yst_hex[struct.calcsize(header_fmt):]
        
    # Opcode = B
    # numAttribute = B
    # ? = B
    # padding = x

    instruction_cur = 0

    instruction_fmt = "<3Bx"

    instruction_dict = {

    }

    instruction_unpack = struct.unpack(instruction_fmt, instruction_hex[instruction_cur:struct.calcsize(instruction_fmt)+instruction_cur])
    print(instruction_unpack)

def readExtractYSCM(folder_path):
    
    DEBUG = True

    ysc_path = os.path.join(folder_path, "ysc.ybn")
    if not os.path.exists(ysc_path):
        # We didn't find the file
        return 1
    
    with open(ysc_path, 'rb') as f:
        ysc_hex = memoryview(f.read())
    yap(f"Decoding {ysc_path}:", DEBUG)

    # Header = 4s
    # Version = i
    # NumCommands = i
    # Padding = 4x
    header_fmt = "<4s2i4x"

    header_hex = ysc_hex[:struct.calcsize(header_fmt)]
    header_unpack = struct.unpack(header_fmt, header_hex)
    header_dict = {
        'header' : header_unpack[0],
        'version' : header_unpack[1],
        'num_commands' : header_unpack[2],
        'commands' : []
    }

    # Name = string_end s x
    # NumAttrib = B

    command_hex = ysc_hex[struct.calcsize(header_fmt):]
    command_cur = 0

    # Struct doesn't support null terminated strings ffs
    for command_num in range(header_dict['num_commands']):
        command_end = bytes(command_hex[command_cur:]).index(b'\x00')
        # print(f"Command next zero: {command_end}")

        command_fmt = f"<{command_end}sxB"
        command_unpack = struct.unpack(command_fmt, command_hex[command_cur:struct.calcsize(command_fmt)+command_cur])
        command_dict = {
            'name' : command_unpack[0],
            'num_attributes' : command_unpack[1],
            'attributes': []
        }
        # print(command_dict)
        command_cur += struct.calcsize(command_fmt)

        for attribute_num in range(command_dict['num_attributes']):
            # Name attribute_end s x
            # Type B
            # Vaid B
    
            if command_dict['num_attributes'] > 0:
                attribute_end = bytes(command_hex[command_cur:]).index(b'\x00')
                # print(f"Attribute next zero: {attribute_end}")
                attribute_fmt = f"<{attribute_end}sx2B"
                attribute_unpack = struct.unpack(attribute_fmt, command_hex[command_cur:struct.calcsize(attribute_fmt)+command_cur])
                # print(attribute_unpack)
                command_cur += struct.calcsize(attribute_fmt)
                command_dict['attributes'].append({
                    'name' : attribute_unpack[0],
                    'type' : attribute_unpack[1],
                    'vaid' : attribute_unpack[2]
                })

        # print(command_dict)
        header_dict['commands'].append(command_dict)
    print(prettyDict(header_dict))
        # print("")

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
