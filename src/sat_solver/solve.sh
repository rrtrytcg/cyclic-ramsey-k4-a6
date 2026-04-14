#!/usr/bin/env bash

./get_binaries.sh || exit 1

type1="pmon"
type2="pmon"
mode="cyc"

maxtimegen="3m"
maxtimekis="5m"

n=$(( $1 > $2 ? $1 : $2 ))

f1=$(printf "%02d" "${1}")
f2=$(printf "%02d" "${2}")

while true; do
	fn=$(printf "%02d" "${n}")
	outfile="../../kissat_output/${type1}_${type2}_${mode}/${type1}${f1}_${type2}${f2}_${mode}_${fn}.txt"
	gtimeout $maxtimegen ./cnf_generator tmp.cnf $n $mode $1 $type1 $2 $type2
	if [ $? -eq 124 ]; then
		echo "Timeout (cnf_generator) at n = $n"
		break
	fi
	gtimeout $maxtimekis ./kissat tmp.cnf > $outfile
	if [ $? -eq 124 ]; then
		echo "Timeout (kissat) at n = $n"
		break
	fi
	result=$(cat $outfile | grep "^s ")
	if echo "$result" | grep -q "UNSATISFIABLE"; then
		echo "Unsatisfiable at n = $n"
		break
	fi
	echo "Satisfiable at n = $n, continuing ..."
	n=$(( n + 1 ))
done

