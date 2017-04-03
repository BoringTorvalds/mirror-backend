import redis
import time
from websocket import create_connection

r = redis.StrictRedis(host='localhost',port=6379, db=0)
p = r.pubsub()
p.subscribe('hello')    
while True:
    m = p.get_message()
    if m:
        ws = create_connection("ws://127.0.0.1:9000")
        print("Sending 'Hello, World'...")
        ws.send("Hello, World")
        print("Sent")
        print("Receiving...")
        result =  ws.recv()
        print(result)
        ws.close()
        print(m)
    time.sleep(0.001)
