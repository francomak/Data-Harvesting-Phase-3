#!/bin/bash

sed 's/^.*	\([[:alnum:]]*\);\? \?$/\1/' $1
