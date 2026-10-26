#!/bin/bash

# Define the CMakeLists.txt file path
CMAKE_FILE="CMakeLists.txt"

# Define the Boost configuration
BOOST_CONFIG="
# Boost Configuration
set(Boost_INCLUDE_DIR /usr/include)
set(Boost_LIBRARY_DIR /usr/lib/aarch64-linux-gnu)
find_package(Boost REQUIRED)
include_directories(\${Boost_INCLUDE_DIR})
"

# Check if Boost configuration already exists
if grep -q "find_package(Boost REQUIRED)" "$CMAKE_FILE"; then
    echo "Boost configuration already exists in $CMAKE_FILE"
    exit 0
fi

# Insert Boost configuration before the first occurrence of add_subdirectory
awk -v config="$BOOST_CONFIG" '
    !added && /add_subdirectory/ {
        print config;
        added=1
    }
    { print }
' "$CMAKE_FILE" > temp_CMakeLists.txt && mv temp_CMakeLists.txt "$CMAKE_FILE"

echo "Boost configuration added before the first add_subdirectory in $CMAKE_FILE"

