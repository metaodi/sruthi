#!/bin/bash

set -e

function cleanup {
    exit $?
}

trap "cleanup" EXIT

# Check code style and McCabe complexity
make lint

# Check type annotations
make typecheck

# run tests with test coverage
make test
