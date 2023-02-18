import os
import re
import sys
import argparse

def read_extract_yst_list(folder_path):
    yst_list_path = os.path.join(folder_path, "yst_list.ybn")
    if not os.path.exists(yst_list_path):
        print("We're missing dat yst_list.ybn, chief.")
        print("Check if you're running me in the right folder")
        quit()
    
    with open(yst_list_path, 'r', encoding='cp932', errors='ignore') as f:
        list_lines = f.readlines()

    yst_dict = []
    yst_index = 0
    for single_list in list_lines:
        og_names = re.findall(r'(?:data)(.*?)(?:.yst|.txt)', single_list)
        for og_name in og_names:
            if "userscript" in og_name:
                base_name = og_name.split("\\", 3)[3]
                # Try to predict the implicit file name using the yst_list
                chap_split = base_name.split("\\", 3)
                match chap_split[0]:
                    case "01-op":
                        pred_name = f"00_op_{chap_split[1].split('-')[0]}"
                    case "02-前半":
                        pred_name = f"01_kyo_{chap_split[2].split('-')[0]}"
                yst_dict.append({
                    'pred_file': f'yst{str(yst_index).zfill(5)}',
                    'base_name': base_name,
                    'pred_name': pred_name
                })
            yst_index += 1
    return yst_dict

def decode_yst_file(file_name):
    with open(file_name, 'r', encoding='utf-16-le') as f:
        yst_lines = f.readlines()

    arg_list = []
    for num_line, line in enumerate(yst_lines):
        # Decode argument type
        if "inst_arg" in line:
            inst_arg = re.findall(r'\:([^:]*)\,', line)[0] #regex match :"string",
            num_args = int(re.findall(r'\:([^,[]*)\]', line)[0], 16) - 1
            match inst_arg:
                case "0x1D":
                    arg_type = "eris"
                case "0x5F":
                    arg_type = "text"
                case "0x40":
                    arg_type = "stop"
                case "0x1C":
                    arg_type = "jump"
                case _:
                    arg_type = "unkn"

            arg_dic = {
                'inst_arg': inst_arg,
                #'num_args': num_args,
                'arg_type': arg_type
                }
        # Decode argument data
        if "rsc_data" in line:
            try:
                #rsc_arg = re.findall(r'\"([^:]*)\"', line)[0]
                rsc_arg = re.findall(r'"([^"]*)', line)[0]
            except IndexError:
                try:
                    rsc_arg = re.findall(r'\[([^:]*)\]', line)[1]
                except IndexError:
                    rsc_arg = re.findall(r"\'([^:]*)\'", line)[0]

            rsc_idx = re.findall(r'rsc_data\[(\d*)\]', line)[0]

            if arg_type == "text":
                name, _, quote = rsc_arg.partition(':')

                # Handle text()
                if quote:
                    quote = quote.strip().strip('“').strip('”')
                    name = name.replace('／', '/')
                    arg_dic['name'] = name
                    arg_dic['quote'] = quote
                else:
                    arg_dic['quote'] = name

            # Handle stop() -> Do nothing
            elif arg_type == "stop":
                continue

            # Handle eris()
            elif arg_type == "eris":
                try:
                    if rsc_idx == "0":
                        arg_dic['func_arg'].append(rsc_arg)
                    else:
                        arg_dic['func_arg'][-1] = [arg_dic['func_arg'][-1], rsc_arg] 
                except KeyError:
                    arg_dic['func_name'] = rsc_arg
                    arg_dic['func_arg'] = []

            # Unknown function
            else:

                try:
                    arg_dic['func_arg'].append(rsc_arg)
                except KeyError:
                    arg_dic['func_arg'] = []
                    arg_dic['func_arg'].append(rsc_arg)

        if line == '\n':
            arg_list.append(arg_dic)
    return arg_list

#TODO
# Sprite positioning
# * Base
# - Precise positioning
# - Zoom on character (SP001 - SP002)
# - Better transitioning
# Music
# * Base
# - Separate audio channels * character
# - Sustain voice until next voice 
# Scenario select / jump
# Autogenerate whole project
# * OP
# - 1st Common

