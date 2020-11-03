#!/bin/bash


#patch amount
total=0

for i in `ls *.tar`; do
	tar -xf $i
    total=$[$total+1]
done

#begin with patch1
j=1

while [ $total -gt 0 ]; do
	if [ -d patch$j ]; then
		echo "=== patch$j ==="
		cd patch$j
        #run_patch.py should be used instead of ru_path.py in the future 
		[ -f run_path.py ] && python run_path.py 1>/dev/null
		[ -f run_patch.py ] && sed -i 's/zxvfP/xvfP/' run_patch.py && python run_patch.py 1>/dev/null
		cd ..
        total=$[$total-1]
	fi
    #patch direct: /home/kaifa/patch1, /home/kaifa/patch2
    j=$[$j+1]
done
