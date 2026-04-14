#!/usr/bin/env bash

if [[ ! -f cnf_generator ]]; then
    # Build cnf_generator from this repo
    g++ -I../../include/ord_ram_num -O2 cnf_generator.cpp -o cnf_generator || exit 1
fi

if [[ ! -f kissat ]]; then
    # Build kissat from external source files
    mkdir tmp
    cd tmp
    git clone https://github.com/arminbiere/kissat || exit 1
    cd kissat
    ./configure || exit 1
    make -j$(nproc) || exit 1
    cp build/kissat ../../
    cd ../..
    rm -rf tmp
fi
