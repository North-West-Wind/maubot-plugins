#!/usr/bin/env sh
mkdir -p build
for dir in maubot-*; do
	echo Packaging $dir...
	(
		cd $dir
		sh mbp.sh
		mv $dir.mbp ../build/$dir.mbp
	)
done