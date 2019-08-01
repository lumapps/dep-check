# Contributing

Contributions are welcome, and they are greatly appreciated! Every
little bit helps, and you will always be credited.

You can contribute in different ways:

## Types of Contributions

### Report Bugs

Report bugs at <https://github.com/lumapps/dep-check/issues>.

If you are reporting a bug, please include:

- Your operating system name and version.
- Any details about your local setup that might be helpful
    in troubleshooting.
- Detailed steps to reproduce the bug.

### Fix Bugs

Look through the GitHub issues for bugs. Anything tagged with "bug" and
"help wanted" is open to whoever wants to implement it.

### Implement Features

Look through the GitHub issues for features. Anything tagged with
"enhancement" and "help wanted" is open to whoever wants to implement
it.

### Write Documentation

dep-check could always use more documentation, whether as part of the
official dep-check docs, in docstrings, or even on the web in blog
posts, articles, and such.

### Submit Feedback

The best way to send feedback is to file an issue at
<https://github.com/lumapps/dep-check/issues>.

If you are proposing a feature:

- Explain in detail how it would work.
- Keep the scope as narrow as possible, to make it easier
    to implement.
- Remember that this is a volunteer-driven project, and that
    contributions are welcome :)

## Get Started!

Ready to contribute? Here's how to set up dep-check for local
development.

1. Fork the dep-check repository on GitHub.
2. Clone your fork locally:

    ```sh
    git clone git@github.com:your_name_here/dep-check.git
    ```

3. Install your local copy into a virtualenv:

    ```sh
    python3.7 -m venv venv
    source venv/bin/activate && \
    python3.7 setup.py develop && \
    make init
    ```

4. Create a branch for local development:

    ```sh
    git checkout -b name-of-your-bugfix-or-feature
    ```

    Now you can make your changes locally.

5. When you're done making changes, check that your changes pass pylint
    and the tests:

    ```sh
    make lint
    make test
    ```

6. Commit your changes and push your branch to GitHub:

    ```sh
    git add .
    git commit -m "Your detailed description of your changes."
    git push origin name-of-your-bugfix-or-feature
    ```

7. Submit a pull request through the GitHub website.

## Pull Request Guidelines

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, you should update the docs.
    Put your new functionality into a function with a docstring, and add
    the feature to the [README.md](../README.md).
3. The pull request should work for Python 3.7.

## Tips

To run a subset of tests:

```sh
pytest tests/test_my_test
```
