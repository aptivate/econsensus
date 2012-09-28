#This is a dummy class to allow testing of emails without using a full
#email server

class POP3(object):
    mailbox = ()
    
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.username = None
        self.password = None 

    def user(self, username):
        self.username = username

    def pass_(self, password):
        self.password = password
    
    def retr(self, num):
        return self.mailbox
    
    def stat(self):
        return (1, 0)
    
    def dele(self, num):
        pass
    
    def quit(self):
        pass
    
class POP3_SSL(POP3):
    pass