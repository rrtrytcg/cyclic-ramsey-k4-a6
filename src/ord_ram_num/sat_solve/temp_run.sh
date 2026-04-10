type1="cmon"
type2="palt"
mode="ord"

g++ -O2 cnf_gen_main.cpp -o cnf_gen_main && ./cnf_gen_main tmp.cnf $3 $mode $1 $type1 $2 $type2 && ./kissat tmp.cnf > "../../../kissat_output/${type1}_${type2}_${mode}/${type1}${1}_${type2}${2}_${mode}_${3}.txt"

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