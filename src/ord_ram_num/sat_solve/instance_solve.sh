#!/usr/bin/env bash

g++ -I../../../include/ord_ram_num -O2 cnf_generator.cpp -o cnf_generator && ./cnf_generator tmp.cnf $@ && ./kissat tmp.cnf