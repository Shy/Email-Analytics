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
	temp = lst[0][1]
	Email= temp.splitlines(True)		
	count = 5	
	cd,cf,ct,cs,ci = [1,1,1,1,1]

	for s in range(0,len(Email)):
		temp = Email[s]
		if temp[0:5] == 'Date:' :
			Date = temp [6:len(temp)]
			count = count - cd; 
			cd = 0;		
		elif temp[0:5] == 'From:' :
			From = temp [6:len(temp)]
			count = count - cf
			cf = 0
		elif temp[0:3] == 'To:' :
			To = temp [4:len(temp)]
			count = count - ct
			ct = 0
		elif temp[0:8] == 'Subject:' :
			Subject = temp [9:len(temp)]
			count = count - cs
			cs = 0
		elif temp[0:11] == 'Message-ID:' or temp[0:11] == 'Message-Id:'  :
			ID = temp [12:len(temp)]
			count = count - ci
			ci = 0
		if count == 0:
			break;

	with open("Data","a") as myfile:
		myfile.write(To + "\t" + From + "\t" + Date + "\t" + Subject + "\t" + ID + "\n")

filere = re.compile(r"(\d+).eml$")
def UIDFromFilename(fname):
	m = filere.match(fname)
	if m:
		return int(m.group(1))


svr = imaplib.IMAP4_SSL('imap.gmail.com')
svr.login(raw_input("Gmail address: "), getpass.getpass("Gmail password: "))

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
	downloadMessage(i, uid+'.eml')


svr.close()
svr.logout()
