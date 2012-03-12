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


import imaplib, os, getpass, re

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
	Email= read.splitlines(True)		
		
	count = [1,1,1,1,1]

	for s in range(0,len(Email)):
		line = Email[s]
		
		if line[0:5] == 'Date:' :
			Date = line [6:len(line)]
			count[0]=0;
		elif line[0:5] == 'From:' :
			From = line [6:len(line)]
			count[1] = 0
		elif line[0:3] == 'To:' :
			To = line [4:len(line)]
			count[2] = 0
		elif line[0:8] == 'Subject:' :
			Subject = line [9:len(line)]
			count[3] = 0
		elif line[0:11] == 'Message-ID:' or line[0:11] == 'Message-Id:'  :
			ID = line [12:len(line)]
			count[4] = 0
		if count == [0,0,0,0,0]:
			break;

	with open("Data","a") as myfile:
		myfile.write(fname+ "\t" + To + "\t" + From + "\t" + Date + "\t" + Subject + "\t" + ID + "\n")

filere = re.compile(r"(\d+).eml$")
def UIDFromFilename(fname):
	m = filere.match(fname)
	if m:
		return int(m.group(1))


svr = imaplib.IMAP4_SSL('imap.gmail.com')
#svr.login(raw_input("Gmail address: "), getpass.getpass("Gmail password: "))
svr.login("shyamalruparel1991@gmail.com","tmivuwpieoiokaoq") 

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
	print "Downloading %d/%d (UID: %s)" % (i, count, uid)
	downloadMessage(i, uid)


svr.close()
svr.logout()
