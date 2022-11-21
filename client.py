import zmq

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")


def doRequest(s):
    socket.send(bytes(s, 'ascii'))
    reply = socket.recv()
    print("Reply:", str(reply, encoding="ascii"))


while not socket.closed:
    s = input("Request: ")
    doRequest(s)
