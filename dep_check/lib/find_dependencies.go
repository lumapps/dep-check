package main

// #cgo pkg-config: python3
// #define Py_LIMITED_API
// #include <Python.h>
// int PyArg_ParseTuple_str(PyObject *, char **);
// PyObject * Py_BuildValue_str(PyObject * args, char * src);
import "C"

import (
	"fmt"
	"go/parser"
	"go/token"
)

//export find_dependencies
func find_dependencies(self, args *C.PyObject) *C.PyObject {
	var src *C.char
	if C.PyArg_ParseTuple_str(args, &src) == 0 {
		return nil
	}

	fset := token.NewFileSet() // positions are relative to fset

	// Parse src but stop after processing the imports.
	f, err := parser.ParseFile(fset, "", C.GoString(src), parser.ImportsOnly)
	if err != nil {
		fmt.Println(err)
		return nil
	}

	// Print the imports from the file's AST.
	dependencies := ""
	for _, s := range f.Imports {
		dependencies += s.Path.Value + ";"
	}

	return C.Py_BuildValue_str(self, C.CString(dependencies))
}

func main() {}
