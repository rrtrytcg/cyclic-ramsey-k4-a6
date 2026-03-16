#pragma once

#include <cstdint>

namespace SubgraphCounting {

template <template <typename T> class LengthRangeGenerator,
          class State = SubgraphStateSimple, class... ExtraArgs>
uint64_t solve_graph(AdjGraph big, AdjGraph small, ExtraArgs... args) {
  State state(big, small, args...);
  LengthRangeGenerator<State> gen(state, small.n, big.n);
  gen.run();
  return gen.get();
}

} // namespace SubgraphCounting
