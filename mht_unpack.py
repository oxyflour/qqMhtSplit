#!/usr/bin/python
import re
import os
import sys
import base64

def enum(*sequential, **named):
	enums = dict(zip(sequential, range(len(sequential))), **named)
	return type('Enum', (), enums)

States = enum(
	'PARSE_BOUNDARY',
	'GET_BOUNDARY',
	'GET_FILEINFO',
	'GET_FILECONTENT')

boundaryPatt = re.compile(r'boundary="(.*)"', re.I)
fileNamePatt = re.compile(r'^Content-Location:(.*)', re.I)
fileEncPatt = re.compile(r'^Content-Transfer-Encoding:(.*)', re.I)

class FileContent:

	folder = './'

	def __init__(self):
		self.path = 'index.html'
		self.encoding = ''
		self.content = [ ]

	def save(self):
		if self.path and len(self.content):
			print '# writing to file %s (%d lines)' % (self.path, len(self.content))

			path = os.path.join(self.folder, self.path)
			folder, name = os.path.split(path)
			if not os.path.exists(folder):
				os.makedirs(folder)

			if self.encoding == 'base64':
				content = base64.b64decode(''.join(self.content))
				mode = 'wb'
			else:
				content = '\n'.join(self.content)
				mode = 'w'

			fout = open(path, mode)
			fout.write(content)
			fout.close()

		else:
			print '# nothing to write!'


if __name__ == '__main__':
	if (len(sys.argv) > 1):
		fileName = sys.argv[1]
		if (len(sys.argv) > 2):
			FileContent.folder = sys.argv[2]
	else:
		print('Unpack .mht file exported by Tencent QQ')
		print('  Usage: mht_unpack.py <file.mht> [.]')
		sys.exit(1)

	with open(fileName, 'r') as fin:
		state = States.PARSE_BOUNDARY

		boundary = ''
		fout = FileContent()

		print '# unpacking...'
		for line in fin.readlines():
			line = line.strip()

			if state == States.PARSE_BOUNDARY:
				match = boundaryPatt.search(line)
				if match:
					boundary = '--' + match.group(1)
					print '# got boundary: ' + boundary
					state = States.GET_BOUNDARY

			elif state == States.GET_BOUNDARY:
				if line == boundary:
					fout = FileContent()
					state = States.GET_FILEINFO

			elif state == States.GET_FILEINFO:
				if line:
					match = fileNamePatt.search(line)
					if match:
						fout.path = match.group(1).strip()

					match = fileEncPatt.search(line)
					if match:
						fout.encoding = match.group(1).strip()

				else:
					state = States.GET_FILECONTENT

			elif state == States.GET_FILECONTENT:
				if line == boundary:
					fout.save()
					fout = FileContent()
					state = States.GET_FILEINFO

				elif line == boundary + '--':
					fout.save()
					print '# done'
					print
					break

				else:
					fout.content.append(line)



