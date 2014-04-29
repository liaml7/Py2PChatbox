import socket,time,thread;
mainservers = [];
clientIDs = [];
clientHosts = [];
clientPorts = [];
HOST = "";
PORT = 31;
def keepalive(null1, null2):
	global HOST,PORT,clientIDs,clientHosts,clientPorts,mainservers;
	while 1:
		popped = 0;
		if len(clientHosts) > 0:
			for i in range(len(clientHosts)):
				s = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
				s.settimeout(3);
				try:
					s.connect((str(clientHosts[i]), int(clientPorts[i])));
				except Exception:
					data = "0000";
				else:
					try:
						s.send("0000");
					except Exception:
						data = "0000";
					else:
						try:
							data = s.recv(4096);
						except Exception:
							data = "0000";
				s.close();
				if data == "0001":
					print(clientIDs[i]+":"+clientHosts[i]+":"+clientPorts[i]);
				elif popped == 0:
					popped = 1;
					clientIDs.pop(i);
					clientHosts.pop(i);
					clientPorts.pop(i);
		time.sleep(50);
def listener(null1, null2):
	global HOST,PORT,clientIDs,clientHosts,clientPorts,mainservers;
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
	s.bind((HOST, PORT));
	while 1:
		s.listen(1);
		conn, addr = s.accept();
		print("Connected by",addr);
		data = conn.recv(4096);
		message = data[4:];
		message = message.split("|");
		#0000ADD CLIENT WITH SPECIFIED ID|HOSTNAME|PORT
		#0001FIND CLIENTHOST:CLIENTPORT WITH SPECIFIED ID
		if data[:4] == "0000":
			if len(message) == 4:
				print("New user joining from "+message[1]+":"+message[2]);
				connectordata = "";
				try:
					connector = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
					print("Sending test connection to user");
					connector.connect((message[1], int(message[2])));
					print("Connected, trying to send test data: "+message[3]);
					connector.send("0001"+message[3]);
					print("Data sent");
					connectordata = connector.recv(4096);
					print("Data received "+connectordata);
				except Exception:
					print("Test connection failed!");
					connectordata = "";
					conn.sendall("0000");
				connector.close();
				if connectordata == "0001":
					print("Connection accepted");
					if message[1] in clientHosts and message[2] in clientPorts:
						print("User already connected!");
						conn.sendall("0000");
					else:
						print("Adding user to network");
						clientIDs.append(message[0]);
						clientHosts.append(message[1]);
						clientPorts.append(message[2]);
						conn.sendall("0001");
				elif connectordata == "0000":
					conn.sendall("0000");
					print("Server rejected data");
				else: conn.sendall("0001");
			else: conn.sendall("0000");
		elif data[:4] == "0001":
			stringSend = "0001";
			if len(clientIDs)>0:
				for x in range(len(clientIDs)):
					if clientIDs[x] == message[0]:
						stringSend += clientHosts[x]+":"+clientPorts[x]+"|";
			if len(stringSend) > 4:
				stringSend = stringSend[:-1];
			print("User requested users from chat: "+message[0]+", sending reply "+stringSend);
			conn.sendall(stringSend);
		elif data[:4] == "0002":
			conn.sendall("0001"+addr[0])
		else: conn.sendall("0000");
		conn.close();
thread.start_new_thread(keepalive,(0,"NULLVALUE"));
thread.start_new_thread(listener,(0,"NULLVALUE"));
while 1:
	pass;
