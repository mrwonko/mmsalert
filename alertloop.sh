#!/usr/bin/env bash

while true; do
	./alert.py
	sleep $((60 * 15)) || break
done
