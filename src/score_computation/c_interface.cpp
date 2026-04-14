#include "generators.hpp"
#include "graph.hpp"
#include "states.hpp"
#include "utils.hpp"

#include <condition_variable>
#include <cstring>
#include <functional>
#include <mutex>

extern "C" {
#include "c_interface.h"
}

namespace OrdRamNum {

void pool_submit(std::function<void()> task);

extern "C" uint64_t subgraph_count(uint64_t *args) {
  Graph big;
  Graph small;
  memcpy(big.adj, args, 512);
  memcpy(small.adj, args + 64, 512);

  auto last = args[128];
  big.n = last & 0xff;
  small.n = (last >> 8) & 0xff;
  auto type = (last >> 16) & 0xff;
  uint8_t req_u = (last >> 24) & 0xff;
  uint8_t req_v = (last >> 32) & 0xff;

  if (!req_u && !req_v) {
    if (type == 0) {
      return solve_graph<Generators::UnorderedCombination>(big, small);
    } else if (type == 1) {
      return solve_graph<Generators::Increasing>(big, small);
    } else {
      return solve_graph<Generators::Cyclic>(big, small);
    }
  } else {
    if (type == 0) {
      return solve_graph<Generators::UnorderedCombination,
                         States::SubgraphRequiredEdge>(big, small, req_u,
                                                       req_v);
    } else if (type == 1) {
      return solve_graph<Generators::Increasing, States::SubgraphRequiredEdge>(
          big, small, req_u, req_v);
    } else {
      return solve_graph<Generators::Cyclic, States::SubgraphRequiredEdge>(
          big, small, req_u, req_v);
    }
  }
}

extern "C" void subgraph_count_batch(uint64_t *args, uint64_t *results) {
  Graph small;
  memcpy(small.adj, args, 512);

  auto next = args[64];
  small.n = next & 0xff;
  auto type = (next >> 8) & 0xff;
  auto num_big = next >> 16;

  args += 65;

  auto remaining = num_big;
  std::mutex mtx;
  std::condition_variable cv;

  for (uint64_t i = 0; i < num_big; i++) {
    Graph big;
    next = *(args++);
    big.n = next & 0xff;
    memcpy(big.adj, args, 512);
    args += 64;
    auto req_u = (next >> 8) & 0xff;
    auto req_v = (next >> 16) & 0xff;

    std::function<void()> task;

    if (!req_u && !req_v) {
      if (type == 0) {
        task = [=] {
          results[i] =
              solve_graph<Generators::UnorderedCombination>(big, small);
        };
      } else if (type == 1) {
        task = [=] {
          results[i] = solve_graph<Generators::Increasing>(big, small);
        };
      } else {
        task = [=] {
          results[i] = solve_graph<Generators::Cyclic>(big, small);
        };
      }
    } else {
      if (type == 0) {
        task = [=] {
          results[i] = solve_graph<Generators::UnorderedCombination,
                                   States::SubgraphRequiredEdge>(big, small,
                                                                 req_u, req_v);
        };
      } else if (type == 1) {
        task = [=] {
          results[i] =
              solve_graph<Generators::Increasing, States::SubgraphRequiredEdge>(
                  big, small, req_u, req_v);
        };
      } else {
        task = [=] {
          results[i] =
              solve_graph<Generators::Cyclic, States::SubgraphRequiredEdge>(
                  big, small, req_u, req_v);
        };
      }
    }

    pool_submit([&, task = std::move(task)] {
      task();
      bool done = false;
      {
        std::unique_lock lck(mtx);
        done = (--remaining == 0);
      }
      if (done) {
        cv.notify_one();
      }
    });
  }

  std::unique_lock lck(mtx);
  cv.wait(lck, [&] { return remaining == 0; });
}

} // namespace OrdRamNum
