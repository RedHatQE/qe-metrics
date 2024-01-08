# qe-metrics Contribution and Development Guide

## Contributing

Thank you for your interest in contributing to the qe-metrics project! We welcome any contributions that help improve the 
project and make it more robust. This document outlines the guidelines for contributing to the project. 
Please take a moment to review these guidelines before making your contributions.

### Types of Contributions

We appreciate any form of contribution, including but not limited to:

- Bug fixes
- New features
- Documentation improvements
- Code optimizations
- Test coverage improvements

### Code of Conduct

We strive to maintain a friendly and inclusive community. We have not yet established a formal code of conduct, 
but we expect all contributors to adhere to the principles of respect, open-mindedness, and professionalism. 
Please be kind and considerate when interacting with others.

## Development

If you are interested in contributing to the project, you will need to fork this repository and clone it to your local machine for development.

### Testing changes

If you would like to execute the tool with your changes:

1. Populate the `development/dev.config` file using the [configuration guide](docs/configuration-guide.md).
2. Open a terminal and `cd` to the root of the repository.
   - Run `make container-build-run` if you would like an interactive terminal in the container.
   - Run `make container-build-test` if you would like to execute the `development/test.sh` script in the container using the `development/dev.config` file.

### Executing Unit Tests

If you would like to execute the unit tests, you will need:
- Python 3.11
- tox installed `pip install tox`

Once you have the prerequisites installed, you can execute the unit tests by running `tox` from the root of the repository.

### Running pre-commit hooks

If you would like to run the pre-commit hooks, you will need:
- Python 3.11
- pre-commit installed `pip install pre-commit`

Once you have the prerequisites installed, you can run the pre-commit hooks by running `make pre-commit` from the root of the repository.

## Submitting Changes

Before submitting a pull request, please ensure that you have done the following:

1. Run the pre-commit hooks.
2. Execute the unit tests.
3. Tested your changes locally.
4. Updated the documentation if needed.
5. Update the unit tests if needed.


Thank you for contributing to firewatch! Your help is greatly appreciated.