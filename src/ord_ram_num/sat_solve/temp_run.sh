#!/usr/bin/env bash

maxtimegen="1m"
maxtimekis="2m"
type1="pmon"
type2="pmon"
mode="cyc"
outfile="../../../kissat_output/${type1}_${type2}_${mode}/${type1}${1}_${type2}${2}_${mode}_${3}.txt"

n=$(( $1 > $2 ? $1 : $2 ))

f1=$(printf "%02d" "${1}")
f2=$(printf "%02d" "${2}")

while true; do
	fn=$(printf "%02d" "${n}")
	outfile="../../../kissat_output/${type1}_${type2}_${mode}/${type1}${f1}_${type2}${f2}_${mode}_${fn}.txt"
	g++ -O2 cnf_gen_main.cpp -o cnf_gen_main || exit 1
	gtimeout $maxtimegen ./cnf_gen_main tmp.cnf $n $mode $1 $type1 $2 $type2
	if [ $? -eq 124 ]; then
		echo "Timeout (cnf_gen_main) at n = $n"
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

# ./cnf_gen_main tmp.cnf $3 $mode $1 $type1 $2 $type2 && ./kissat tmp.cnf > $outfile

# cat $outfile | grep "^s "

# for i in {7..11}; do
#     for j in {4..4}; do
#         for ((k=(i > j ? i : j)+6; k<=(i > j ? i : j)+9; k++)); do
#             printf -v ip "%02d" "$i"
#             printf -v jp "%02d" "$j"
#             printf -v kp "%02d" "$k"

#             g++ -O2 cnf_gen_main.cpp -o cnf_gen_main && ./cnf_gen_main tmp_${ip}_${jp}_${kp}.cnf $kp $mode $ip $type1 $jp $type2 && ./kissat tmp_${ip}_${jp}_${kp}.cnf > "../../../kissat_output/${type1}_${type2}_${mode}/${type1}${ip}_${type2}${jp}_${mode}_${kp}.txt"
#         done
#     done
# done
