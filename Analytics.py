# Copyright (c) 2012 by Shyamal Ruparel - Burst Development
#
# GNU General Public Licence (GPL)
# 
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA  02111-1307  USA


import imaplib, os, getpass, re, email
from email.parser import Parser
_re_word_boundaries = re.compile(r'\b')

uidre = re.compile(r"\d+\s+\(UID (\d+)\)$")
def getUIDForMessage(n):
	resp, lst = svr.fetch(n, 'UID')
	m = uidre.match(lst[0])
	if not m:
		raise Exception("Internal error parsing UID response: %s %s.  Please try again" % (resp, lst))
	return m.group(1)
	

def downloadMessage(n, fname):
	resp, lst = svr.fetch(n, '(RFC822)')
	if resp!='OK':
		raise Exception("Bad response: %s %s" % (resp, lst))
	read = lst[0][1]
	headers = Parser().parsestr(read)
	msg = email.message_from_string(read)





	with open("Data","a") as myfile:
		try:
				myfile.write(fname +  "\n")
				myfile.write('To: %s' % headers['to'] + "\n")
				myfile.write('cc: %s' % headers['cc'] + "\n")
				myfile.write('bcc: %s' % headers['bcc'] + "\n")
				myfile.write('From: %s' % headers['from'] + "\n")
				myfile.write('Subject: %s' % headers['subject'] + "\n")
				myfile.write('Date: %s' % headers['date'] + "\n")
				myfile.write('Word Count: %s' % num_words(str(msg)) + "\n")
				myfile.write("\n")		
			
#			myfile.write(fname+ "\n" + "\tTo: " +  headers['to'] + "\n" + "\tFrom: " + headers['from'] + "\n" + "\tDate: " + headers['date'] + "\n" + "\tSubject: " +headers['subject'])
#			myfile.write(fname+ "\n" + "\tcc: " +  headers['cc'] + "\n" + "\tbcc: " + headers['bcc'] + "\n" + "\tword count: " + num_words(str(msg)))
#
		except:
			print (fname + ' print failed.')

filere = re.compile(r"(\d+).eml$")

def num_words(line):
    return sum(1 for word in _re_word_boundaries.finditer(line)) >> 1


def UIDFromFilename(fname):
	m = filere.match(fname)
	if m:
		return int(m.group(1))


svr = imaplib.IMAP4_SSL('imap.gmail.com')

#svr.login(raw_input("Gmail address: "), getpass.getpass("Gmail password: "))

try:
	Login  = open('pass.txt','r')
except:
	print "pass.txt file not found."

Address = Login.readline().rstrip('\n')
Password = Login.readline().rstrip('\n')

svr.login( Address, Password )

resp, [countstr] = svr.select("[Gmail]/All Mail", True)
count = int(countstr)

lastdownloaded = max(UIDFromFilename(f) for f in os.listdir('.'))


# A simple binary search to see where we left off
gotten, ungotten = 0, count+1
while ungotten-gotten>1:
	attempt = (gotten+ungotten)/2
	uid = getUIDForMessage(attempt)
	if int(uid)<=lastdownloaded:
		print "Finding starting point: %d/%d (UID: %s) too low" % (attempt, count, uid)
		gotten = attempt
	else:
		print "Finding starting point: %d/%d (UID: %s) too high" % (attempt, count, uid)
		ungotten = attempt


# The download loop
for i in range(ungotten, count+1):
	uid = getUIDForMessage(i)
	print "Processing %d/%d (UID: %s)" % (i, count, uid)
	downloadMessage(i, uid)


svr.close()
svr.logout()
