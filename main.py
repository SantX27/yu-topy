#!/bin/env python3
import os
# import shutil
import argparse
from ytp_parser import *
from expr_parser import *
from func import *

if __name__ == "__main__":
    print("YTP_NEXT v4.2.0")
    print("---------------")
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', dest='input', type=str, required=True, help='Folder that contains the decrypted yu-ris files')
    parser.add_argument('-o', '--output', dest='output', type=str, required=True, help='Folder where to drop the generated ren\'py files')
    #parser.add_argument('-d', '--debug', action='store_true', help='Let the program yap about what it\'s doing behind the scenes')
    args = parser.parse_args()

    # Sanity check since the user might be insane
    if not os.path.exists(args.input):
        print("The folder you specified DOESN'T EXIST? WHAT!")
        print(f"Tried to access: {args.input}")
        quit()

    YSCF = readExtractYSCF(args.input)
    YSTL = readExtractYSTL(args.input, YSCF['caption'])
    YSLB = readExtractYSLB(args.input)
    YSVR = readExtractYSVR(args.input)
    YSCM = readExtractYSCM(args.input)

    with open(os.path.join(args.output, "yst_list.ytp"), 'w') as f:
        f.write(prettyDict(YSTL))

    with open(os.path.join(args.output,"ysl.ytp"), 'w') as f:
        f.write(prettyDict(YSLB))

    with open(os.path.join(args.output, "ysv.ytp"), 'w') as f:
        f.write(prettyDict(YSVR))

    with open(os.path.join(args.output, "yscfg.ytp"), 'w') as f:
        f.write(prettyDict(YSCF))

    with open(os.path.join(args.output, "ysc.ytp"), 'w') as f:
        f.write(prettyDict(YSCM))

    # Read all yst00*.ybn files, excluding eris
    for num_script, script in enumerate(YSTL['scripts']):
        if "eris" in YSTL['scripts'][num_script]['path']:
            print("Eris file, skipping...")
            pass
        else:
            yst_index_name = "yst" + str(script['index']).zfill(5) + ".ybn"
            
            YSTB = readExtractYSTB(os.path.join(args.input, yst_index_name))
            
            with open(os.path.join(args.output, yst_index_name + ".ytp"), 'w') as f:
                f.write(prettyDict(YSTB))
            yap(f"Wrote {os.path.join(args.output, yst_index_name + ".ytp")}", True)

            try:
                if YSTB != 1:
                    parsed = instructionParser(script['index'], YSTB, YSCM, YSTL, YSVR, YSLB)
                        
                    yurisPrint(parsed)
                    with open(os.path.join(args.output, yst_index_name + ".ytp.parsed"), 'w') as f:
                        #f.write(prettyDict(parsed))
                        f.write(yurisPrint(parsed))
                    yap(f"Wrote {os.path.join(args.output, yst_index_name + ".ytp.parsed")}", True)

            except Exception as e:
                print(e)
                pass

    # print(prettyDict(instructionParser(YSTB, YSCM, YSTL)))
            
    

    
    
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