#!/usr/bin/env sh
mkdir -p build
for dir in maubot-*; do
	echo Packaging $dir...
	yes | ./.venv/bin/mbc build $dir -o build/$dir.mbp
done