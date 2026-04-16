#include "common_graphs.hpp"
#include "generators.hpp"
#include "states.hpp"
#include "utils.hpp"

#include <algorithm>
#include <fstream>
#include <iostream>
#include <stdexcept>

using namespace OrdRamNum;

int print_usage() {
  std::cerr << R"(Usage: ./cnf_generator <outfile>
    <big_graph_nodes>
    ( ord | cyc )
    <small_graph_1_nodes> ( pmon | palt | pralt | cmon | ssc | mnest | k )
    <small_graph_2_nodes> ( pmon | palt | pralt | cmon | ssc | mnest | k )
)";
  return 1;
}

Graph get_from_args(int offs, char **argv) {
  Graph small;
  int small_n = atoi(argv[offs]);
  std::string desc = argv[offs + 1];
  if (desc == "pmon") {
    small = path(small_n);
  } else if (desc == "palt") {
    small = alternating_path(small_n);
  } else if (desc == "pralt") {
    small = reverse_alternating_path(small_n);
  } else if (desc == "cmon") {
    small = cycle(small_n);
  } else if (desc == "ssc") {
    small = star(small_n);
  } else if (desc == "mnest") {
    small = nested_matching(small_n);
  } else if (desc == "k") {
    small = complete(small_n);
  } else if (desc == "pqmon") {
    small = example_path(5, small_n);
  } else {
    throw std::runtime_error{"Unknown graph type"};
  }
  return small;
}

int main(int argc, char **argv) {
  std::string fname;
  int big_n;
  std::string problem_mode;
  Graph small_1;
  Graph small_2;

  try {
    if (argc != 8) {
      throw std::runtime_error{"Wrong number of arguments"};
    }
    fname = argv[1];
    big_n = atoi(argv[2]);
    problem_mode = argv[3];
    small_1 = get_from_args(4, argv);
    small_2 = get_from_args(6, argv);
  } catch (std::exception &e) {
    std::cerr << "error: " << e.what() << '\n';
    return print_usage();
  }

  std::string content;

  if (problem_mode == "ord") {
    content = solve_graph<Generators::Increasing, States::CNFWriter>(
        complete(big_n), small_1, 1);
    content += solve_graph<Generators::Increasing, States::CNFWriter>(
        complete(big_n), small_2, -1);
  } else if (problem_mode == "cyc") {
    content = solve_graph<Generators::Cyclic, States::CNFWriter>(
        complete(big_n), small_1, 1);
    content += solve_graph<Generators::Cyclic, States::CNFWriter>(
        complete(big_n), small_2, -1);
  } else {
    std::cerr << "unknown problem mode: " << problem_mode << '\n';
    return 1;
  }

  std::ofstream outf(fname);
  outf << "p cnf " << big_n * (big_n - 1) / 2 << ' '
       << std::count(content.begin(), content.end(), '\n') << '\n';
  outf << content;
}
