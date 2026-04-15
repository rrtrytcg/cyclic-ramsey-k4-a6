#pragma once

#include <cstdint>

namespace OrdRamNum {

struct Graph {
  uint64_t adj[64] = {0};
  uint64_t n;
};

} // namespace OrdRamNum
