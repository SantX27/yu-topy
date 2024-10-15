import os
import codecs
import struct
from func import *

def readExtractYPF(folder_path): #TODO everything
    DEBUG = True

    ypf_path = "cgsys.ypf"
    if not os.path.exists(ypf_path):
        # We didn't find the file
        print(f"Can't find {ypf_path}, ERROR!")
        return 1
    
    with open(ypf_path, 'rb') as f:
        ypf_hex = memoryview(f.read())
    yap(f"Decoding {ypf_path}", DEBUG)

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
    
def readExtractYSTL(folder_path, caption):
    '''
    Reads and extract yst_list.ybn file, which lists the properties, path and the filename of the yst*.ybn files
    '''

    DEBUG = True

    yst_list_path = os.path.join(folder_path, "yst_list.ybn")
    if not os.path.exists(yst_list_path):
        # We didn't find the file
        print(f"Can't find {yst_list_path}, ERROR!")
        return 1
    
    with open(yst_list_path, 'rb') as f:
        yst_hex = memoryview(f.read())
    yap(f"Decoding {yst_list_path}", DEBUG)

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
        # NumTexts = i  # Only on Euphoria
        script_fmt = "<2i"

        script_unpack = struct.unpack(script_fmt, script_hex[script_cur:struct.calcsize(script_fmt)+script_cur])
        script_dict = {
            'index' : script_unpack[0],
            'path_length' : script_unpack[1],
        }

        # The SDK uses a different format
        if caption != "(タイトル名)":
            script_fmt = f"<2i{script_dict['path_length']}sq3i"
            script_unpack = struct.unpack(script_fmt, script_hex[script_cur:struct.calcsize(script_fmt)+script_cur])
            script_dict.update({
                'path' : codecs.decode(script_unpack[2].hex(), 'hex').decode('cp932'),
                'num_variables' : script_unpack[4],
                'num_labels' : script_unpack[5],
                'num_texts' : script_unpack[6]
            })
        else:
            script_fmt = f"<2i{script_dict['path_length']}sq2i"
            script_unpack = struct.unpack(script_fmt, script_hex[script_cur:struct.calcsize(script_fmt)+script_cur])
            script_dict.update({
                'path' : codecs.decode(script_unpack[2].hex(), 'hex').decode('cp932'),
                'num_variables' : script_unpack[4],
                'num_labels' : script_unpack[5]
            })
        script_cur += struct.calcsize(script_fmt)
        header_dict['scripts'].append(script_dict)

    return header_dict

def readExtractYSLB(folder_path):
    '''
    Reads and extract the ysl.ybn file, which contains the labels of the project
    '''
    DEBUG = True

    ysl_path = os.path.join(folder_path, "ysl.ybn")
    if not os.path.exists(ysl_path):
        print(f"Can't find {ysl_path}, ERROR!")
        # We didn't find the file
        return 1
    
    with open(ysl_path, 'rb') as f:
        ysl_hex = memoryview(f.read())
    yap(f"Decoding {ysl_path}", DEBUG)

    # Header = 4s
    # Version = i
    # NumLabels = i
    # LabelRangeStartIndexes = 1024x
    header_fmt = "<4s2i1024x"
    header_hex = ysl_hex[:struct.calcsize(header_fmt)]
    header_unpack = struct.unpack(header_fmt, header_hex)
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
    
    return header_dict

def readExtractYSVR(folder_path):
    '''
    Reads and extract the ysv.ybn file which contains the variables of the project
    '''
    DEBUG = True

    ysv_path = os.path.join(folder_path, "ysv.ybn")
    if not os.path.exists(ysv_path):
        # We didn't find the file
        print(f"Can't find {ysv_path}, ERROR!")
        return 1
    
    with open(ysv_path, 'rb') as f:
        ysv_hex = f.read()
    yap(f"Decoding {ysv_path}", DEBUG)

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
    
    return header_dict

