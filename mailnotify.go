package main

import (
	"fmt"
	"log"
	"os"
	"regexp"
	"strings"
	"time"

	"github.com/DusanKasan/parsemail"
	"github.com/dietsche/rfsnotify"
	"github.com/esiqveland/notify"
	"github.com/godbus/dbus/v5"
	"gopkg.in/fsnotify.v1"
)

var pathRegex = regexp.MustCompile(`.*\/INBOX\/new\/.*`)

var htmlEscaper = strings.NewReplacer(`&`, "&amp;", `<`, "&lt;", `>`, "&gt;")

func main() {
	// Connect to DBus for sending the notification
	conn, err := dbus.SessionBusPrivate()
	if err != nil {
		panic(err)
	}
	defer conn.Close()

	if err = conn.Auth(nil); err != nil {
		panic(err)
	}

	if err = conn.Hello(); err != nil {
		panic(err)
	}

	// Watch the filesystem
	watcher, err := rfsnotify.NewWatcher()
	if err != nil {
		log.Fatal(err)
	}
	defer watcher.Close()

	iconPath := ""
	if len(os.Args) > 2 {
		iconPath = os.Args[2]
	}

	done := make(chan bool)
	// Wait for files to be created, then parse them and show the basic info.
	go func() {
		for {
			select {
			case event, ok := <-watcher.Events:
				if !ok {
					return
				}
				if event.Op&fsnotify.Create != fsnotify.Create {
					continue
				}
				if !pathRegex.MatchString(event.Name) {
					continue
				}

				log.Printf("New file: %s", event.Name)

				file, err := os.Open(event.Name)
				if err != nil {
					log.Println("error opening file: ", err)
					continue
				}
				defer file.Close()

				email, err := parsemail.Parse(file)
				if err != nil {
					log.Println("error parsing mail file: ", err)
					continue
				}

				body := fmt.Sprintf(`<i>From: %s</i><br><i>To: %s</i><br><br>%s`,
					htmlEscaper.Replace(email.From[0].String()),
					htmlEscaper.Replace(email.Header.Get("Delivered-To")),
					htmlEscaper.Replace(email.TextBody[:100]))

				n := notify.Notification{
					AppName:       "Mail",
					ReplacesID:    uint32(0),
					AppIcon:       iconPath,
					Summary:       email.Subject,
					Body:          body,
					Hints:         map[string]dbus.Variant{},
					ExpireTimeout: time.Second * 5,
				}

				createdID, err := notify.SendNotification(conn, n)
				if err != nil {
					log.Printf("error sending notification: %v", err.Error())
				}
				log.Printf("created notification with id: %v", createdID)
			}
		}
	}()

	err = watcher.AddRecursive(os.Args[1])
	if err != nil {
		log.Fatal(err)
	}
	<-done
}
