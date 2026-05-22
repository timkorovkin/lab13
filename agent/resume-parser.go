package agent

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"sync/atomic"

	"github.com/nats-io/nats.go"
)

type Resume struct {
	Name       string   `json:"name"`
	Experience int      `json:"experience_years"`
	Skills     []string `json:"skills"`
	Education  string   `json:"education"`
}

type ParsedResume struct {
	Name   string   `json:"name"`
	Level  string   `json:"level"`
	Skills []string `json:"skills"`
}

var processedCount int64

func DetermineLevel(years int) string {
	switch {
	case years < 2:
		return "junior"
	case years < 5:
		return "middle"
	default:
		return "senior"
	}
}

func StartResumeParserAgent(nc *nats.Conn) {
	os.MkdirAll("logs", 0755)
	logFile, err := os.OpenFile("logs/agent.log", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		log.Fatalf("[ERROR] Не удалось открыть файл лога: %v", err)
	}

	fileLogger := log.New(logFile, "", log.LstdFlags)

	logInfo := func(msg string) {
		line := fmt.Sprintf("[INFO] %s", msg)
		log.Println(line)
		fileLogger.Println(line)
	}

	logError := func(msg string) {
		line := fmt.Sprintf("[ERROR] %s", msg)
		log.Println(line)
		fileLogger.Println(line)
	}

	nc.Subscribe("resume.parse", func(msg *nats.Msg) {
		var resume Resume
		if err := json.Unmarshal(msg.Data, &resume); err != nil {
			logError(fmt.Sprintf("Ошибка парсинга JSON: %v", err))
			return
		}

		logInfo(fmt.Sprintf("Получено резюме: %s, опыт: %d лет", resume.Name, resume.Experience))

		result := ParsedResume{
			Name:   resume.Name,
			Level:  DetermineLevel(resume.Experience),
			Skills: resume.Skills,
		}

		data, err := json.Marshal(result)
		if err != nil {
			logError(fmt.Sprintf("Ошибка сериализации: %v", err))
			return
		}

		nc.Publish("resume.parsed", data)

		atomic.AddInt64(&processedCount, 1)
		logInfo(fmt.Sprintf("Результат опубликован: %s → %s | Обработано задач: %d", result.Name, result.Level, atomic.LoadInt64(&processedCount)))
	})

	logInfo("Агент resume_parser запущен, ожидает задачи...")
}