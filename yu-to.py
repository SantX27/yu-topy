import re

# READ REAL FILE LIST
with open ('yst_list.ybn', 'r', encoding='cp932', errors='ignore') as f:
    list_lines = f.readlines()

yst_dict = []
yst_index = 0
for single_list in list_lines:
    single_list
    og_names = re.findall(r'(?:data)(.*?)(?:.yst|.txt)', single_list)
    for og_name in og_names:
        if "userscript" in og_name:
            base_name = og_name.split("\\", 3)[3]
            #print(f'yst{str(yst_index).zfill(5)}: {base_name}')
            yst_dict.append({
                'pred_file': f'yst{str(yst_index).zfill(5)}',
                'base_name': base_name
            })

            #euphoria specific filenames
            
        yst_index += 1
print(yst_dict)

with open('yst00140.txt', 'r', encoding='utf-16-le') as f:
#with open('ystslim.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

#print(lines)
# DECODER
arg_list = []
for num_line, line in enumerate(lines):
    if "inst_arg" in line:
        #print(line)
        inst_arg = re.findall(r'\:([^:]*)\,', line)[0] #regex match :"string",
        num_args = int(re.findall(r'\:([^,[]*)\]', line)[0], 16) - 1
        # arg_type = "unkn"
        # if inst_arg == "0x1D": arg_type = "eris"
        # if inst_arg == "0x5F": arg_type = "text"
        # if inst_arg == "0x40": arg_type = "stop"
        # if inst_arg == "0x1C": arg_type = "jump"
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
            'num_args': num_args,
            'arg_type': arg_type,
            }
    if "rsc_data" in line:
        try:
            #rsc_arg = re.findall(r'\"([^:]*)\"', line)[0]
            rsc_arg = re.findall(r'"([^"]*)', line)[0]
        except IndexError:
            try:
                rsc_arg = re.findall(r'\[([^:]*)\]', line)[1]
            except IndexError:
                rsc_arg = re.findall(r"\'([^:]*)\'", line)[0]
        rsc_idx = re.findall(r'rsc_data\[(\d)\]', line)[0]
        if arg_type == "text":
            name, _, quote = rsc_arg.partition(':')
            if quote:
                quote = quote.strip().strip('“').strip('”')
                name = name.replace('／', '/')
                arg_dic['name'] = name
                arg_dic['quote'] = quote
            else:
                arg_dic['quote'] = name
        elif arg_type == "stop":
            continue 
        elif arg_type == "eris":
            try:
                if rsc_idx == "0":
                    arg_dic['func_arg'].append(rsc_arg)
                else:
                    arg_dic['func_arg'][-1] = [arg_dic['func_arg'][-1], rsc_arg] 
            except KeyError:
                arg_dic['func_name'] = rsc_arg
                arg_dic['func_arg'] = []

        else:
            try:
                arg_dic['func_arg'].append(rsc_arg)
            except KeyError:
                arg_dic['func_arg'] = []
                arg_dic['func_arg'].append(rsc_arg)

    if line == '\n':
        arg_list.append(arg_dic)

# ENCODER
# for single_arg in arg_list:
#      print(single_arg)
# exit()

init_list = []
script_list = []
for single_arg in arg_list:
    #TODO
    # Posizionamento sprite
    # * Base
    # - Posizionamento preciso
    # - Zoom personaggio
    # Musica
    # * Base
    # - Canali audio separati
    # - Audio continua fino a prossimo audio 
    # Scelte di scenario
    # Migliorare transizioni
    # Autogenerare intero progetto
    #
    if single_arg['arg_type'] == "text":
        try:
            script_list.append(f"\"{single_arg['name']}\" \"{single_arg['quote']}\"")
        except KeyError:
            script_list.append(f"\"{single_arg['quote']}\"")

    if single_arg['arg_type'] == "eris" and single_arg['func_name'] == "MAC.BG":
        if not any(single_arg['func_arg'][0] in string for string in init_list):
            init_list.append(f"image {single_arg['func_arg'][0]} = im.Scale(\"images/bg/{single_arg['func_arg'][0]}.png\", 1920, 1080)")
        script_list.append(f"scene {single_arg['func_arg'][0]}")

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
        if "show" in script_list[-1]:
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
            case "0B ":
                sound_type = "sound"
                sound_name = single_arg['func_arg'][1].lower() + ".ogg"
                sound_path = "audio/se/" + sound_name
        if sound_type == "voice":
            script_list.append(f"{sound_type} \"{sound_path}\"")
            script_list.append("voice sustain")
        else:
            script_list.append(f"play {sound_type} \"{sound_path}\"")
        # print(sound_path)

init_list.sort()
# print('\n'.join(init_list))
# print()
# print('\n'.join(script_list))

# for single_arg in arg_list:
#     if single_arg['arg_type'] == "eris" and single_arg['func_name'] == "es.SND":
#         print(single_arg)
    # if single_arg['arg_type'] == "text":
    #     input("Press Enter to continue...")

# for single_arg in arg_list:
#     print(single_arg)