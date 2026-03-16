#include <condition_variable>
#include <functional>
#include <mutex>
#include <queue>
#include <thread>

namespace SubgraphCounting {

namespace {

class ThreadPool {
  std::queue<std::function<void()>> m_tasks;
  bool m_done = false;
  std::mutex m_mtx;
  std::condition_variable m_cv;
  std::vector<std::thread> m_threads;

public:
  void submit(std::function<void()> task) {
    {
      std::unique_lock lck(m_mtx);
      m_tasks.push(std::move(task));
    }
    m_cv.notify_one();
  }

  void thread_loop() {
    while (1) {
      std::function<void()> task;
      {
        std::unique_lock lck(m_mtx);
        m_cv.wait(lck, [&] { return !m_tasks.empty() || m_done; });
        if (m_done) {
          return;
        }
        task = std::move(m_tasks.front());
        m_tasks.pop();
      }
      task();
    }
  }

  ThreadPool() {
    size_t n_threads = std::thread::hardware_concurrency();
    for (size_t i = 0; i < n_threads; i++) {
      m_threads.emplace_back([&] { thread_loop(); });
    }
  };

  ~ThreadPool() {
    {
      std::unique_lock lck(m_mtx);
      m_done = true;
    }
    m_cv.notify_all();
    for (auto &t : m_threads) {
      t.join();
    }
  }
};

ThreadPool g_pool;

} // namespace

void pool_submit(std::function<void()> task) { g_pool.submit(std::move(task)); }

} // namespace SubgraphCounting
