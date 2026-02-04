package main

import (
	"embed"
	"fmt"
	"os"
	"strings"

	webview "github.com/webview/webview_go"
)

//go:embed ui/*
var uiFS embed.FS

type ProjectData struct {
	Name string `json:"name"`
	MD   string `json:"md"`
	YAML string `json:"yaml"`
}

func main() {
	// Create webview
	debug := true
	w := webview.New(debug)
	defer w.Destroy()

	w.SetTitle("Project View & Logic Canvas")
	w.SetSize(1400, 900, 0)

	// Initialize services
	buildService := NewBuildService()
	projectService := NewProjectService()

	// Bind Project Data Fetcher
	w.Bind("getProjectData", func(name string) ProjectData {
		data, _ := projectService.GetData(name)
		return data
	})

	// Bind Project Loader
	w.Bind("loadProjectGame", func(name string) string {
		html, err := buildService.GenerateProject(name)
		if err != nil {
			return fmt.Sprintf("Error: %v", err)
		}
		return html
	})

	// Load and prepare HTML from embedded files
	htmlBytes, err := uiFS.ReadFile("ui/index.html")
	if err != nil {
		fmt.Printf("Fatal error: Could not read embedded index.html: %v\n", err)
		return
	}
	cssBytes, err := uiFS.ReadFile("ui/style.css")
	if err != nil {
		fmt.Printf("Warning: Could not read embedded style.css: %v\n", err)
	}
	jsBytes, err := uiFS.ReadFile("ui/script.js")
	if err != nil {
		fmt.Printf("Warning: Could not read embedded script.js: %v\n", err)
	}

	html := string(htmlBytes)
	// Inject CSS and JS content directly into the HTML to avoid relative path issues in webview
	html = strings.Replace(html, `<link rel="stylesheet" href="style.css">`, `<style>`+string(cssBytes)+`</style>`, 1)
	html = strings.Replace(html, `<script src="script.js"></script>`, `<script>`+string(jsBytes)+`</script>`, 1)

	// Debug: Write HTML to file for inspection
	if err := os.WriteFile("debug_output.html", []byte(html), 0644); err != nil {
		fmt.Printf("ERROR writing debug HTML: %v\n", err)
	} else {
		fmt.Printf("✓ Wrote debug_output.html for inspection\n")
	}

	w.SetHtml(html)
	w.Run()
}
