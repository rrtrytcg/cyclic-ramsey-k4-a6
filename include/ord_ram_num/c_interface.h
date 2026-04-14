
#include <stdint.h>

/**
 * The layout is as follows:
 * First 64 values = 64 x 64 adjacency matrix of the big graph
 * Next 64 values = 64 x 64 adjacency matrix of the small graph
 *
 * The last 64-bit value should be interpreted as follows:
 *
 * Lowest byte: size of big graph
 * Next lowest byte: size of small graph
 * Next lowest byte: sequece type, one of:
 *   0: unordered combinations (any sequence of unique values)
 *   1: increasing
 *   2: circular-increasing
 * Next two bytes:
 *   - If both are zero, no edge is required in the big graph
 *   - Otherwise, these two bytes represent indices of an edge
 *      in the big graph. The edge must exist in the big graph.
 *      count only mappings where a small graph's edge is mapped
 *      into this edge.
 */
uint64_t subgraph_count(uint64_t *args);

/**
 * The layout of args is as follows:
 *
 * First 64 values = 64 x 64 adjacency matrix of the small graph
 *
 * The next first 64-bit value should be interpreted as follows:
 *
 * Lowest byte: size of small graph
 * Next lowest byte: sequece type, one of:
 *   0: unordered combinations (any sequence of unique values)
 *   1: increasing
 *   2: circular-increasing
 * Remaining 6 bytes:
 *   The number of big graphs to process.
 *
 * Let N be the number of big graphs. The following (65 * N) 64-bit
 * values describe the N graphs, where each is described using 65
 * values to be interpreted as follows:
 *
 * First 64 bit value:
 *   Lowest byte: size of graph
 *   Next two bytes:
 *   - If both are zero, no edge is required in the big graph
 *   - Otherwise, these two bytes represent indices of an edge
 *      in the big graph. The edge must exist in the big graph.
 *      count only mappings where a small graph's edge is mapped
 *      into this edge.
 *
 * The next 64 bit values describe the 64 x 64 adjacency matrix
 * of the big graph.
 *
 * The result for the i-th graph will be written into results[i].
 */
void subgraph_count_batch(uint64_t *args, uint64_t *results);
