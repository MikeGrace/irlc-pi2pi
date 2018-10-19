# https://www.cisco.com/c/en/us/td/docs/ios/12_2/configfun/command/reference/ffun_r/frf019.pdf
import sys, tty, termios, os, paramiko, datetime
from os import listdir
from os.path import isfile, join
from RPLCD.i2c import CharLCD

fd = sys.stdin.fileno()
old_settings = termios.tcgetattr(fd)

def init():
	initialize_screen()
	main_menu()
	sys.exit()

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
			sys.exit()


def get_contact_list():
	global contact_list_length
	contacts_path = 'contacts/'
	contacts = []
	onlyfiles = [f for f in listdir(contacts_path) if isfile(join(contacts_path, f))]
	i = 0
	for c in onlyfiles:
		i += 1
		contacts.append(c)
		
	contact_list_length = i
	return contacts


def contact_menu():
	terminal_clear()
	contacts = get_contact_list()
	i = 0
	for c in contacts:
		i += 1
		terminal_print('%i: %s' % (i, c))
	
	while True:
		ch = sys.stdin.read(1)
		# escape
		if '\x1b' == ch:
			main_menu()
			break
		else:
			try:
				menu_selection = int(ch)
				if menu_selection <= contact_list_length:
					select_contact(menu_selection)
					break;
			except ValueError:
				pass

	
def select_contact(i):
	terminal_clear()
	terminal_print('Connecting...')

	contacts_path = 'contacts/'
	contacts = get_contact_list()
	name = contacts[i-1]
	c = open(contacts_path + name, 'r').read().splitlines()
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
	global lcd
	# lcd = CharLCD('PCF8574', 0x27)
	
	lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1,
		cols=20, rows=4, dotsize=8,
		charmap='A02',
		auto_linebreaks=True,
		backlight_enabled=True)

def screen_print(text):
	lcd.write_string(text + '\n\r')

def screen_clear():
	lcd.clear()

def screen_type(char):
	lcd.write_string(char)

def screen_shift_up(chars):
	lcd.clear()
	lcd.write_string(''.join(chars))

def screen_backspace(chars):
	screen_cursor_shift()
	lcd.write_string(' ')
	screen_cursor_shift()

def screen_cursor_shift(chars):
	pos = lcd.cursor_pos
	# at the beginning of the screen
	if pos[0] == 0 and pos[1] == 0:
		pass
	# at the beginning of the line
	elif pos[0] > 0 and pos[1] == 0:
		lcd.cursor_pos = (pos[0] - 1, 19)
		screen_shift_down(chars)
	else:
		lcd.cursor_pos = (pos[0], pos[1] - 1)

def screen_cursor_hide():
	lcd.cursor_mode = 'hide'

def screen_cursor_line():
	lcd.cursor_mode = 'line'

def terminal_type(char):
	#sys.stdout.write(ch.encode('hex'))
	sys.stdout.write(char)
	sys.stdout.flush()
	screen_type(char)



# working around tty manipulation issue
def terminal_print(str):
	print(str + '\r')
	screen_print(str)


def terminal_clear():
	os.system('cls' if os.name == 'nt' else 'clear')
	screen_clear()


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
	terminal_clear()
	screen_cursor_line()
	m = []
	screen_character_count = 0
	line_character_count = 0
	screen_full = False

	while True:
		ch = sys.stdin.read(1)

		# # backspace
		if '\x7f' == ch:
			if screen_character_count > 0:
				m.pop()
				screen_backspace(m)
				screen_character_count -= 1
				line_character_count -= 1

		# escape
		elif '\x1b' == ch:
			composing_menu(to_name, ''.join(m), connection_details)
			screen_cursor_hide()
			break

		elif '\x0D' == ch:
			pass

		else:
			m.append(ch)
			terminal_type(ch)
			screen_character_count += 1
			line_character_count += 1

			if screen_full and line_character_count == 20:
				# shift lines up, clear last row, set cursor to beginnig of last row
				line_character_count = 0
				screen_shift_up(m[-60:])
			elif screen_full == False and screen_character_count == 80:
				#shift lines up, clear last row, set cursor to beginning of last row
				screen_full = True
				line_character_count = 0
				screen_shift_up(m[-60:])


def composing_menu(to_name, message, connection_details):
	terminal_clear()
	terminal_print('1: Send message')
	terminal_print('4: Save as draft')
	terminal_print('Esc: Discard')
	while True:
		ch = sys.stdin.read(1)

		if '1' == ch:
			send_message(to_name, message, connection_details)
			break
		elif '4' == ch:
			save_draft(to_name, message, connection_details)
			break
		elif '\x1b' == ch:
			contact_menu()

def send_message(to_name, message, connection_details):
	terminal_clear()
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
		terminal_print('Esc: main menu')
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
		terminal_print('Esc: Main menu')
		while True:
			ch = sys.stdin.read(1)
			if '\x1b' == ch:
				main_menu()
				break
		



def get_self():
	return open('config').read()


def exit_app():
	terminal_clear()
	terminal_print('GoodBye!')
	termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)



# LET'S GET THIS PARTY STARTED!!!
try:
	tty.setraw(sys.stdin.fileno())
	init()
finally:
	terminal_clear()
	terminal_print('GoodBye!')
	termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
	sys.exit()




#