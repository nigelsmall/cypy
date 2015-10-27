#!/usr/bin/env bash

CYPHER_FILES=$(find test -name *.cypher)

for FILE in ${CYPHER_FILES}
do
    python -m cypy.parser ${FILE} > /dev/null
    STATUS=$?
    if [ "${STATUS}" -ne "0" ]
    then
        echo "Failed to parse ${FILE}"
        exit ${STATUS}
    fi
done
