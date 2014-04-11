
class bootstrapping:
	def __init__(self):
		hostfile = "/etc/hosts"
		myfile = open(hostfile,"r")
		lines = myfile.readlines()
		myfile.close()
		myfile = open(hostfile,"w")
		for line in lines:
			if line.find('bootdns') is -1:
				myfile.write(line)

		myfile.close()
		with open(hostfile, "a") as myfile:
			ipaddr = '127.0.0.1'
			dnsname = 'bootdns'
			myfile.write(ipaddr + " " + dnsname + " " + dnsname)
		myfile.close()

