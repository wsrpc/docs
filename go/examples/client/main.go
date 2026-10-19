package main

import (
	"context"
	"fmt"
	"log"
	"time"

	wsrpc "github.com/wsrpc/wsrpc-go"
	"github.com/wsrpc/wsrpc-go/ws"
)

type Value struct {
	Value int `json:"value"`
}
type EchoParams struct {
	Text string `json:"text"`
}
type EchoResult struct {
	Text string `json:"text"`
}

func main() {
	routes := new(wsrpc.Router)
	if err := routes.Handle("double", func(_ context.Context, p Value) (int, error) { return p.Value * 2, nil }); err != nil {
		log.Fatal(err)
	}
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	peer, err := ws.Dial(ctx, "ws://127.0.0.1:8000/ws/", wsrpc.Options{Routes: routes})
	if err != nil {
		log.Fatal(err)
	}
	defer func() { _ = peer.Close(); peer.Wait() }()
	echo, err := peer.Method[EchoParams, EchoResult]("echo").Call(ctx, EchoParams{Text: "Go"})
	if err != nil {
		log.Fatal(err)
	}
	result, err := peer.Call[int](ctx, "callback", Value{Value: 21})
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println(echo.Text, result)
}
