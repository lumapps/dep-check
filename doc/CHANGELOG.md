# CHANGELOG

## 3.0.1(2023-03-28)

### BUGFIX

- Use OrderedSet instead of set, in order to have a deterministic runs

## 3.0.0(2022-12-21)

### MAJOR

- Update python support, tested on 3.9, 3.10, 3.11.
- Add support of dynamic rules (see doc)
- Support multiple files and directories in parameters.
- Drop `error_on_unused` option (replaced by `unused_level`).
- Add `unused_level` option to choose the raise an error when unused rules are detected.

## 2.0.1(2022-06-02)

### MAJOR

- Drop go compatibility.
- Update python support, tested on 3.8, 3.9, 3.10.
- Add `error_on_unused` option to raise an error when unused rules are detected.

## 1.0.3(2019-08-26)

### BUGFIX

- The tool now works correctly with Go.

## 1.0.0 (2019-08-20)

### Modified

- The tool now writes a full report, displaying the number of errors, warnings and files.
- The commands have been simplified, to avoid too long command lines

### Added

- The tool now supports Go language
- Better documentation

## 0.2.0 (2019-07-16)

### Added

- You can now add layers to your graph.
- The tool now warns you if a rule in your configuration file is not used.

## 0.1.0 (2019-07-09)

- First release on PyPI.