def readExtractYSCF(folder_path): 
    '''
    Read and extract the yscfg.ybn file, which contains the configurations of the project
    '''
    DEBUG = True

    ystcfg_path = os.path.join(folder_path, "yscfg.ybn")
    if not os.path.exists(ystcfg_path):
        # We didn't find the file
        print(f"Can't find {ystcfg_path}, ERROR!")
        return 1
    
    with open(ystcfg_path, 'rb') as f:
        yst_hex = memoryview(f.read())
    yap(f"Decoding {ystcfg_path}", DEBUG)

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
    # fileprioritydev = i #Not present on SDK builds!
    # fileprioritydebug = i #Not present on SDK builds!
    # filepriorityrelease = i #Not present on SDK builds!
    # padding = 4x
    # captionlen = h
    # caption = [captionlen]s

    # Let's extract the caption early so that we can account for missing data in SDK
    caption_start = bytes(yst_hex[::-1]).index(b'\x00')
    caption = bytes((yst_hex[::-1][:caption_start])[::-1]).decode("cp932")

    if caption != "(タイトル名)":
        header_fmt = "<4si4x4i8B4B5i3i4xh"
        header_hex = yst_hex[:struct.calcsize(header_fmt)]
        header_unpack = struct.unpack(header_fmt, header_hex)
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
            'file_priority_dev' : header_unpack[23],
            'file_priority_debug' : header_unpack[24],
            'file_priority_release' : header_unpack[25],
            #padding
            'caption_length' : header_unpack[26],
        }
    else:
        print("Found SDK file!")
        header_fmt = "<4si4x4i8B4B5i4xh"
        header_hex = yst_hex[:struct.calcsize(header_fmt)]
        header_unpack = struct.unpack(header_fmt, header_hex)
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
            #'file_priority_dev' : header_unpack[23],
            #'file_priority_debug' : header_unpack[24],
            #'file_priority_release' : header_unpack[25],
            #padding
            'caption_length' : header_unpack[23],
        }
    
    caption_cur = 0
    caption_hex = yst_hex[struct.calcsize(header_fmt):]
    caption_fmt = f"<{header_dict['caption_length']}s"
    caption_unpack = struct.unpack(caption_fmt, caption_hex[caption_cur:struct.calcsize(caption_fmt)+caption_cur])
    header_dict.update({
        'caption' : codecs.decode(caption_unpack[0].hex(), 'hex').decode('cp932'),
    })
    caption_cur += struct.calcsize(caption_fmt)
    
    return header_dict

