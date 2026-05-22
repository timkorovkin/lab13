package main

import (
	"log"
	"os"
	"os/signal"
	"syscall"

	"github.com/nats-io/nats.go"
	"lab13/agent"
)

func main() {
	natsURL := "nats://localhost:4222"

	nc, err := nats.Connect(natsURL)
	if err != nil {
		log.Fatalf("[ERROR] Не удалось подключиться к NATS: %v", err)
	}
	defer nc.Close()

	log.Println("[INFO] Подключение к NATS успешно")

	agent.StartResumeParserAgent(nc)

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	log.Println("[INFO] Завершение работы агента")
}