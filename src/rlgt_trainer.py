from typing import List

import numpy as np
import torch.nn as nn
import torch.optim as optim
from rlgt.agents import DeepCrossEntropyAgent, ExponentialRandomActionMechanism
from rlgt.environments import LinearBuildEnvironment
from rlgt.graphs import Graph

from score_computation.ramsey_scores import RamseyScoreType, compute_ramsey_score


def train(graph_order: int, pattern_graph_list: List[Graph], ramsey_score_type: RamseyScoreType):
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
                pattern_graph_list=pattern_graph_list,
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
            print(f"Success! The following graph is a solution:")
            print(agent.best_graph.adjacency_matrix_colors)

            break

        if agent.step_count >= 1500:
            print("Restarting...")
            agent.reset()


if __name__ == "__main__":
    palt_06 = Graph.from_bitmask(np.array([[32, 48, 24, 4, 6, 3]], dtype=np.uint64))
    palt_07 = Graph.from_bitmask(np.array([[64, 96, 48, 16, 12, 6, 3]], dtype=np.uint64))
    palt_08 = Graph.from_bitmask(np.array([[128, 192, 96, 48, 8, 12, 6, 3]], dtype=np.uint64))

    # This works.
    train(
        graph_order=11,
        pattern_graph_list=[palt_06, palt_06],
        ramsey_score_type=RamseyScoreType.ORDERED,
    )

    # This works.
    # train(
    #     graph_order=12,
    #     pattern_graph_list=[palt_06, palt_07],
    #     ramsey_score_type=RamseyScoreType.ORDERED,
    # )

    # This works.
    # train(
    #     graph_order=13,
    #     pattern_graph_list=[palt_06, palt_08],
    #     ramsey_score_type=RamseyScoreType.ORDERED,
    # )

    # This works.
    # train(
    #     graph_order=13,
    #     pattern_graph_list=[palt_07, palt_07],
    #     ramsey_score_type=RamseyScoreType.ORDERED,
    # )

    # This does not work.
    # train(
    #     graph_order=13,
    #     pattern_graph_list=[palt_06, palt_07],
    #     ramsey_score_type=RamseyScoreType.ORDERED,
    # )

    # This does not work.
    # train(
    #     graph_order=14,
    #     pattern_graph_list=[palt_06, palt_08],
    #     ramsey_score_type=RamseyScoreType.ORDERED,
    # )

    # This does not work.
    # train(
    #     graph_order=14,
    #     pattern_graph_list=[palt_07, palt_07],
    #     ramsey_score_type=RamseyScoreType.ORDERED,
    # )
