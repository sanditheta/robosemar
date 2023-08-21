#!/bin/bash

# Check if the correct number of arguments are provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <old_path> <new_path>"
    exit 1
fi

old_path="$1"
new_path="$2"

# Move the virtual environment directory
mv "$old_path" "$new_path"

# Update paths in the bin directory
for file in "$new_path/bin/"*; do
    sed -i "s#${old_path}#${new_path}#g" "$file"
done

echo "Virtual environment moved and paths updated successfully!"
