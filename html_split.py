#!/usr/bin/python
import os
import re
import sys
from HTMLParser import HTMLParser

msgDatePatt = re.compile(r'\d+-\d+-\d+')

class MessageSaver:

	folder = './'

	dateStyle = ''.join([
		'border-bottom-width:1px;',
		'border-bottom-color:#8EC3EB;',
		'border-bottom-style:solid;',
		'color:#3568BB;',
		'font-weight:bold;',
		'height:24px;',
		'line-height:24px;',
		'padding-left:10px;',
		'margin-bottom:5px;'
	])

	def __init__(self):
		self.date = 'head'
		self.list = [ ]
		self.head = [ ]
		self.saved = { }

	def get_date(self, message):
		match = msgDatePatt.search(message)
		if match:
			return match.group(0)
		return ''

	def add_message(self, message):
		if message.find(self.dateStyle) >= 0:
			if len(self.list):
				if self.date == 'head':
					self.head = self.list[:]
				else:
					self.save_message()
			self.date = self.get_date(message)
			self.list = [ ]

		self.list.append(message)

	def save_message(self):
		if self.date and len(self.list):
			print '# saving %s (%d messages)' % (self.date, len(self.list))

			content = '\n'.join(self.head[:] + self.list)
			path = os.path.join(self.folder, '%s.html.part' % self.date)
			self.saved[self.date] = path

			fout = open(path, 'w')
			fout.write(content.encode('utf8'))
			fout.close()

	def finish(self, header, footer):
		self.save_message()

		print '# adding header and footer'
		for date, path in self.saved.iteritems():
			with open(path, 'r') as fin:
				fout = open(os.path.join(self.folder, '%s.html' % date), 'w')
				fout.write(header)
				for line in fin.readlines():
					fout.write(line)
				fout.write(footer)
				fout.close()
			os.remove(path)

class MessageParser(HTMLParser):

	self_closing_tags = ['br', 'img']
	html_message_path = 'html/body/table/tr'

	def __init__(self):
		HTMLParser.__init__(self)
		self.body = ''
		self.path = [ ]
		self.messages = MessageSaver()
		self.header = ''
		self.footer = ''

	def handle_starttag(self, tag, attrs):
		attrs = ' ' + ' '.join('%s="%s"' % (k, v) for k, v in attrs) if attrs else ''
		if tag not in self.self_closing_tags:

			if '/'.join(self.path) + '/' + tag == self.html_message_path:
				if not self.header:
					self.header = self.body
				self.body = ''

			self.path.append(tag)
			self.body += '<%s%s>' % (tag, attrs)

		else:
			self.body += '<%s%s />' % (tag, attrs)

	def handle_endtag(self, tag):
		if tag not in self.self_closing_tags:
			self.path.pop()
			self.body += '</%s>' % tag

			if '/'.join(self.path) + '/' + tag == self.html_message_path:
				self.messages.add_message(self.body)
				self.body = ''

	def handle_data(self, data):
		self.body += data

	def finish(self):
		self.footer = self.body
		self.messages.finish(self.header, self.footer)
		print '# done'
		print

if __name__ == '__main__':
	if (len(sys.argv) > 1):
		MessageSaver.folder = sys.argv[1]
	else:
		print('Split html file by date converted by mht_unpack.py')
		print('  Usage: html_split.py <.>')
		sys.exit(1)

	parser = MessageParser()
	path = os.path.join(MessageSaver.folder, 'index.html')

	print '# splitting...'
	with open(path, 'r') as fin:
		for line in fin.readlines():
			parser.feed(line.decode('utf8'))

	parser.finish()
