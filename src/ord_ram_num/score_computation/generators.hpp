#pragma once

#include <cstdint>
#include <utility>

namespace SubgraphCounting {

template <class State> class PermutationGenerator {
  State m_state;
  uint8_t m_n;

  uint64_t m_mask = 0;
  uint64_t m_full_mask = 0;

public:
  PermutationGenerator(State state, uint8_t n)
      : m_state(state), m_n(n), m_full_mask((1ull << n) - 1) {}

  void run() {
    if (m_mask == m_full_mask) {
      return;
    }

    for (uint8_t i = 0; i < m_n; i++) {
      auto i_mask = 1ull << i;
      if (!(m_mask & i_mask)) {
        if (m_state.push(i)) {
          m_mask += i_mask;
          run();
          m_mask -= i_mask;
          m_state.pop();
        }
      }
    }
  }

  uint64_t get() const { return m_state.get(); }
};

template <class State> class VariationGenerator {
  State m_state;
  uint8_t m_target_len;
  uint8_t m_range;

  uint64_t m_len = 0;

public:
  VariationGenerator(State state, uint8_t target_len, uint8_t range)
      : m_state(state), m_target_len(target_len), m_range(range) {}

  void run() {
    if (m_len == m_target_len - 1) {
      m_state.probe_range(m_range);
    } else {
      for (uint8_t i = 0; i < m_range; i++) {
        if (m_state.push(i)) {
          m_len++;
          run();
          m_len--;
          m_state.pop();
        }
      }
    }
  }

  uint64_t get() const { return m_state.get(); }
};

template <class State> class UnorderedCombinationGenerator {
  State m_state;
  uint8_t m_target_len;
  uint8_t m_range;

  uint64_t m_len = 0;
  uint64_t m_mask = 0;

public:
  UnorderedCombinationGenerator(State state, uint8_t target_len, uint8_t range)
      : m_state(state), m_target_len(target_len), m_range(range) {}

  void run() {
    if (m_len < m_target_len) {
      for (uint8_t i = 0; i < m_range; i++) {
        uint64_t i_mask = 1ull << i;
        if (m_mask & i_mask) {
          continue;
        }

        if (m_state.push(i)) {
          m_len++;
          m_mask += i_mask;
          run();
          m_mask -= i_mask;
          m_len--;
          m_state.pop();
        }
      }
    }
  }

  uint64_t get() const { return m_state.get(); }
};

template <class State> class IncreasingSequenceGenerator {
  State m_state;
  uint8_t m_target_len;
  uint8_t m_range;

  uint64_t m_len = 0;
  uint64_t m_allowed = 0;

public:
  IncreasingSequenceGenerator(State state, uint8_t target_len, uint8_t range)
      : m_state(state), m_target_len(target_len), m_range(range) {}

  void run() {
    if (m_len < m_target_len) {
      auto upper = m_range - m_target_len + m_len;
      for (uint8_t i = m_allowed; i <= upper; i++) {
        if (m_state.push(i)) {
          m_len++;
          auto saved = std::exchange(m_allowed, i + 1);
          run();
          m_allowed = saved;
          m_len--;
          m_state.pop();
        }
      }
    }
  }

  uint64_t get() const { return m_state.get(); }
};

template <class State> class CircularSequenceGenerator {
  State m_state;
  uint8_t m_target_len;
  uint8_t m_range;

  uint64_t m_start_offset = 0;
  uint64_t m_len = 0;
  uint64_t m_allowed = 0;

public:
  CircularSequenceGenerator(State state, uint8_t target_len, uint8_t range)
      : m_state(state), m_target_len(target_len), m_range(range) {}

  void run() {
    if (m_len == 0) {
      for (uint8_t i = 0; i < m_range; i++) {
        if (m_state.push(i)) {
          m_start_offset = i;
          m_len++;
          m_allowed = 1;
          run();
          m_len--;
          m_state.pop();
        }
      }
    } else if (m_len < m_target_len) {
      auto upper = m_range - m_target_len + m_len;
      for (uint8_t i = m_allowed; i <= upper; i++) {
        uint8_t val = m_start_offset + i;
        if (val >= m_range) {
          val -= m_range;
        }

        if (m_state.push(val)) {
          m_len++;
          auto saved = std::exchange(m_allowed, i + 1);
          run();
          m_allowed = saved;
          m_len--;
          m_state.pop();
        }
      }
    }
  }

  uint64_t get() const { return m_state.get(); }
};

} // namespace SubgraphCounting
