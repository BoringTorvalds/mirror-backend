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
	r := mux.NewRouter()
	// Configure websocket route
	r.HandleFunc("/ws", handleConnections)

	// Navigate to a mirror page
	r.HandleFunc("/navigate/{route}", navigateHandler)
	// Handle signup with name
	r.HandleFunc("/signup/{name}", signupHandler)
	// Handle training options
	r.HandleFunc("/training/{option}", trainingHandler)
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

// Navigate the mirror to the expected route
func navigateHandler(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	msg := &Message{
		Content: vars["route"],
		Type:    "navigation",
	}
	msgObject, _ := json.Marshal(msg)
	w.Write(msgObject)
	broadcast <- *msg
}

// Sign up callbacks from Alexa
func signupHandler(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	msg := &Message{
		Content: vars["name"],
		Type:    "signup",
	}
	msgObject, _ := json.Marshal(msg)
	w.Write(msgObject)
	broadcast <- *msg
}

// Switch on and off training mode
func trainingHandler(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	msg := &Message{
		Content: vars["option"],
		Type:    "training",
	}

	msgObject, _ := json.Marshal(msg)
	w.Write(msgObject)
	broadcast <- *msg
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
