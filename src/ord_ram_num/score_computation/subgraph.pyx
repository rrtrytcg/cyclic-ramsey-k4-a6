from libc.stdint cimport uint64_t, uint8_t
from libc.stdlib cimport malloc, free
import numpy as np

cdef extern from "c_interface.h":
    uint64_t subgraph_count(uint64_t *args);
    void subgraph_count_batch(uint64_t *args, uint64_t* results);

def count_subgraphs(args: list[int]):
    cdef uint64_t cargs[129]
    cdef Py_ssize_t i

    for i in range(129):
        cargs[i] = <uint64_t>(args[i])

    # call the external C function; the array name decays to a pointer
    return subgraph_count(cargs)

def count_subgraphs_batch(args: np.ndarray) -> np.ndarray:
    cdef uint64_t* cargs
    cdef uint64_t* cresults

    n_big = args[64] // 65536

    cargs = <uint64_t*>malloc(<uint64_t>(len(args)) * 8)
    cresults = <uint64_t*>malloc(<uint64_t>(n_big) * 8)

    for i in range(args.shape[0]):
        cargs[i] = <uint64_t>(args[i])

    subgraph_count_batch(cargs, cresults)

    results = np.zeros(n_big, dtype=np.uint64)
    for i in range(n_big):
        results[i] = cresults[i]

    free(cargs)
    free(cresults)

    return results
