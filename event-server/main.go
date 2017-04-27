package main

import (
	"encoding/json"
	"log"
	"net/http"

	"github.com/gorilla/mux"
	"github.com/gorilla/websocket"
)

var clients = make(map[*websocket.Conn]bool) // connected clients
var broadcast = make(chan Message)           // broadcast channel

// Configure the upgrader
var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool {
		return true
	},
}

// Define our message object
type Message struct {
	Content string `json:"content"`
	Type    string `json:"type"`
}

func main() {
	// Create a simple file server
	//fs := http.FileServer(http.Dir("../public"))
	r := mux.NewRouter()
	//r.Handle("/", fs)
	r.HandleFunc("/navigate/{route}", navigateHandler)

	// Configure websocket route
	r.HandleFunc("/ws", handleConnections)
	http.Handle("/", r)

	// Start listening for incoming chat messages
	go handleMessages()

	// Start the server on localhost port 8000 and log any errors
	log.Println("http server started on :8000")
	err := http.ListenAndServe(":9000", nil)
	if err != nil {
		log.Fatal("ListenAndServe: ", err)
	}
}

func navigateHandler(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	msg := &Message{
		Content: vars["route"],
		Type:    "navigation",
	}
	msgObject, _ := json.Marshal(msg)
	w.Write(msgObject)
	broadcast <- *msg

	log.Println("body: ", string(msgObject))
}
func handleConnections(w http.ResponseWriter, r *http.Request) {
	// Upgrade initial GET request to a websocket
	ws, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Fatal(err)
	}
	// Make sure we close the connection when the function returns
	defer ws.Close()

	// Register our new client
	clients[ws] = true

	for {
		var msg Message
		// Read in a new message as JSON and map it to a Message object
		err := ws.ReadJSON(&msg)
		if err != nil {
			log.Printf("error: %v", err)
			delete(clients, ws)
			break
		}
		// Send the newly received message to the broadcast channel
		broadcast <- msg
	}
}

func handleMessages() {
	for {
		// Grab the next message from the broadcast channel
		msg := <-broadcast
		for client := range clients {
			err := client.WriteJSON(msg)
			if err != nil {
				log.Printf("error: %v", err)
				client.Close()
				delete(clients, client)
			}
		}
		// Send it out to every client that is currently connected
	}
}
