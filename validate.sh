#!/bin/bash

set -e

function cleanup {
    exit $?
}

trap "cleanup" EXIT

# Check PEP-8 code style and McCabe complexity
make lint

# Run mypy type checker
make typecheck

# run tests with test coverage
make test
