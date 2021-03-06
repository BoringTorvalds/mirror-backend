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

type Stock struct {
	Title  string `json:"title"`
	Symbol string `json:"symbol"`
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
	// Handle weather
	r.HandleFunc("/weather/{location}", weatherHandler)
	r.HandleFunc("/fullweather/{location}", fullWeatherHandler)
	r.HandleFunc("/feeds/{option}", feedsHandler)
	r.HandleFunc("/stock/{title}/{symbol}/{exch}", stockHandler)
	http.Handle("/", r)

	// Start listening for incoming chat messages
	go handleMessages()

	// Start the server on localhost port 9001 and log any errors
	log.Println("http server started on :9001")
	err := http.ListenAndServe(":9001", nil)
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

// Request for stock
func stockHandler(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	str := vars["title"] + "/" + vars["symbol"] + "/" + vars["exch"]
	log.Println(str)
	msg := &Message{
		Content: str,
		Type:    "stock",
	}
	msgObject, _ := json.Marshal(msg)
	w.Write(msgObject)
	broadcast <- *msg
}
func weatherHandler(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	msg := &Message{
		Content: vars["location"],
		Type:    "weather",
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
func fullWeatherHandler(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	msg := &Message{
		Content: vars["location"],
		Type:    "full_weather",
	}

	msgObject, _ := json.Marshal(msg)
	w.Write(msgObject)
	broadcast <- *msg
}

func feedsHandler(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	msg := &Message{
		Content: vars["option"],
		Type:    "feeds",
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
