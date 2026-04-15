#!/usr/bin/env bash

./get_binaries.sh || exit 1

type1="mnest"
type2="mnest"
mode="ord"

maxtimegen="1m"
maxtimekis="2m"

amax=${1}
bmax=${2}

for ((a=3; a<=amax; a++)); do
	nomas=false
	nomas2=0

	for ((b=a; b<=bmax; b++)); do
		echo "Processing a = $a, b = $b"
		n=$(( $a > $b ? $a : $b ))

		f1=$(printf "%02d" "${a}")
		f2=$(printf "%02d" "${b}")
	
		while true; do
			fn=$(printf "%02d" "${n}")
			outfile="../../kissat_output/${type1}_${type2}_${mode}/${type1}${f1}_${type2}${f2}_${mode}_${fn}.txt"
			gtimeout $maxtimegen ./cnf_generator tmp.cnf $n $mode $a $type1 $b $type2
			if [ $? -eq 124 ]; then
				printf "\tTimeout (cnf_generator) at n = %d\n" "$n"
				nomas=true
				break
			fi
			gtimeout $maxtimekis ./kissat tmp.cnf > $outfile
			if [ $? -eq 124 ]; then
				printf "\tTimeout (kissat) at n = %d\n" "$n"
				((nomas2++))
				break
			fi
			result=$(cat $outfile | grep "^s ")
			if echo "$result" | grep -q "UNSATISFIABLE"; then
				printf "\tUnsatisfiable at n = %d\n" "$n"
				break
			fi
			printf "\tSatisfiable at n = %d, continuing ...\n" "$n"
			n=$(( n + 1 ))
		done

		if [ "$nomas" = true ]; then
			break
		fi
		if [ "$nomas2" -eq 3 ]; then
			break
		fi
	done
done