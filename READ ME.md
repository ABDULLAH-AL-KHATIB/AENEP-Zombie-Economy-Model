# AENEP: A Computational Framework for Modeling the Emergence of a Zombie Economy

This repository contains the Python source code for the agent-based model presented in the paper:

> Al khatib, A. M. G. (Forthcoming). "Emergence of a Zombie Economy: A Computational Framework for Modeling Systemic Crises and Persistent Dysfunction."

The **Adaptive Economic Networks with Emergent Properties (AENEP)** framework is a novel computational model designed to explore the long-term consequences of systemic shocks in financial networks. This implementation simulates a financial crisis and demonstrates the emergence of a persistent "zombie economy" characterized by high systemic stress and an explosive rise in wealth inequality.

## Abstract of the Paper

Traditional economic models often assume systems return to equilibrium after a shock, failing to capture the persistent dysfunction observed in the aftermath of major financial crises. This paper argues that such events can permanently flip an economy into a dysfunctional, "zombie" state. To explore this, we introduce the AENEP framework, a novel agent-based model where agents' strategies and network connections co-evolve. Through simulation experiments, we demonstrate that a severe liquidity shock triggers a systemic collapse from which the system does not recover. Instead, it becomes trapped in a high-stress "zombie equilibrium," where central bank interventions prevent total collapse but fail to restore economic health. Critically, we find this post-crisis state endogenously generates a "great divergence": an explosive rise in wealth inequality among the few surviving agents.

## Getting Started

### Prerequisites

The simulation is written in Python 3. To run the code, you will need to have the following libraries installed:

*   **NumPy:** For numerical operations.
*   **NetworkX:** For creating and analyzing complex networks.
*   **Matplotlib:** For generating the plots and visualizations.

You can install these dependencies using pip:

```bash
pip install numpy networkx matplotlib
Running the Simulation
The main simulation script is AENEP-Zombie-Economy-Model.py
The script is configured to run the exact experiment presented in the paper when executed directly.
To run the simulation and generate the result plots, simply execute the script from your terminal:
AENEP-Zombie-Economy-Model.py
The script will:
Initialize a model with 50 agents.
Run a pre-shock simulation for 100 time steps.
Introduce a severe liquidity shock.
Run a post-shock simulation for 400 time steps to observe the crisis and its aftermath.
Automatically generate and display the two key figures from the paper: the 6-panel time-series plot and the final agent network visualization.
Model Overview
The AENEP framework models a financial system as a dynamic network of heterogeneous, adaptive agents. Key features of this implementation include:
Heterogeneous Agents: The model includes a Central Bank and various types of financial institutions (Commercial Banks, Hedge Funds, etc.) with capital levels drawn from a Pareto distribution.
Co-evolution: Agents' behavioral strategies and their network connections co-evolve in response to performance and systemic conditions.
Zombie State: Failed agents are not removed. Instead, they enter an inert "zombie" state, allowing the model to study the long-term burden of insolvent firms.
Policy Intervention: A Central Bank agent can perform targeted bailouts by recapitalizing zombie agents in an attempt to stabilize the system.
For a complete theoretical and mathematical description of the framework, please refer to the full paper.
Citation
If you use this code or the AENEP framework in your research, please cite the original paper:
@article{Alkhatib_AENEP_2025,
  author    = {Al khatib, Abdullah Mohammad Ghazi},
  title     = {Emergence of a Zombie Economy: A Computational Framework for Modeling Systemic Crises and Persistent Dysfunction},
  journal   = {Journal Name},
  year      = {Forthcoming},
  volume    = {},
  pages     = {},
  doi       = {}
}
(Note: Please update the citation details once the paper is published.)
