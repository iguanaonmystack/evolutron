#!/bin/sh

# This file is intended to be used as a git pre-commit hook.
# Create a symlink to it at .git/hooks/pre-commit

echo "Generating screenshots/auto.png ..."

python novel-evolve --screenshot screenshots/auto.png
git add screenshots/auto.png

echo "Done"
