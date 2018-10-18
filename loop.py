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
	print '1: Message Contact'
	print '2: Read Messages'
	print '3: Update WIFI'
	while True:
		ch = sys.stdin.read(1)
		terminal_helper(ch)

		if '1' == ch:
			mode = 'contact menu'
			contact_menu()
			break
		elif '2' == ch:
			mode = 'read messages'
			read_messages()
			break
		# escape
		elif '\x1b' == ch:
			print 'goodbye'
			break



def contact_menu():
	global contact_list_length
	onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
	i = 0
	for c in onlyfiles:
		i += 1
		print '%i: %s' % (i, c)
	contact_list_length = i
	
	while True:
		ch = sys.stdin.read(1)
		terminal_helper(ch)
		try:
			if int(ch) <= contact_list_length:
				select_contact(int(ch))
				break;
		finally:
			pass
	
def select_contact(i):
	onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
	name = onlyfiles[i-1]
	print name
	print open(mypath + name, 'r').read()

def read_messages():
	print 'read messages now'

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
	noop()

def terminal_helper(char):
	#sys.stdout.write(ch.encode('hex'))
	sys.stdout.write(char)
	sys.stdout.flush()


# LET'S GET THIS PARTY STARTED!!!
try:
	tty.setraw(sys.stdin.fileno())
	init()
finally:
	print 'attempting to return to normal'
	termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)




