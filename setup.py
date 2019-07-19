from setuptools import Extension, setup

setup(
    ext_modules=[
        Extension('go_parse', ['dep_check/lib/go_parse.go'])
    ],
    build_golang={'root': 'github.com/lumapps/dep-check'})
