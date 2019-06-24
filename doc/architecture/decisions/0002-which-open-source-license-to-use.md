# 2. Which open-source license to use

- Status: pending
- Date: 2019-06-20

## Context

As the dependency checker is going to be released as open-source software, we have to chose which open-source license we are going to use, and why.
This tool makes sure the dependencies between every file are well respected, based on the principles of Clean Architecture.

## Considered options

### Apache License 2.0

Non copyleft license, allows commercial and private use, modification and distribution, changes must be stated and documented. It also provides a grant of patent rights.

Pros:

- Very popular today
- Compatible with GNU GPL v3.0

Cons:

- Not compatible with GNU GPL 2.0 (which is used a lot)

### MIT License

Non copyleft license very permissive, allows almost everything under no conditions. It doesn't provide any grant of patent rights though.

Pros:

- Compatible with GNU GPL
- Applies very well for small programs

Cons:

- Maybe too permissive?

### GNU GPL

Copyleft license, meaning that any modification must be released under the same license when distributed. Allows commercial and private use, modification and distribution, changes must be stated and documented. It also provides a grant of patent rights. Source code must be made available when distributed.

Pros:

- The most popular and known by developers
- Ensure the program improvement over time

Cons:

- "Contaminating" license
- Can talk people out of using the tool in companies, because of too many constraints

## Decision proposed

We think that MIT License is the one that best applies to our tool, because it's the one that gives the most freedom to future users.
