#!/bin/bash

download_llamafile() {
    local url=$1
    local file=$2

    if [ -f "$file" ]; then
        echo "File already exists: $file"
    else
        # Create the directory for the file if it doesn't exist
        mkdir -p "$(dirname "$file")"
        echo "Downloading $file ..."
        curl -L -o "$file" "$url"
    fi
}

download_llamafile "https://huggingface.co/Mozilla/llava-v1.5-7b-llamafile/resolve/main/llava-v1.5-7b-q4.llamafile" "llamafile/llava-v1.5-7b-q4.llamafile"

chmod +x llamafile/llava-v1.5-7b-q4.llamafile

#run llamafile without opening browser

sh -c "./llamafile/llava-v1.5-7b-q4.llamafile --nobrowser"
