import os
import codecs
import struct
from func import *
from ytp_parser import *

def instructionParser(script_index, YSTB, YSCM, YSTL, YSVR, YSLB):

    parsed_script = []

    #Load script specific info
    script_labels = search_value(script_index, 'script_index', YSLB['labels'])
    # TODO read the rest of the infos

    for num_instruction, instruction in enumerate(YSTB['instructions']):
        # PARSE ALL THE LABELS
        for label in search_value(num_instruction, 'offset', script_labels):
            parsed_script.append({
                'type' : "label",
                'value' : label['name']
            })
        # PARSE THE FUCKING INSTRUCTIONS

        parsed_script.append({
            'type' : "instruction",
            'opcode' : YSCM['commands'][int(instruction['opcode'], 16)]['name'].decode("cp932"),
            'attributes' : []
        })

        for attribute in instruction['attributes']:
            attribute_dict = {
                'attrib_values' : []
            }
            # PARSE ALL THE ATTRIBUTES OF THE INSTRUCTIONS

            # If we have named arguments for our instruction, we extract it, so that we can map the attributes better later
            if len(YSCM['commands'][int(instruction['opcode'], 16)]['attributes']) > 0:
                attribute_dict.update({
                    'argument': YSCM['commands'][int(instruction['opcode'], 16)]['attributes'][attribute['id']]['name'].decode("cp932"),
                })

            for attrib_val in attribute['attrib_val']:
                match attrib_val['arg_type']:
                    # Parse VM instructions
                    case "0x21":
                        value = "vm_notequal"
                    case "0x25":
                        value = "vm_mod"
                    case "0x26":
                        value = "vm_logand"
                    case "0x29":
                        value = "vm_performvarindexation"
                    case "0x2a":
                        value = "vm_mul"
                    case "0x2b":
                        value = "vm_add"
                    case "0x2c":
                        value = "vm_nop"
                    case "0x2d":
                        value = "vm_sub"
                    case "0x2f":
                        value = "vm_div"
                    case "0x3d":
                        value = "vm_equal"
                    case "0x3c":
                        value = "vm_less"
                    case "0x3e":
                        value = "vm_greater"
                    case "0x41":
                        value = "vm_binand"
                    case "0x4f":
                        value = "vm_binor"
                    case "0x52":
                        value = "vm_changesign"
                    case "0x53":
                        value = "vm_lessequal"
                    case "0x5a":
                        value = "vm_greaterequal"
                    case "0x5e":
                        value = "vm_binxor"
                    case "0x69":
                        value = "vm_tonumber"
                    case "0x73":
                        value = "vm_tostring"
                    case "0x7c":
                        value = "vm_logor"
                    # Parse data types

                    # Parse pushint8/pushint16/pushint32/pushint64
                    case "0x42" | "0x49" | "0x4c" | "0x57":
                            value = le_hex_to_int(attrib_val['value'])[0]
                    # Parse pushstring
                    case "0x4d":
                            value = bytes.fromhex(attrib_val['value']).decode('cp932')
                    #Parse pushscalarvar
                    case "0x48":
                            value = f"{bytes.fromhex(attrib_val['value'][:2]).decode('cp932')}{le_hex_to_int(attrib_val['value'][2:])[0]}"
                    case _:
                            value = f"UNMAPPED {attrib_val['arg_type']}: {attrib_val['value']}!!!"
                
                attribute_dict['attrib_values'].append(value)
            parsed_script[-1]['attributes'].append(attribute_dict)
    return parsed_script

    #YSTB['instructions'][num_instruction]['attributes'][num_attribute]['attrib_val'][0]['value']