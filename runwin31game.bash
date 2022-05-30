#!/bin/bash
file=$1
input="win $file\nexit"
exe=".EXE"
if [[ $file != *"$exe"* ]]
then
	echo "Must be .EXE"
	exit
fi
fileloc=$(find ~/dos/WINDOWS -name $file | sed 's|/[^/]*$||')
echo $fileloc
filelocarr=($fileloc)
if [[ $fileloc == '' ]]
then
	echo "FILE NOT FOUND!!  Rename 16 bit exe to the parent dir name."
	exit
else
	echo "FILE FOUND!!!"
fi
for i in "${filelocarr[@]}"
do
	subfile=$(echo "${file%%.*}")
	if [[ $i == *"WINDOWS/$subfile"* ]]
	then
		echo "FOUND"
		fileloc=$i
		break
	fi
done
lis=$(ls $fileloc)
array=($lis)
todelete=()

for i in "${array[@]}"
do
	fil="$fileloc/$i"
	echo $fil
	dupcheck=~/dos/WINDOWS/$i
	if [ -d $dupcheck ] || [ -f $dupcheck ]
	then
		echo "File $i Exists DO NOT COPY!!"
	else
		if [ -d $fil ]
		then
			#echo "DIRECTORY: $fil"
			cp -Rvn $fil ~/dos/WINDOWS
			todelete+=($dupcheck)
		else
			if [ -f $fil ]
			then
				#echo "FILE: $fil"
				cp -vn $fil ~/dos/WINDOWS
				todelete+=($dupcheck)
			else
				echo "File or directory does not exist! $i"
			fi
		fi
	fi
done
conffilepath=~/.dosbox/dosbox-0.74-3win31.conf
echo -e $input
echo -e $input >> $conffilepath
dosbox -conf $conffilepath
sed -i '$ d' $conffilepath
sed -i '$ d' $conffilepath
for i in "${todelete[@]}"
do
	echo $i
	if [ -d $i ]
	then
		rm -r -v $i
	else
		rm -v $i
	fi
done
