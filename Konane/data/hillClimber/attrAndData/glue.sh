#!/bin/bash
for file in ../attr-*;
do
    ending=${file:8}
    if [ ! -e "./attrAndData-$ending" ]; then
        cat "$file" "../data-$ending" >> "./attrAndData-$ending"
    fi
done