def encode_renpy_file(arg_list):
    init_list = []
    script_list = []

    for single_arg in arg_list:

        if single_arg['arg_type'] == "text":
            try:
                script_list.append(f"\"{single_arg['name']}\" \"{single_arg['quote']}\"")
            except KeyError:
                script_list.append(f"\"{single_arg['quote']}\"")

        if single_arg['arg_type'] == "eris" and single_arg['func_name'] == "MAC.BG":
            try:
                if not any(single_arg['func_arg'][0] in string for string in init_list):
                    init_list.append(f"image {single_arg['func_arg'][0]} = im.Scale(\"images/bg/{single_arg['func_arg'][0]}.png\", 1920, 1080)")
            except:
                continue
            script_list.append(f"scene {single_arg['func_arg'][0]}")
            script_list.append("with dissolve")

        if single_arg['arg_type'] == "eris" and single_arg['func_name'] == "es.SP.ST.SET":
            chara = (single_arg['func_arg'][1].split("_")[1][:3])
            match chara:
                case "NEM":
                    image_path = "images/stand/01_nem/"
                case "KAN":
                    image_path = "images/stand/02_kan/"
                case "RIN":
                    image_path = "images/stand/03_rin/"
                case "RIK":
                    image_path = "images/stand/04_rik/"
                case "NAT":
                    image_path = "images/stand/05_nat/"
                case "MIY":
                    image_path = "images/stand/11_miy/"
                
            if not any(single_arg['func_arg'][1] in string for string in init_list):
                init_list.append(f"image {chara} {single_arg['func_arg'][1]} = \"{image_path}{single_arg['func_arg'][1]}.png\"")
            script_list.append(f"show {chara} {single_arg['func_arg'][1]}")
        
        if single_arg['arg_type'] == "eris" and single_arg['func_name'] == "es.SP.X.SET":
            if "show" in script_list[-1] and not "at" in script_list[-1]:
                # print(type(single_arg['func_arg'][1]))
                if isinstance(single_arg['func_arg'][1], list):
                    script_list[-1] += " at left"
                elif "C8 00 " == single_arg['func_arg'][1]:
                    script_list[-1] += " at right"

        if single_arg['arg_type'] == "eris" and single_arg['func_name'] == "es.SP.DEL.SET":
            script_list.append(f"hide {single_arg['func_arg'][0]} with dissolve")

        if single_arg['arg_type'] == "eris" and single_arg['func_name'] == "es.SND":
            match single_arg['func_arg'][0]:
                case "15 ":
                    sound_type = "voice"
                    sound_name = single_arg['func_arg'][1].lower() + ".ogg"
                    sound_path = "audio/voice/" + sound_name
                case "01 ":
                    sound_type = "music"
                    sound_name = single_arg['func_arg'][1][2:] + ".ogg"
                    sound_path = "audio/bgm/" + sound_name
                case "0B " | "0C ":
                    sound_type = "sound"
                    sound_name = single_arg['func_arg'][1].lower() + ".ogg"
                    sound_path = "audio/se/" + sound_name
                
            if single_arg['func_arg'][1]:     
                if sound_type == "voice":
                    script_list.append(f"{sound_type} \"{sound_path}\"")
                    script_list.append("voice sustain")
                else:
                    script_list.append(f"play {sound_type} \"{sound_path}\"")
            else:
                if sound_type != "voice":
                    script_list.append(f"stop {sound_type}")
        
        if single_arg['arg_type'] == "jump" and single_arg['func_arg'][0][:4].find('_') != -1:
            script_list.append(f"call yu_{single_arg['func_arg'][0]}")
            try:
                # print(choice_list)
                # print(f"choice_pos: {choice_pos}")
                script_list.append(f"\nlabel yu_{choice_list[choice_pos]['choice_id']}:")
                choice_pos += 1
            except:
                continue #Not sure it's the right way but for now screw it

        if single_arg['arg_type'] == "eris" and single_arg['func_name'] == "ES.SEL.GO":
            choice_pos = 0
            choice_list = []
            for choice_id in single_arg['func_arg']:
                if choice_id:
                    choice_list.append({
                        'choice_id': choice_id
                    })

        if single_arg['arg_type'] == "eris" and single_arg['func_name'] == "ES.SEL.SET":
            for idx, choice_name in enumerate(single_arg['func_arg']):
                if choice_name:
                    choice_list[idx]['choice_name'] = choice_name.strip().strip('“').strip('”')
            script_list.append("menu:")
            if choice_list:
                for choice in choice_list:
                    script_list.append(f"    \"{choice['choice_name']}\":")
                    script_list.append(f"        jump yu_{choice['choice_id']}")
                # print(choice_list)
                # print(f"choice_pos: {choice_pos}")
                script_list.append(f"\nlabel yu_{choice_list[choice_pos]['choice_id']}:")
                choice_pos += 1



    init_list.sort()
    # print('\n'.join(init_list))
    # print()
    # print('\n'.join(script_list))
    # It's fucking ugly but that just fucking does it
    return '    ' +'\n    '.join(init_list) + '\n\n    ' + '\n    '.join(script_list)

if __name__ == "__main__":
    print("yu-topy ~ a yu-ris to ren'py converter")
    print("--------------------------------------")
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', dest='input', type=str, required=True, help='Folder that contains the decrypted yu-ris files')
    parser.add_argument('-o', '--output', dest='output', type=str, required=True, help='Folder where to drop the generated ren\'py files')
    parser.add_argument('-d', '--debug', action='store_true', help='Creates debug files on the output folder')
    args = parser.parse_args()

    # Sanity check since the user might be insane
    if not os.path.exists(args.input):
        print("The folder you specified DOESN'T EXIST? WHAT!")
        print(f"Tried to access: {args.input}")
        quit()

    if not os.path.exists(args.output):
        print("The folder you specified DOESN'T EXIST? WHAT!")
        print(f"Tried to access: {args.output}")
        quit()
    
    yst_dict = read_extract_yst_list(args.input)
    for yst_dict_it in yst_dict:
        print(f"Converting {yst_dict_it['pred_file']}: {yst_dict_it['base_name']} - {yst_dict_it['pred_name']}")
        yst_file_path = os.path.join(args.input, yst_dict_it['pred_file'] )
        arg_list = decode_yst_file(yst_file_path + ".txt")

        renpy_base = encode_renpy_file(arg_list)
        renpy_file = os.path.join (args.output, yst_dict_it['pred_file'] + ".rpy")
        with open(renpy_file, 'w') as f:
            f.write(f"label yu_{yst_dict_it['pred_name']}:\n")
            f.write(renpy_base)
            f.write("\nreturn")

        if args.debug:
            debug_dir = os.path.join(args.output, "debug")
            if not os.path.exists(debug_dir):
                os.makedirs(debug_dir)
            debug_file = os.path.join(debug_dir, yst_dict_it['pred_file'] + "_arg_debug.txt")
            print(debug_file)
            with open(debug_file, 'w') as f:
                for single_arg in arg_list:
                    f.write(str(single_arg) + "\n")
