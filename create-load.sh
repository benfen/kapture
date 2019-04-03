#!/bin/bash

DATA=_data.txt
TMP=_tmp.txt

echo "key:value" > $DATA

for i in {1..25}; do cat $DATA $DATA > $TMP && mv $TMP $DATA; done

watch ./dispatch-message.sh db-messages $DATA
