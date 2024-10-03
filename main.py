#!/bin/env python3
import os
# import shutil
import argparse
from ytp_parser import *
from func import *

if __name__ == "__main__":
    print("YTP_NEXT v4.2.0")
    print("---------------")
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', dest='input', type=str, required=True, help='Folder that contains the decrypted yu-ris files')
    # parser.add_argument('-o', '--output', dest='output', type=str, required=True, help='Folder where to drop the generated ren\'py files')
    #parser.add_argument('-d', '--debug', action='store_true', help='Let the program yap about what it\'s doing behind the scenes')
    args = parser.parse_args()

    # Sanity check since the user might be insane
    if not os.path.exists(args.input):
        print("The folder you specified DOESN'T EXIST? WHAT!")
        print(f"Tried to access: {args.input}")
        quit()

    # if not os.path.exists(args.output):
    #     os.makedirs(args.output)

    #yst_list_decode = readExtractYstlist_new(args.input)
    #ysl_decode = readExtractYsl_new(args.input)
    YTSB = readExtractYSCM(args.input)
    print(prettyDict(YTSB))
    #yscfg_decode = readExtractYscfg(args.input)
    #yst_decode = readExtractYst(args.input)
    #ysc_decode = readExtractYsc(args.input)
    
    
    
    #read_extract_ystlist(args.input)
    #ysl_decode = read_extract_ysl(args.input)
    #print(search_value(108, 'scriptindex', ysl_decode['labels']))
    
    #read_extract_yst(f"{args.input}/yst00108.ybn")
    
    # print([item for item in yst_list_decode['scripts'] if item['index'] == 100])
    # print([item for item in ysl_decode['labels'] if item['scriptindex'] == 100])

    # print(search_value(115, 'index', yst_list_decode['scripts']))
    # print(search_value(115, 'scriptindex', ysl_decode['labels']))
    
    # print([element for element in yst_list_decode['scripts'] if ['index'] == 114])
    # search(index, yst_list_decode['scripts'])

    # yst_paths = read_extract_yst_list(args.input)

    # for yst_num, yst_path in enumerate(yst_paths):
    #     file_name = yst_path.split("\\")[-1]
    #     file_path = yst_path.split("\\")[:-1]

    #     if "userscript" in file_path:
    #         og_file = os.path.join(args.input, "yst" + str(yst_num).zfill(5) + ".txt")
    #         print(f"Found: {og_file} - {file_name}")

    #         decode_yst_file(og_file)
            # shutil.copy(og_file, args.output)