from Crypto.Cipher import AES
import md5,thread,time,socket,random,base64
personalkey = "0000"
inputMessage = ">"
thisHost = ""
thisPort = ""
mainServerHost = ""
mainServerPort = 0
messages = []
clientHosts = []
clientPorts = []
settings = []
thisHostSet = 0
thisPortSet = 0
settingsfilename = "settings.dat"
errors = 1
quitting = 0
def askForHost():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((getMainserverHost(), int(getMainserverPort())))
	setThisHost(str(s.getsockname()[0]))
	s.close()
def loadSettings(filename):
	global settings
	for line in open(settingsfilename,"r").readlines():
		line = line.split(":")
		while line[0][-1:] == " ":
			line[0] = line[0][:-1]
		while line[1][:1] == " ":
			line[1] = line[1][1:]
		if line[1][-1:] == "\n":
			line[1] = line[1][:-1]
		settings.append(line)
def getSetting(settingname):
	for setting in settings:
		if setting[0] == settingname:
			debugger("Loaded setting '"+settingname+"'",1)
			return setting[1]
	debugger("Couldn't load setting '"+settingname+"'",-1)
	return ""
def ttquit():
	global quitting
	quitting = 1
def getMainserverHost():
	global mainServerHost
	if mainServerHost == "":
		mainServerHost = getSetting("mainserverhost")
	return socket.gethostbyname(mainServerHost)
def getMainserverPort():
	global mainServerPort
	if mainServerPort == 0:
		mainServerPort = int(getSetting("mainserverport"))
	return mainServerPort
def getThisHost():
	global thisHost
	if thisHost == "":
		thisHost = getSetting("thishost")
	return thisHost
def getThisPort(override):
	global thisPort,thisPortSet
	if thisPort == "":
		thisPort = getSetting("thisport")
	if override != 1 and thisPortSet == 0:
		return -1
	else:
		return thisPort
def setThisHost(hostval):
	global thisHost,thisHostSet
	thisHost = hostval
	thisHostSet = 1
def setThisPort(portVal):
	global thisPort,thisPortSet
	thisPort = str(portVal)
	thisPortSet = 1
def debugger(errormessage,errorlevel):
	global errors
	if errorlevel <= errors:
		addMessage("@"+errormessage)
	drawMessages()
	if errorlevel < 0:
		ttquit()
def generatePersonalKey():
	global personalkey
	personalkey = hashCal(str(random.random()))
def getPersonalKey():
	global personalkey
	return personalkey
def hashCal(data):
	return md5.new(data).hexdigest()+md5.new(data).hexdigest()+md5.new(md5.new(data).hexdigest()).hexdigest()
def generateID(data):
	id = data
	for i in range(0,1000):
		newpass = id
		for i in range(0,100):
			newpass=newpass+hashCal(newpass)
		id = md5.new(newpass).hexdigest()
	return id
def stringToHosts(string):
	global clientHosts,clientPorts,thisHost
	clientHosts = []
	clientPorts = []
	string = string.split("|")
	if len(string) > 0:
		for host in string:
			newhost = host
			newhost = newhost.split(":")
			if len(newhost) == 2:
				hostname = newhost[0]
				hostport = newhost[1]
				if str(getThisHost) != str(hostname) or int(getThisPort(0)) != int(hostport):
					clientHosts.append(hostname)
					clientPorts.append(hostport)
def showAllClients():
	global clientHosts,clientPorts
	toReturn = ""
	for i in range(len(clientHosts)):
		toReturn += clientHosts[i]+":"+clientPorts[i]+"|"
	if len(toReturn) > 0:
		toReturn = toReturn[:-1]
	return toReturn
def refreshClients(id):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((getMainserverHost(), int(getMainserverPort())))
	s.send("0001"+id)
	data = s.recv(4096)
	s.close()
	stringToHosts(data[4:])
def createMessage(password, message):
	message = "-"+message
	if len(password) > 16:
		password = password[:16]
	while len(password) < 16:
		password += "0"
	iv = hashCal(password)
	iv = iv[:16]
	cryption = AES.new(password,AES.MODE_CBC,iv)
	while len(message) % 16 != 0:
		message += "|"
	message = cryption.encrypt(message)
	message = base64.b64encode(message)
	return message
