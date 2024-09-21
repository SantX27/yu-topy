import struct

format_header = '4s2i'
size = format_header
with open('/home/kanae/yu-ris_0474_008/test/data/ysbin/yst_list.ybn', 'rb') as fp:
    file = fp.read()
header = file[:12]

#prints the fucking header
header_str, version, numscript = struct.unpack(format_header, header)
print(header_str, version, numscript)

start = 12
stop = 20
script = file[start:stop]
format_script = '2i'
index, len = struct.unpack(format_script, script)
print(struct.unpack(format_script, script))

i = 0
while i < numscript:
    start = stop
    stop = stop + len
    script_path = file[start:stop+28]
    format_path = f'{len}s2d5i'
    print(struct.unpack(format_path, script_path))
    i += 1




