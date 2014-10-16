#!/bin/bash
for file in ../attr-*;
do
    if [ ! -e "./attrAndData-$ending" ]; then
        cat "$file" "../data-$ending" >> "./attrAndData-$ending"
    fi
done
