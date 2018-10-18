# https://www.cisco.com/c/en/us/td/docs/ios/12_2/configfun/command/reference/ffun_r/frf019.pdf
import sys, tty, termios
from os import listdir
from os.path import isfile, join
# from RPLCD.i2c import CharLCD

fd = sys.stdin.fileno()
old_settings = termios.tcgetattr(fd)
mypath = 'contacts/'

# modes: main menu, contact menu, message
mode = 'main menu';

def init():
	# loop capturing input 1 character at a time.
	# switch between input and command mode like vim using the escape character.

	initialize_screen()
	global mode

	a = []
	try:
		tty.setraw(sys.stdin.fileno())
		while True:
			
			ch = sys.stdin.read(1)

			# escape
			if '\x1b' == ch:
				print 'output:'
				print ''.join(a)
				break
			
			# backspace
			elif '\x7f' == ch:
				a.pop()


			elif 'main menu' == mode:
				if '1' == ch:
					mode = 'contact menu'
					contact_menu()
				if '2' == ch:
					mode = 'read messages'
					read_messages()


			elif 'contact menu' == mode:
				try:
					if int(ch) <= contact_list_length:
						select_contact(int(ch))
				finally:
					pass

			# other characters
			else:
				# sys.stdout.write(ch)
				sys.stdout.write(ch.encode('hex'))
				sys.stdout.flush()
				a.append(ch)


	finally:
		print 'attempting to return to normal'
		termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def contact_menu():
	global contact_list_length
	onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
	i = 0
	for c in onlyfiles:
		i += 1
		print '%i: %s' % (i, c)
	contact_list_length = i
	
def select_contact(i):
	onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
	name = onlyfiles[i-1]
	print name
	print open(mypath + name, 'r').read()

def read_messages():
	print 'read messages now'

def initialize_screen():
	print '1: Message Contact'
	print '2: Read Messages'
	print '3: Update WIFI'

	#lcd = CharLCD('PCF8574', 0x27)
	global lcd
	# lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1,
	# 	cols=20, rows=4, dotsize=8,
	# 	charmap='A02',
	# 	auto_linebreaks=True,
	# 	backlight_enabled=True)

def update_screen(text):
	# lcd.write_string(text)
	noop()

init()