def readExtractYSTB(folder_path):
    '''
    The definition of suffering, it reads and extract those fucking yst*.ybn files decompiling them and also finding the XOR key to """decrypt""" them.
    Those files are the reason why God abandoned us
    '''

    DEBUG = True

    yst_path = os.path.join(folder_path)
    if not os.path.exists(yst_path):
        # We didn't find the file
        print(f"Can't find {yst_path}, ERROR!")
        return 1
    
    with open(yst_path, 'rb') as f:
        yst_hex = memoryview(f.read())
    yap(f"Decoding {yst_path}", True)

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

    # Finding XOR key.
    # In the instruction list, END is always placed at the end (duh), and it's values are always
    # 0C 00 00 00. By XORing it back, we can get the XOR decryption key.
    # We find it by cutting the header + number of instructions * 4 bytes,
    # We subtract the last 4 bytes (our END location), then we trim it. 
    end_instruction = yst_hex[struct.calcsize(header_fmt)+(header_dict['num_instructions']*4)-4:][:4]
    if end_instruction.hex() != "0c000000":
        xor_key = f"{int(end_instruction.hex(),16) ^ int("0C000000",16):X}"
        print(f"Decrypt KEY: {xor_key}")
        decoded_hex = memoryview(bytes.fromhex(rolling_xor(yst_hex[struct.calcsize(header_fmt):].hex(), xor_key)))
    else:
        print("File already decrypted!")
        decoded_hex = yst_hex[struct.calcsize(header_fmt):]
        
    # Splitting the lists.
    # To find peace of mind and not end up crazy, we predefine
    # the Attributes and AttributeValues lists, by finding their
    # max byte extension and by splitting the yst_hex according to
    # their region.

    # Instructions are a group of 4 bytes * their number + the header bytes.
    instruction_max = (4*header_dict['num_instructions'])
    # AttributeDescriptors are a group of 12 bytes * their size/12 + instruction_max
    attrib_desc_max = instruction_max+(12*int(header_dict['attrib_desc_size']/12))
    # AttributeValues are a single byte * their size + attrib_desc_max
    attrib_val_max = attrib_desc_max+header_dict['attrib_val_size']

    instruction_hex = decoded_hex[:instruction_max]
    attrib_desc_hex = decoded_hex[instruction_max:attrib_desc_max]
    attrib_val_hex = decoded_hex[attrib_desc_max:attrib_val_max]

    instruction_cur = 0
    attrib_desc_cur = 0

    for instruction_num in range(header_dict['num_instructions']):

        # Opcode = B
        # numAttributes = B
        # ? = B
        # padding = x

        instruction_fmt = "<3Bx"
        instruction_unpack = struct.unpack(instruction_fmt, instruction_hex[instruction_cur:struct.calcsize(instruction_fmt)+instruction_cur])
        instruction_dict = {
            'opcode' : hex(instruction_unpack[0]),
            'instruction_num' : instruction_num,
            'num_attributes' : instruction_unpack[1],
            'missing_na' : instruction_unpack[2],
            'attributes' : []
        }
        instruction_cur += struct.calcsize(instruction_fmt)
        
        # Let's get them attribussy
        for attribute_num in range(instruction_dict['num_attributes']):
            # ID = h
            # Type = h
            # Size = i
            # OffsetAttribVal = i

            attrib_desc_fmt = "<2h2i"
            attrib_desc_unpack = struct.unpack(attrib_desc_fmt, attrib_desc_hex[attrib_desc_cur:struct.calcsize(attrib_desc_fmt)+attrib_desc_cur])
            attrib_desc_cur += struct.calcsize(attrib_desc_fmt)
            attrib_desc_dict = {
                'id' : attrib_desc_unpack[0],
                'type' : attrib_desc_unpack[1],
                'size' : attrib_desc_unpack[2],
                'offset' : attrib_desc_unpack[3],
                'attrib_val' : []
            }

            # Fishing the attribute value
            single_attrib_val = attrib_val_hex[attrib_desc_dict['offset']:attrib_desc_dict['size']+attrib_desc_dict['offset']]
            # print(single_attrib_val.hex())

            # Type = B
            # Size = B
            # Padding/Size_upper = B
            # Value = Size s

            attrib_val_cur = 0
            
            while True:
                # Try reading enough bytes to unpack an argument, if it fails then we're good. 
                try:
                    # Check if the instruction follows the FUCKING RULES, we got straggler bytes everywhere.
                    if attrib_val_cur != 0:
                        # print(f"HEX {single_attrib_val[attrib_val_cur:].hex()}")
                        attrib_zero_pad = bytes(single_attrib_val[attrib_val_cur:]).index(b'\x00')
                        # print(f"Next zero: {attrib_zero_pad}")
                        if attrib_zero_pad == 1:
                            #Check if next byte is a padding byte, else we fault on this b
                            if single_attrib_val[attrib_val_cur+attrib_zero_pad:attrib_val_cur+attrib_zero_pad+1] != b'\x00':
                                print(f"Fuck this {single_attrib_val[attrib_val_cur:].hex()}")
                                break
                        elif attrib_zero_pad > 2:
                            # Honowi fumbled the bytes, let's fix his mistakes
                            # print(f"{single_attrib_val[attrib_val_cur:].hex()}")
                            #Let's naively skip the extra bytes at the beginning, so that it lines up again to two bytes.
                            attrib_val_cur += attrib_zero_pad - 2
                            # print(f"{single_attrib_val[attrib_val_cur:].hex()}")

                    attrib_val_fmt = "<3B"
                    attrib_val_unpack = struct.unpack(attrib_val_fmt, single_attrib_val[attrib_val_cur:struct.calcsize(attrib_val_fmt)+attrib_val_cur])
                    attrib_val_dict = {
                        'arg_type' : hex(attrib_val_unpack[0]),
                        'size' : attrib_val_unpack[1]
                    }
                    # If we're reading a pushstring, tha padding byte becomes the size short upper byte, for whatever retarded reason.
                    if attrib_val_dict['arg_type'] == "0x4d" and attrib_val_unpack[2] != 0:
                        attrib_val_fmt = "<BH"
                        attrib_val_unpack = struct.unpack(attrib_val_fmt, single_attrib_val[attrib_val_cur:struct.calcsize(attrib_val_fmt)+attrib_val_cur])
                        attrib_val_dict['size'] = attrib_val_unpack[1]

                    attrib_val_fmt = f"<3B{attrib_val_dict['size']}s"
                    attrib_val_unpack = struct.unpack(attrib_val_fmt, single_attrib_val[attrib_val_cur:struct.calcsize(attrib_val_fmt)+attrib_val_cur])
                    attrib_val_cur += struct.calcsize(attrib_val_fmt)
                    attrib_val_dict['value'] = attrib_val_unpack[3].hex()
                    attrib_desc_dict['attrib_val'].append(attrib_val_dict)
                except (struct.error, ValueError):
                    break
            
            instruction_dict['attributes'].append(attrib_desc_dict)

        header_dict['instructions'].append(instruction_dict)

    return header_dict

def readExtractYSCM(folder_path):
    '''
    Reads and extract the ysc.ybn files, which contains the instruction present inside the yst*.ybn files that have been compiled
    '''
    DEBUG = True

    ysc_path = os.path.join(folder_path, "ysc.ybn")
    if not os.path.exists(ysc_path):
        # We didn't find the file
        print(f"Can't find {ysc_path}, ERROR!")
        return 1
    
    with open(ysc_path, 'rb') as f:
        ysc_hex = memoryview(f.read())
    yap(f"Decoding {ysc_path}", DEBUG)

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
            'opcode': hex(command_num),
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

    return header_dict