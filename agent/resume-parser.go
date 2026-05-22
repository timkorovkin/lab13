package agent

import (
	"encoding/json"
	"log"

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
	nc.Subscribe("resume.parse", func(msg *nats.Msg) {
		var resume Resume
		if err := json.Unmarshal(msg.Data, &resume); err != nil {
			log.Printf("[ERROR] Ошибка парсинга JSON: %v", err)
			return
		}

		log.Printf("[INFO] Получено резюме: %s, опыт: %d лет", resume.Name, resume.Experience)

		result := ParsedResume{
			Name:   resume.Name,
			Level:  DetermineLevel(resume.Experience),
			Skills: resume.Skills,
		}

		data, err := json.Marshal(result)
		if err != nil {
			log.Printf("[ERROR] Ошибка сериализации: %v", err)
			return
		}

		nc.Publish("resume.parsed", data)
		log.Printf("[INFO] Результат опубликован: %s → %s", result.Name, result.Level)
	})

	log.Println("[INFO] Агент resume_parser запущен, ожидает задачи...")
}