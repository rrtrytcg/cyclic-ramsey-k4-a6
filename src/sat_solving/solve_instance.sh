#!/usr/bin/env bash

./get_binaries.sh || exit 1
./cnf_generator tmp.cnf $@ && ./kissat tmp.cnf
