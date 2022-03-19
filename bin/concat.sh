#!/bin/zsh
#
# A script that concatenates text files, first suppressing Windows \r
# characters, then concatenating and finally sorting the rows.
# The result is written to stdout
sed 's/\r//' $* | cat | sort 
