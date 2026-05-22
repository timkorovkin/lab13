package tests

import (
	"testing"
	"lab13/agent"
)

func TestDetermineLevel_Junior(t *testing.T) {
	level := agent.DetermineLevel(0)
	if level != "junior" {
		t.Errorf("Ожидался junior, получен %s", level)
	}
}

func TestDetermineLevel_Junior_Border(t *testing.T) {
	level := agent.DetermineLevel(1)
	if level != "junior" {
		t.Errorf("Ожидался junior, получен %s", level)
	}
}

func TestDetermineLevel_Middle(t *testing.T) {
	level := agent.DetermineLevel(3)
	if level != "middle" {
		t.Errorf("Ожидался middle, получен %s", level)
	}
}

func TestDetermineLevel_Middle_Border(t *testing.T) {
	level := agent.DetermineLevel(4)
	if level != "middle" {
		t.Errorf("Ожидался middle, получен %s", level)
	}
}

func TestDetermineLevel_Senior(t *testing.T) {
	level := agent.DetermineLevel(5)
	if level != "senior" {
		t.Errorf("Ожидался senior, получен %s", level)
	}
}

func TestDetermineLevel_Senior_High(t *testing.T) {
	level := agent.DetermineLevel(10)
	if level != "senior" {
		t.Errorf("Ожидался senior, получен %s", level)
	}
}