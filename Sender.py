import sys
import getopt,time,threading,os

import Checksum
import BasicSender

'''
This is a skeleton sender class. Create a fantastic transport protocol here.
'''
class Sender(BasicSender.BasicSender):
    def __init__(self, dest, port, filename, debug=False):
        super(Sender, self).__init__(dest, port, filename, debug)

    # Main sending loop.
    msg_size=4000
    end_size=2**32
    send_packet={}
    resend_time=0.5
    max_now=0
    def send_msg(self,seqno):
        if seqno>self.end_size:
            return
        self.infile.seek(seqno*self.msg_size,os.SEEK_SET)
        msg=self.infile.read(self.msg_size)
        msg_type='data'
        if seqno == 0:
            msg_type='start'
        elif msg.__len__()<self.msg_size:
            msg_type='end'
            self.end_size=seqno
        packet = self.make_packet(msg_type, seqno, msg)
        self.send(packet)
        self.send_packet[seqno]=(packet,time.time())
    def start(self):
        t=threading.Thread(target=self.rec,args=())
        t.setDaemon(True)
        t.start()
        self.seqno=0
        while self.seqno<=self.end_size+1:
            if self.seqno >self.max_now+5:
                continue
            self.send_msg(self.seqno)
            self.seqno+=1
        try:
            t.join()
        except:
            pass
    def rec(self):
        while True:
            response=self.receive(0.005)
            if  response is not None :
                if Checksum.validate_checksum(response):
                    _, seqno, _, _ =self.split_packet(response)
                    seqno=int(seqno)
                    if seqno-1==self.end_size:
                        return
                    for x in self.send_packet.items():
                        if x[0]<seqno:
                            self.resend_time=(self.resend_time*0.75+(time.time()-x[1][1])*0.5)
                            self.send_packet.pop(x[0])
                    self.max_now=max(self.max_now,seqno)
            for x in self.send_packet.items():
                if time.time()-x[1][1] > self.resend_time:
                    self.send(x[1][0])
                    self.send_packet[x[0]]=(x[1][0],time.time())


'''
This will be run if you run this script from the command line. You should not
change any of this; the grader may rely on the behavior here to test your
submission.
'''
if __name__ == "__main__":
    def usage():
        print "BEARS-TP Sender"
        print "-f FILE | --file=FILE The file to transfer; if empty reads from STDIN"
        print "-p PORT | --port=PORT The destination port, defaults to 33122"
        print "-a ADDRESS | --address=ADDRESS The receiver address or hostname, defaults to localhost"
        print "-d | --debug Print debug messages"
        print "-h | --help Print this usage message"

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                               "f:p:a:d", ["file=", "port=", "address=", "debug="])
    except:
        usage()
        exit()

    port = 33122
    dest = "localhost"
    filename = None
    debug = False

    for o,a in opts:
        if o in ("-f", "--file="):
            filename = a
        elif o in ("-p", "--port="):
            port = int(a)
        elif o in ("-a", "--address="):
            dest = a
        elif o in ("-d", "--debug="):
            debug = True

    s = Sender(dest,port,filename,debug)
    try:
        s.start()
    except (KeyboardInterrupt, SystemExit):
        exit()
