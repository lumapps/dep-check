package main

import "C"

import (
	"fmt"
	"go/parser"
	"go/token"
)

//export FindDependencies
func FindDependencies(src string) *C.char {
	fset := token.NewFileSet() // positions are relative to fset

	// Parse src but stop after processing the imports.
	f, err := parser.ParseFile(fset, "", src, parser.ImportsOnly)
	if err != nil {
		fmt.Println(err)
		return nil
	}

	// Print the imports from the file's AST.
	dependencies := ""
	for _, s := range f.Imports {
		dependencies += s.Path.Value + ";"
	}

	return C.CString(dependencies)
}

func main() {}
