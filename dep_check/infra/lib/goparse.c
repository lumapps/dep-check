#include <Python.h>

PyObject * find_dependencies(PyObject *, PyObject *);

// Workaround missing variadic function support
// https://github.com/golang/go/issues/975
int PyArg_ParseTuple_str(PyObject * args, char ** src) {
    return PyArg_ParseTuple(args, "s", src);
}

// Fix SystemError: built-in function gen_nums returned NULL without setting an error
// see https://stackoverflow.com/a/40688635
PyObject *Py_return_None() {
        Py_RETURN_NONE;
}


static PyMethodDef GoParseMethods[] = {
    {"find_dependencies", find_dependencies, METH_VARARGS, "Parses a file and returns its dependencies."},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef goparsemodule = {
   PyModuleDef_HEAD_INIT, "goparse", NULL, -1, GoParseMethods
};

PyObject * Py_BuildValue_str(PyObject * args, char * src) {
    return Py_BuildValue("s", src);
}

PyMODINIT_FUNC
PyInit_goparse(void)
{
    return PyModule_Create(&goparsemodule);
}
