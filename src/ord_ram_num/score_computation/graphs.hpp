#pragma once

#include <cstdint>

namespace SubgraphCounting {

struct AdjGraph {
  uint64_t adj[64] = {0};
  uint64_t n;
};

} // namespace SubgraphCounting
