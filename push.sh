#!/bin/bash

if [[ -d ~/Anki/addons ]]; then
	addon_dir="$HOME/Anki/addons"
elif [[ -d ~/Documents/Anki/addons ]]; then
	addon_dir="$HOME/Documents/Anki/addons"
else
	echo "Cannot find anki directory"
	exit 1
fi

cp readings_audio.py $addon_dir
cp -r readings_audio $addon_dir
