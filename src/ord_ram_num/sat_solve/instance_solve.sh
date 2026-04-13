#!/usr/bin/env bash

g++ -O2 cnf_gen_main.cpp -o cnf_gen_main && ./cnf_gen_main tmp.cnf $@ && ./kissat tmp.cnf