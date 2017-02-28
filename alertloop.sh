#!/usr/bin/env bash

while true; do
	sleep $((60 * 15)) || break
	./alert.py
done
