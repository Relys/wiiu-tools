from rplfile import *
import io
import copy
from elftools.elf.elffile import ELFFile

with open("000012db.app", "rb") as rplstream, open("out.elf", "wb") as outstream:
	rpl = rplstream.read()
	rplstream.seek(0)
	a = RPLFile(rplstream)
	rplstream = io.BytesIO(rpl)
	headerbytes = bytearray(rplstream.read(a.header["e_ehsize"]))
	headerbytes[0x7] = 0 # sysV
	headerbytes[0x8] = 0 # abi v0
	headerbytes[0x10] = 0
	headerbytes[0x11] = 3 # dyn

	outstream.write(headerbytes)
	print(a)
	print(a.header)
	b = 0
	crushed_data = io.BytesIO()
	crushed_indexes = []
	post_headers = a.header["e_shoff"] + (a.header["e_shentsize"] * a.header["e_shnum"])
	if (a.structs.Elf_Shdr.sizeof() != a.header["e_shentsize"]):
		print("FAIL", a.structs.Elf_Shdr.sizeof(), a.header["e_shentsize"])
	for i in a.iter_sections():
		#outstream.seek(a.header["e_shentsize"] * b + a.header["e_shoff"])
		#outstream.write(
		#print(i)
		#print(i.header)
		#print(i.name)
		#with open("section" + str(b) + ".bin", "wb") as outfile:
		#	outfile.write(i.data())
		data = i.data()
		crushed_indexes.append(crushed_data.tell())
		crushed_data.write(data)
		outstream.seek(a.header["e_shoff"] + (a.header["e_shentsize"] * b))
		newheader = copy.copy(i.header)
		newheader["sh_size"] = len(data)
		newheader["sh_offset"] = crushed_indexes[b] + post_headers
		newheader["sh_flags"] &= ~0x08000000
		if newheader["sh_type"] == "SHT_SYMTAB":
			newheader["sh_info"] = newheader["sh_info"] // newheader["sh_entsize"]
		outstream.write(a.structs.Elf_Shdr.build(newheader))
		b = b + 1
	outstream.write(crushed_data.getvalue())

with open("out.elf", "rb") as instream:
	a = ELFFile(instream)
	print(a.header)
	for i in a.iter_sections():
		print(i.name)
		print(i.header)