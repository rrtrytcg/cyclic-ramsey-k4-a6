from typing import Dict, List

import numpy as np
import torch.nn as nn
import torch.optim as optim
from rlgt.agents import DeepCrossEntropyAgent, ExponentialRandomActionMechanism
from rlgt.environments import LinearBuildEnvironment
from rlgt.graphs import CycleGraph, Graph, GraphFormat, PathGraph

from score_computation import RamseyScoreType, compute_ramsey_score


all_graphs: Dict[str, Graph] = {
    "p3m": PathGraph({GraphFormat.BITMASK_OUT}, 3),
    "p4m": PathGraph({GraphFormat.BITMASK_OUT}, 4),
    "p5m": PathGraph({GraphFormat.BITMASK_OUT}, 5),
    "p6m": PathGraph({GraphFormat.BITMASK_OUT}, 6),
    "p7m": PathGraph({GraphFormat.BITMASK_OUT}, 7),
    "c3m": CycleGraph({GraphFormat.BITMASK_OUT}, 3),
    "c4m": CycleGraph({GraphFormat.BITMASK_OUT}, 4),
    "c4b": Graph.from_bitmask(np.array([[12, 12, 3, 3]], dtype=np.uint64)),
    "c4c": Graph.from_bitmask(np.array([[6, 9, 9, 6]], dtype=np.uint64)),
    "c5m": CycleGraph({GraphFormat.BITMASK_OUT}, 5),
    "c6m": CycleGraph({GraphFormat.BITMASK_OUT}, 6),
    "c7m": CycleGraph({GraphFormat.BITMASK_OUT}, 7),
}


def train(graph_order: int, pattern_graph_list: List[str], ramsey_score_type: RamseyScoreType):
    pattern_graph_list_graphs = list(map(lambda item: all_graphs[item], pattern_graph_list))

    policy_network = nn.Sequential(
        nn.Linear(graph_order * (graph_order - 1), 72),
        nn.ReLU(),
        nn.Dropout(0.2),
        nn.Linear(72, 12),
        nn.ReLU(),
        nn.Dropout(0.2),
        nn.Linear(12, 2),
    )

    agent = DeepCrossEntropyAgent(
        environment=LinearBuildEnvironment(
            graph_invariant=lambda input_graph_batch: -compute_ramsey_score(
                input_graph_batch=input_graph_batch,
                pattern_graph_list=pattern_graph_list_graphs,
                ramsey_score_type=ramsey_score_type,
            ),
            graph_order=graph_order,
        ),
        policy_network=policy_network,
        optimizer=optim.Adam(policy_network.parameters(), lr=0.001),
        random_action_mechanism=ExponentialRandomActionMechanism(
            initial_random_action_probability=0.005,
            waiting_period=10,
            multiplicative_factor=1.25,
            maximum_random_action_probability=0.300,
        ),
    )

    print("Starting...")
    agent.reset()

    while True:
        agent.step()
        print(f"Learning iterations: {agent.step_count}. Best score: {agent.best_score:.3f}.")

        if agent.best_score > -0.5:
            solution = agent.best_graph
            print(f"Success! The following graph is a solution:")
            print(solution.adjacency_matrix_colors)

            output_file_name = "_".join(pattern_graph_list) + f"__{graph_order:02}.txt"
            with open(f"lower_bounds/{output_file_name}", "a") as opened_file:
                output_bitmask = " ".join([str(item) for item in solution.bitmask_out[-1]])
                opened_file.write(output_bitmask + "\n")

            break

        if agent.step_count >= 1000:
            print("Restarting...")
            agent.reset()


if __name__ == "__main__":
    train(
        graph_order=10,
        pattern_graph_list=["c4m", "c4c"],
        ramsey_score_type=RamseyScoreType.ORDERED,
    )
