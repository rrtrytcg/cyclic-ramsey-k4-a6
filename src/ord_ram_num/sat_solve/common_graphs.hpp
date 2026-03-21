#pragma once

#include "../score_computation/graphs.hpp"

namespace SubgraphCounting {

// one node in the center and n-1 nodes arranged in a cycle
// center node has label n-1
inline AdjGraph wheel(uint8_t n) {
  AdjGraph r;
  r.n = n;
  // cycle (all except last)
  for (uint8_t i = 0; i < n - 2; i++) {
    r.adj[i] |= 1ull << (i + 1);
    r.adj[i + 1] |= 1ull << i;
  }
  // cycle last
  r.adj[0] |= 1ull << (n - 2);
  r.adj[n - 2] |= 1;

  // center
  for (uint8_t i = 0; i < n - 1; i++) {
    r.adj[i] |= 1ull << (n - 1);
  }
  r.adj[n - 1] = (1ull << (n - 1)) - 1;
  return r;
}

// path 0, 1, 2, ..., n-1
inline AdjGraph path(uint8_t n) {
  AdjGraph r;
  r.n = n;
  for (uint8_t i = 0; i < n - 1; i++) {
    r.adj[i] |= 1ull << (i + 1);
    r.adj[i + 1] |= 1ull << i;
  }
  return r;
}

// path 0, n-1, 1, n-2, ... (ends in the middle)
inline AdjGraph alternating_path(uint8_t n) {
  AdjGraph r;
  r.n = n;
  for (uint8_t i = 0; i < n - 1; i++) {
    int x = (i + 1) / 2;
    int y = n - 1 - i / 2;
    r.adj[x] |= 1ull << y;
    r.adj[y] |= 1ull << x;
  }
  return r;
}

// path n-1, 0, n-2, 1, ... (ends in the middle)
inline AdjGraph reverse_alternating_path(uint8_t n) {
  AdjGraph r;
  r.n = n;
  for (uint8_t i = 0; i < n - 1; i++) {
    int x = i / 2;
    int y = n - 1 - (i + 1) / 2;
    r.adj[x] |= 1ull << y;
    r.adj[y] |= 1ull << x;
  }
  return r;
}

// cycle 0, 1, 2, ..., n-2, n-1, 0
inline AdjGraph cycle(uint8_t n) {
  AdjGraph r;
  r.n = n;
  for (uint8_t i = 0; i < n - 1; i++) {
    r.adj[i] |= 1ull << (i + 1);
    r.adj[i + 1] |= 1ull << i;
  }
  r.adj[n-1] |= 1;
  r.adj[0] |= 1ull << (n - 1);
  return r;
}

// node 0 connected to all others
inline AdjGraph star(uint8_t n) {
  AdjGraph r;
  r.n = n;
  r.adj[0] = (1ull << n) - 2;
  for (uint8_t i = 1; i < n; i++) {
    r.adj[i] |= 1;
  }
  return r;
}

// nested matching (n must be even)
inline AdjGraph nested_matching(uint8_t n) {
  AdjGraph r;
  r.n = n;
  for (uint8_t i = 0; i < n / 2; i++) {
    uint8_t j = i + n / 2;
    r.adj[i] |= 1ull << j;
    r.adj[j] |= 1ull << i;
  }
  return r;
}

inline AdjGraph complete(uint8_t n) {
  AdjGraph r;
  r.n = n;
  for (uint8_t i = 0; i < n; i++) {
    r.adj[i] = (1ull << n) - 1 - (1ull << i);
  }

  return r;
}

} // namespace SubgraphCounting
