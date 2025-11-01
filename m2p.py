import re
import sys
import meshtastic
import meshtastic.tcp_interface
import time
import os
from pubsub import pub

logs = False
capcodes = []

def msg_transliterator(text):
    search = r"абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ@"
    replace = r"ABWGDEEVZIJKLMNOPRSTUFHC^[]XYX\@Qabwgdeevzijklmnoprstufhc~{}xyx|@qA"
    trans = str.maketrans(search, replace)
    return text.translate(trans)

def msg_transliterator_en_to_ru(text):
    replace = r"абцдефгхийклмнопярстувщхызАБЦДЕФГХИЙКЛМНОПЯРСТУВЩХЫЗ"
    search = r"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    trans = str.maketrans(search, replace)
    return text.translate(trans)

def msg_transliterator_ru_to_en(text):
    search = r"абцдеёфгхийклмнопярстувжщызъьэючшАБЦДЕЁФГХИЙКЛМНОПЯРСТУВЩЫЗЪЬЭЮЧШЖ"
    replace = r"abcdeefghijklmnopqrstuvxwyz''eu4wABCDEEFGHIJKLMNOPQRSTUVWYZ''EU4WX"
    trans = str.maketrans(search, replace)
    return text.translate(trans)

def msg_regex_cut(text):
    res = re.sub(r"[^a-zA-ZА-Яа-я0-9 =#@\n$%&*()_+';./:>?,<!ёЁ-]+", "*", text)
    return res

def send_msg_to_pgr(capcode, freq, mesg):
    runcheck_command = 'pidof pocsag >/dev/null && echo "run" || echo "nf"'
    rstream = os.popen(runcheck_command)
    routput = rstream.read()
    print(routput)
    while routput == "run":
        print("pocsag is running - sleeping for 8 sec and retry")
        time.sleep(8)
        nrstream = os.popen(runcheck_command)
        nroutput = nrstream.read()
        if nroutput == "nf":
            break
        else:
            continue
    else:
        print("pocsag is not running - executing")

    command = 'echo $(echo "'+ capcode +':'+ mesg +'") | sudo /home/pi/rpitx/pocsag -f "'+ freq +'" -b 3 -r 1200'
    print(command)
    stream = os.popen(command)
    output = stream.read()
    dell = output


def onConnect(interface, topic=pub.AUTO_TOPIC):
	if logs:
		print("Connected to the tcp interface.")

def onLost(interface, packet):
	if logs:
		print("Connection to the tcp interface has been lost")

def onUpdated(interface, node):
	if logs:
		print("Node has been updated.")

def onReceive(interface, packet):
	try:
		packet_decoded = packet.get('decoded')
		if packet_decoded:
			msg = packet_decoded.get('text')
		else:
			msg = False
		if msg:
			fromidsender = str(packet.get('fromId'))
			if fromidsender == "!FRIENDLYNODE1":
				fromidsender = "ProperName1"
			elif fromidsender == "!FRIENDLYNODE2":
				fromidsender = "ProperName2"
			elif fromidsender == "!FRIENDLYNODE3":
				fromidsender = "ProperName3"
			elif fromidsender == "!FRIENDLYNODE4":
				fromidsender = "ProperName4"
			#else:
				#do nothing
	
			message = fromidsender + ": " + msg + " (SNR: " + str(packet.get('rxSnr')) + ", RSSI: " + str(packet.get('rxRssi')) + ", hoplim: " + str(packet.get('hopLimit')) + ")"
			if logs:
				print("packet decoded")
				print(f"message: {message}")

			is_ping = msg.startswith("/ping")

			if is_ping and str(packet.get('toId')) == "!YOURNODEID":
				pong = "pong" + " [SNR: " + str(packet.get('rxSnr')) + ", RSSI: " + str(packet.get('rxRssi')) + ", hoplim: " + str(packet.get('hopLimit')) + "]"
				interface.sendText(pong, destinationId=str(packet.get('fromId')))
				if logs:
					print("ping received, sending pong back via mesh")
					print(pong)
				return

			print("sending to pocsag")
			print(message)
			prepared_msg = msg_regex_cut(message)
			rmsg = msg_transliterator_en_to_ru(prepared_msg)
			sendmsg = msg_transliterator(rmsg)
            #if (capcode == '777'):
            #    sendmsg = msg_transliterator_ru_to_en(prepared_msg)
			print(sendmsg)
			if str(packet.get('toId')) == "!YOURNODEID":
				send_msg_to_pgr("0000123", "157575000", sendmsg) # DIRECT MESSAGES WITH SOUND
			else:
				send_msg_to_pgr("0001123A", "157575000", sendmsg) # MAIL MUTED CAPCODE

	except Exception as ex:
		print (ex)
		pass

pub.subscribe(onReceive, "meshtastic.receive")
pub.subscribe(onConnect, "meshtastic.connection.established")
pub.subscribe(onLost, "meshtastic.connection.lost")
pub.subscribe(onUpdated, "meshtastic.node.updated")

try:
    interface = meshtastic.tcp_interface.TCPInterface(hostname="123.123.123.123") # your node IP address
    while True:
        time.sleep(1000)

except Exception as ex:
    print(f"Error: Could not connect to tcp interface: {ex}")
    sys.exit(1)
