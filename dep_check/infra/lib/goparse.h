#ifndef _GOPARSE_H
#define _GOPARSE_H

int PyArg_ParseTuple_str(PyObject *, char **);

PyObject * Py_BuildValue_str(PyObject * args, char * src);

PyObject *Py_return_None();

#endif
