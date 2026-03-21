#include "../score_computation/generators.hpp"
#include "../score_computation/state.hpp"
#include "../score_computation/utils.hpp"

#include "common_graphs.hpp"

#include <algorithm>
#include <iostream>
#include <fstream>
#include <stdexcept>

int print_usage() {
  std::cerr << R"(Usage: ./cnf_gen_main <outfile>
    <big_graph_nodes>
    <small_graph_nodes>
    (
      path | alternating_path | reverse_alternating_path |
      cycle | star | nested_matching | complete
    )
)";
  return 1;
}

int main(int argc, char** argv) {
  using namespace SubgraphCounting;

  int big_n;
  AdjGraph small;
  std::string fname;

  try {
    if (argc != 5) {
      throw std::runtime_error{"Wrong number of arguments"};
    }
    fname = argv[1];
    big_n = atoi(argv[2]);
    int small_n = atoi(argv[3]);
    std::string desc = argv[4];
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
  } catch (std::exception& e) {
    std::cerr << "error: " << e.what() << '\n';
    return print_usage();
  }

  std::string content = solve_graph<IncreasingSequenceGenerator, CNFState>(
      complete(big_n), small);

  std::ofstream outf(fname);
  outf << "p cnf " << big_n * (big_n - 1) / 2 << ' '
            << std::count(content.begin(), content.end(), '\n') << '\n';
  outf << content;
}
