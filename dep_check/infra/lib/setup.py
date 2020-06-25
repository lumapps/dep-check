from setuptools import setup, Extension

setup(
    name='goparse',
    version='1.0',
    description='Parses a file and returns its dependencies',
    build_golang={'root': 'dep-check'},
    ext_modules=[
        Extension(
            'goparse',
            sources=['find_dependencies.go'],
            py_limited_api=True,
            define_macros=[('Py_LIMITED_API', None)],
        )
    ],
    setup_requires=['setuptools-golang'],

)
