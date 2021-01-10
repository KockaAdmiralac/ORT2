#!/bin/bash
set -e
cd "${0%/*}"
for file in *.asm
do
    ./asm.py "$file" --iv --v3hex > "${file%.*}.v3hex"
done
