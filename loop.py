# https://www.cisco.com/c/en/us/td/docs/ios/12_2/configfun/command/reference/ffun_r/frf019.pdf
import sys, tty, termios, os, paramiko, datetime
from os import listdir
from os.path import isfile, join
# from RPLCD.i2c import CharLCD

fd = sys.stdin.fileno()
old_settings = termios.tcgetattr(fd)
mypath = 'contacts/'

# modes: main menu, contact menu, message
mode = 'main menu';

def init():
	initialize_screen()
	main_menu()

	global mode

	# a = []
	# # escape
	# if '\x1b' == ch:
	# 	print 'output:'
	# 	print ''.join(a)
	# 	break
	
	# # backspace
	# elif '\x7f' == ch:
	# 	a.pop()

		

def main_menu():
	terminal_clear()
	terminal_print('1: Message Contact')
	terminal_print('2: Resume draft')
	terminal_print('4: Read Messages')
	#terminal_print('3: Update WIFI')
	while True:
		ch = sys.stdin.read(1)

		if '1' == ch:
			contact_menu()
			break

		if '2' == ch:
			resume_draft()
			break

		elif '4' == ch:
			read_messages()
			break

		# escape
		elif '\x1b' == ch:
			terminal_print('goodbye')
			break

def get_contact_list():
	global contact_list_length
	contacts = []
	onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
	i = 0
	for c in onlyfiles:
		i += 1
		contacts.append(c)
	contact_list_length = i


def contact_menu():
	terminal_clear()
	contacts = get_contact_list()
	i = 0

	for c in contacts:
		i += 1
		terminal_print('%i: %s' % (i, c))
	
	while True:
		ch = sys.stdin.read(1)
		terminal_type(ch)
		try:
			if int(ch) <= contact_list_length:
				select_contact(int(ch))
				break;
		finally:
			pass
	
def select_contact(i):
	terminal_clear()
	onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
	name = onlyfiles[i-1]
	c = open(mypath + name, 'r').read().splitlines()
	if test_connection(c[0], c[1], c[2], c[3]):
		compose_message(name, c)
	else:
		terminal_print('Connection to %s failed.' % name)
		while True:
			ch = sys.stdin.read(1)
			# escape
			if '\x1b' == ch:
				contact_menu()
				break



def read_messages():
	my_name = get_self()
	contacts = get_contact_list()
	messages_received = []

	for contact in contacts:
		terminal_clear()
		terminal_print('Checking for messages from %s' % contact)
		c = open(contact).read().splitlines()
		host = c[0]
		username = c[1]
		key_path = c[2]
		port = c[3]
		terminal_print('Connecting to %s' % host)

		try:
			transport = paramiko.Transport((host, int(port)))
			private_key = paramiko.RSAKey.from_private_key_file(key_path)
			transport.connect(username = username, pkey=private_key)
			sftp = paramiko.SFTPClient.from_transport(transport)
			filepath = 'to-%s.txt' % my_name 
			file = sftp.file(filepath, 'r')
			msgs = file.read().splitlines()
			file.close()
			sftp.close()
			transport.close()
			if len(msgs) > 0:
				messages_received.append(msgs)
			terminal_clear()
		except Exception as e:
			terminal_clear()
			terminal_print('Failed to connect to %s' % host)
			sleep(2000)

		finally:
			while True:
				ch = sys.stdin.read(1)
				# escape
				if '\x1b' == ch:
					main_menu()
					break

def initialize_screen():
	#lcd = CharLCD('PCF8574', 0x27)
	global lcd
	# lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1,
	# 	cols=20, rows=4, dotsize=8,
	# 	charmap='A02',
	# 	auto_linebreaks=True,
	# 	backlight_enabled=True)

def update_screen(text):
	# lcd.write_string(text)
	pass



def terminal_type(char):
	#sys.stdout.write(ch.encode('hex'))
	sys.stdout.write(char)
	sys.stdout.flush()



# working around tty manipulation issue
def terminal_print(str):
	print(str + '\r')


def terminal_clear():
	os.system('cls' if os.name == 'nt' else 'clear')


def test_connection(host, username, key_path, port):
	transport = paramiko.Transport((host, int(port)))
	private_key = paramiko.RSAKey.from_private_key_file(key_path)
	transport.connect(username = username, pkey=private_key)
	connected = False
	if transport.is_active():
		connected = True

	transport.close()
	return connected


def compose_message(to_name, connection_details):
	m = []
	while True:
		ch = sys.stdin.read(1)
		terminal_type(ch)

		# # backspace
		if '\x7f' == ch:
			m.pop()

		# escape
		elif '\x1b' == ch:
			composing_menu(to_name, ''.join(m), connection_details)
			break

		else:
			m.append(ch)


def composing_menu(to_name, message, connection_details):
	terminal_clear()
	terminal_print('1: Send message')
	terminal_print('4: Save as draft')
	terminal_print('9: Discard')
	while True:
		ch = sys.stdin.read(1)

		if '1' == ch:
			send_message(to_name, message, connection_details)
			break
		elif '4' == ch:
			save_draft(to_name, message, connection_details)
			break

		elif '9' == ch:
			contact_menu()

def send_message(to_name, message, connection_details):
	terminal_print('Sending message...')
	c = connection_details
	host = c[0]
	username = c[1]
	key_path = c[2]
	port = c[3]

	try:
		transport = paramiko.Transport((host, int(port)))
		private_key = paramiko.RSAKey.from_private_key_file(key_path)
		transport.connect(username = username, pkey=private_key)
		sftp = paramiko.SFTPClient.from_transport(transport)
		filepath = 'to-%s.txt' % to_name 
		file = sftp.file(filepath, 'a')
		stampedMessage = '%s:::%s\n' % (str(datetime.datetime.now()), message)
		file.write(stampedMessage)
		file.close()
		sftp.close()
		transport.close()
		terminal_clear()
		terminal_print('Message sent!')
	except Exception as e:
		terminal_clear()
		terminal_print('Failed to send message')

	finally:
		while True:
			ch = sys.stdin.read(1)
			# escape
			if '\x1b' == ch:
				main_menu()
				break


def save_draft(to_name, message):
	terminal_clear()
	my_name = get_self()
	try:
		f = open('draft')
		f.write(message)
		f.close()		
		terminal_print('Saved draft')
	except Exception as e:
		terminal_print('Failed to save draft')
	finally:
		while True:
			ch = sys.stdin.read(1)
			if '\x1b' == ch:
				main_menu()
				break
		



def get_self():
	return = open('config').read()

# LET'S GET THIS PARTY STARTED!!!
try:
	tty.setraw(sys.stdin.fileno())
	init()
finally:
	terminal_print('attempting to return to normal')
	termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)




