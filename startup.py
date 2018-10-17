from cmd import Cmd

class MyPrompt(Cmd):

    def do_lightoff(self, args):
        f = open('/sys/class/leds/led0/trigger','w')
        f.write('none')
        f.close()

        b = open('/sys/class/leds/led0/brightness','w')
        b.write('1')
        b.close()

    def do_lighton(self,args):
        b = open('/sys/class/leds/led0/brightness','w')
        b.write('0')
        b.close()


    def do_hello(self, args):
        """Says hello. If you provide a name, it will greet you with it."""
        if len(args) == 0:
            name = 'stranger'
        else:
            name = args
        print "Hello, %s" % name

    def do_quit(self, args):
        """Quits the program."""
        print "Quitting."
        raise SystemExit


if __name__ == '__main__':
    prompt = MyPrompt()
    prompt.prompt = '> '
    prompt.cmdloop('Starting prompt...')
    