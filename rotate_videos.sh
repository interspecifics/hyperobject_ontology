#!/bin/bash

echo "Starting video rotation script..."

# Navigate to Videos_hd_final directory
cd Videos_hd_final

# Search for directories starting with "ver" (case-insensitive) within subdirectories
for category in */; do
  for dir in "$category"*/; do
    dir_name=$(basename "$dir")
    dir_name_lower=$(echo "$dir_name" | tr '[:upper:]' '[:lower:]')
    if [[ "$dir_name_lower" =~ ^ver ]]; then
      echo "Found directory: $dir"
      # For each video file in these directories, rotate 90 degrees clockwise
      for file in "$dir"*; do
        if [ -f "$file" ]; then
          filename="${file%.*}"
          extension="${file##*.}"
          output_file="${filename}_rotated.${extension}"
          echo "Rotating $file to $output_file"
          ffmpeg -i "$file" -vf "transpose=1" "$output_file"
        fi
      done
    fi
  done
done

echo "Script completed."