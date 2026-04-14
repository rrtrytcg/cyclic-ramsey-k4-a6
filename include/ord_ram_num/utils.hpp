#pragma once

#include "states.hpp"

#include <cstdint>

namespace OrdRamNum {

template <template <typename T> class LengthRangeGenerator,
          class State = States::Subgraph, class... ExtraArgs>
auto solve_graph(Graph big, Graph small, ExtraArgs... args) {
  State state(big, small, args...);
  LengthRangeGenerator<State> gen(state, small.n, big.n);
  gen.run();
  return gen.get();
}

} // namespace OrdRamNum
