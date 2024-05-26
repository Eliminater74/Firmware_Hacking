for file in extracted_segments/*.bin; do
    binwalk -eM $file
done
