#include "../score_computation/generators.hpp"
#include "../score_computation/state.hpp"
#include "../score_computation/utils.hpp"

#include "common_graphs.hpp"

#include <algorithm>
#include <iostream>
#include <fstream>
#include <stdexcept>

using namespace SubgraphCounting;

int print_usage() {
  std::cerr << R"(Usage: ./cnf_gen_main <outfile>
    <big_graph_nodes>
    ( ordered | cyclic )
    <small_graph_1_nodes>
    (
      path | alternating_path | reverse_alternating_path |
      cycle | star | nested_matching | complete
    )
    <small_graph_2_nodes>
    (
      path | alternating_path | reverse_alternating_path |
      cycle | star | nested_matching | complete
    )
)";
  return 1;
}

AdjGraph get_from_args(int offs, char** argv) {
  AdjGraph small;
  int small_n = atoi(argv[offs]);
  std::string desc = argv[offs + 1];
  if (desc == "path") {
    small = path(small_n);
  } else if (desc == "alternating_path") {
    small = alternating_path(small_n);
  } else if (desc == "reverse_alternating_path") {
    small = reverse_alternating_path(small_n);
  } else if (desc == "cycle") {
    small = cycle(small_n);
  } else if (desc == "star") {
    small = star(small_n);
  } else if (desc == "nested_matching") {
    small = nested_matching(small_n);
  } else if (desc == "complete") {
    small = complete(small_n);
  } else {
    throw std::runtime_error{"Unknown graph type"};
  }
  return small;
}

int main(int argc, char** argv) {
  std::string fname;
  int big_n;
  std::string problem_mode;
  AdjGraph small_1;
  AdjGraph small_2;

  try {
    if (argc != 8) {
      throw std::runtime_error{"Wrong number of arguments"};
    }
    fname = argv[1];
    big_n = atoi(argv[2]);
    problem_mode = argv[3];
    small_1 = get_from_args(4, argv);
    small_2 = get_from_args(6, argv);
  } catch (std::exception& e) {
    std::cerr << "error: " << e.what() << '\n';
    return print_usage();
  }

  std::string content = solve_graph<IncreasingSequenceGenerator, CNFState>(
      complete(big_n), small_1, 1);
  content += solve_graph<IncreasingSequenceGenerator, CNFState>(
      complete(big_n), small_2, -1);

  std::ofstream outf(fname);
  outf << "p cnf " << big_n * (big_n - 1) / 2 << ' '
            << std::count(content.begin(), content.end(), '\n') << '\n';
  outf << content;
}
