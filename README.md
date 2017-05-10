## OpenFace
### Classifer server
```
docker run -p 9000:9000 -p 8000:8000 -t -i daoanhnhat1995/openface /bin/bash -l -c '/root/openface/demos/web/websocket-server.py'
```
### Middleware 
```
docker run -p 9001:9001 daoanhnhat1995/eventserver
```
or
```
go run event-server/main.go
```

