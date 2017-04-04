import redis
import json
import time
from websocket import create_connection

r = redis.StrictRedis(host='localhost',port=6379, db=0)
p = r.pubsub()
p.subscribe('navigation')    
while True:
    m = p.get_message()
    if m:
        ws = create_connection("ws://127.0.0.1:9000")
        content = m['data']
        if type(content) == bytes:
            content = content.decode('ascii','ignore')
        else:
            content = str(content)
        msg = {"content": content, "channel": "navigation"}
        ws.send(json.dumps(msg))
        print("Sent")
        print("Receiving...")
        result =  ws.recv()
        print(result)
        ws.close()
        print(m['data'])
    time.sleep(0.001)
