#!/bin/sh

ps aux | grep system_start.py | grep -v grep | awk '{ print "kill -9", $2 }' | sh

