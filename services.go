package main

import (
	"fmt"
	"os"
	"os/exec"
)

// BuildService handles the generation of project code using external scripts.
type BuildService struct{}

// NewBuildService creates a new BuildService.
func NewBuildService() *BuildService {
	return &BuildService{}
}

// GenerateProject runs the appropriate python generator for a project.
func (s *BuildService) GenerateProject(name string) (string, error) {
	htmlFile := fmt.Sprintf("generated/%s_code.html", name)

	// We want to generate if the file doesn't exist OR if we want to force a rebuild
	if _, err := os.Stat(htmlFile); os.IsNotExist(err) {
		fmt.Printf("[BuildService] %s not found, running code_gen.py...\n", htmlFile)

		genScript := "code_gen.py"
		if _, err := os.Stat(genScript); err != nil {
			return "", fmt.Errorf("generation script %s not found", genScript)
		}

		// code_gen.py processes all yamls, we can just run it
		cmd := exec.Command("python", genScript)
		output, err := cmd.CombinedOutput()
		if err != nil {
			return "", fmt.Errorf("generation failed: %v\nOutput: %s", err, string(output))
		}
		fmt.Printf("[BuildService] Projects generated successfully.\n")
	}

	content, err := os.ReadFile(htmlFile)
	if err != nil {
		return "", fmt.Errorf("failed to read generated file: %v", err)
	}

	return string(content), nil
}

// ProjectService handles fetching project metadata.
type ProjectService struct{}

func NewProjectService() *ProjectService {
	return &ProjectService{}
}

func (s *ProjectService) GetData(name string) (ProjectData, error) {
	fmt.Printf("[ProjectService] Loading data for: %s\n", name)

	md, err := os.ReadFile(name + ".md")
	if err != nil {
		fmt.Printf("  Warning: %s.md not found\n", name)
	}

	yaml, err := os.ReadFile(name + ".yaml")
	if err != nil {
		fmt.Printf("  Warning: %s.yaml not found\n", name)
	}

	return ProjectData{
		Name: name,
		MD:   string(md),
		YAML: string(yaml),
	}, nil
}