def addMessage(message):
	global messages
	messages.append(message)
def showMessage(password, message):
	global messages
	message = base64.b64decode(message)
	if len(password) > 16:
		password = password[:16]
	while len(password) < 16:
		password += "0"
	iv = hashCal(password)
	iv = iv[:16]
	cryption = AES.new(password,AES.MODE_CBC,iv)
	message = cryption.decrypt(message)
	while message[-1:] == "|":
		message = message[:-1]
	addMessage(message)
	drawMessages()
def drawMessages():
	global inputMessage,messages
	for i in range(25-len(messages)):
		print("")
	for i in range(len(messages)):
		print(messages[i])
	print(inputMessage)
def sendMessage(clienthost,clientport,password,userinput):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(1)
	try:
		s.connect((str(clienthost), int(clientport)))
	except Exception:
		pass
	else:
		try:
			s.send("0002"+createMessage(password, userinput))
		except Exception:
			pass
		else:
			try:
				data = s.recv(4096)
			except Exception:
				pass
	s.close()
def listener(password,id):
	global thisHost,thisHostSet
	while thisHostSet == 0:
		time.sleep(1)
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	passv = 0
	portv = int(getThisPort(1))
	while passv == 0:
		try:
			s.bind(("", portv))
		except Exception:
			portv += 1
		else:
			passv = 1
	setThisPort(portv)
	while 1:
		s.listen(1)
		conn, addr = s.accept()
		data = conn.recv(4096)
		if data == "0000":
			conn.sendall("0001")
		elif data[:4] == "0001":
			if data[4:] == str(getPersonalKey()):
				conn.sendall("0001")
			else:
				conn.sendall("0000")
		elif data[:4] == "0002":
			showMessage(password,data[4:])
		else:
			conn.sendall("0000")
		conn.close()
def sender(password,id):
	generatePersonalKey()
	global clientHosts,clientPorts,inputMessage
	if getThisHost() == "0.0.0.0":
		askForHost()
	debugger("Logged in as "+thisHost,1)
	while getThisPort(0) == -1:
		time.sleep(1)
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	debugger("Connecting to mainserver...",1)
	s.connect((getMainserverHost(), int(getMainserverPort())))
	debugger("Sending information to mainserver from "+getThisHost()+"...",1)
	s.send("0000"+id+"|"+getThisHost()+"|"+getThisPort(0)+"|"+str(getPersonalKey()))
	debugger("Waiting for information from mainserver",1)
	data = s.recv(4096)
	debugger("Got reply: "+data,1)
	s.close()
	if data == "0000":
		debugger("Couldn't connect to Mainserver: "+getMainserverHost(),0)
	if data == "0001":
		while 1:
			drawMessages()
			userInput = raw_input("")
			if userInput[:1] == "/":
				if userInput[1:] == "showClients":
					addMessage(showAllClients())
				elif userInput[1:] == "refreshClients":
					refreshClients(id)
				elif userInput[1:] == "help":
					addMessage("---HELP---")
					addMessage("---Enter a message to send it")
					addMessage("---/showClients show's clients of same chat ID")
					addMessage("---/refreshClients refreshes client list")
				elif userInput[1:] == "quit":
					ttquit()
				else:
					addMessage("That is not a valid command")
			else:
				if len(clientHosts) > 0:
					for i in range(len(clientHosts)):
						thread.start_new_thread(sendMessage,(clientHosts[i],clientPorts[i],password,userInput))
					else: messages.append(":"+userInput)
				else:
					debugger("No other users in group",0)
def clientrefresher(password,id):
	while 1:
		refreshClients(id)
		time.sleep(120)
def main():
	print("Enter chat password:")
	password = raw_input(">")
	print("Generating chat ID...")
	id = generateID(password)
	print("Generated chat ID: "+id)
	thread.start_new_thread(listener,(password,id))
	thread.start_new_thread(sender,(password,id))
	thread.start_new_thread(clientrefresher,(password,id))
loadSettings(settingsfilename)
main()
while quitting == 0:
	pass
