#pragma once

#include "graphs.hpp"

namespace SubgraphCounting {

class SubgraphStateSimple {
  // Arguments
  AdjGraph m_big;
  AdjGraph m_small;

  // State
  uint8_t m_map[64];
  uint64_t m_len = 0;

  uint64_t m_count = 0;

public:
  SubgraphStateSimple(AdjGraph big, AdjGraph small)
      : m_big(big), m_small(small) {}

  bool push(uint8_t x) {
    auto y = m_len;
    // Vertex y is mapped to x in the big graph.
    // is it okay?
    uint64_t required = 0;
    for (uint8_t i = 0; i < y; i++) {
      required |= ((m_small.adj[y] >> i) & 1) << m_map[i];
    }

    if ((m_big.adj[x] & required) != required) {
      return false;
    }

    // Okay
    m_map[y] = x;
    m_len++;

    if (m_len == m_small.n) {
      // all small vertices were successfully mapped
      m_count++;
    }

    return true;
  }

  void pop() { m_len--; }

  uint64_t get() const { return m_count; }
};

class SubgraphStateRequiredEdge {
  // Arguments
  AdjGraph m_big;
  AdjGraph m_small;
  uint8_t m_u; // Required edge vertex
  uint8_t m_v; // Required edge vertex

  // State
  uint8_t m_map[64];
  uint8_t m_inv_u = 0xff;
  uint8_t m_inv_v = 0xff;
  uint64_t m_len = 0;

  uint64_t m_count = 0;

public:
  SubgraphStateRequiredEdge(AdjGraph big, AdjGraph small, uint8_t u, uint8_t v)
      : m_big(big), m_small(small), m_u(u), m_v(v) {}

  bool push(uint8_t x) {
    auto y = m_len;
    // Vertex y is mapped to x in the big graph.
    // is it okay?
    uint64_t required = 0;
    for (uint8_t i = 0; i < y; i++) {
      required |= ((m_small.adj[y] >> i) & 1) << m_map[i];
    }

    if ((m_big.adj[x] & required) != required) {
      return false;
    }

    // Update inverse mappings
    // Also, if we have both mappings, check if there's
    // an edge in the small graph
    if (x == m_u) {
      if (m_inv_v != 0xff) {
        if (!(m_small.adj[m_inv_v] & (1ull << y))) {
          return false;
        }
      }
      m_inv_u = y;
    } else if (x == m_v) {
      if (m_inv_u != 0xff) {
        if (!(m_small.adj[m_inv_u] & (1ull << y))) {
          return false;
        }
      }
      m_inv_v = y;
    }

    // Ensure that vertices u, v have inverse mappings
    // Also, return early if they cannot possible both attain
    // inverse mappings.
    unsigned unmapped = (m_inv_u == 0xff) + (m_inv_v == 0xff);

    if (unmapped > m_small.n - m_len - 1) {
      return false;
    }

    // Okay
    m_map[y] = x;
    m_len++;

    if (m_len == m_small.n) {
      // all small vertices were successfully mapped
      m_count++;
    }

    return true;
  }

  void pop() {
    m_len--;
    if (m_inv_u == m_len) {
      m_inv_u = 0xff;
    }
    if (m_inv_v == m_len) {
      m_inv_v = 0xff;
    }
  }

  uint64_t get() const { return m_count; }
};

} // namespace SubgraphCounting
