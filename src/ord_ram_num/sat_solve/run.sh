# Example on how to run cnf_gen_main together with kissat.
# Requirements: build kissat and put the executable in this folder.
g++ -O2 cnf_gen_main.cpp -o cnf_gen_main && ./cnf_gen_main tmp.cnf $@ && ./kissat tmp.cnf

