
def decode_yst_file(file_name):
    with open(file_name, 'r', encoding='utf-16-le') as f:
        yst_lines = f.readlines()

    # print(yst_lines)
    