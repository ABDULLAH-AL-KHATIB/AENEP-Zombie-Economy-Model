"""
AENEP Framework: Adaptive Economic Networks with Emergent Properties

A novel computational framework for modeling economic systems as complex adaptive networks.
Version 6: Corrected network dynamics for stable density plot.
"""

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from scipy.stats import pareto
from enum import Enum
import logging
from dataclasses import dataclass
from typing import Dict, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AENEP")


class AgentType(Enum):
    """Enumeration of different agent types in the economic network."""
    COMMERCIAL_BANK = 1
    INVESTMENT_BANK = 2
    HEDGE_FUND = 3
    ASSET_MANAGER = 4
    INSURANCE_COMPANY = 5
    CENTRAL_BANK = 6


@dataclass
class AgentState:
    """Represents the state of an economic agent."""
    agent_id: int
    agent_type: AgentType
    capital: float
    assets: float
    liabilities: float
    risk_appetite: float
    strategy: np.ndarray
    connections: List[int]
    health: float
    is_zombie: bool = False


class AENEPModel:
    """
    Adaptive Economic Networks with Emergent Properties Model.
    
    Simulates economic agents interacting through a dynamic network,
    with zombie firm dynamics and central bank intervention policies.
    """
    
    def __init__(self, num_agents: int = 50, initial_capital: float = 1000.0,
                 network_type: str = "scale_free", seed: int = 42):
        """
        Initialize the AENEP model.
        
        Args:
            num_agents: Number of economic agents in the simulation
            initial_capital: Base capital level for agents
            network_type: Type of network topology (default: scale_free)
            seed: Random seed for reproducibility
        """
        self.num_agents = num_agents
        self.initial_capital = initial_capital
        self.seed = seed
        np.random.seed(seed)
        
        self.agents = self._initialize_agents(num_agents)
        self.network = self._initialize_network(num_agents)
        self.market_stress = 0.0
        self.asset_prices = np.ones(5)
        self.time_step = 0
        
        self.history = {
            'market_stress': [],
            'systemic_risk': [],
            'zombie_agents': [],
            'network_density': [],
            'capital_distribution': [],
            'asset_prices': []
        }
        
        logger.info(f"AENEP model initialized with {num_agents} agents")
    
    def _initialize_agents(self, num_agents) -> Dict[int, AgentState]:
        """Create and initialize economic agents with heterogeneous characteristics."""
        agents = {}
        capital_dist = pareto.rvs(1.5, size=num_agents) * self.initial_capital
        
        for i in range(num_agents):
            # Central bank is always agent 0
            if i == 0:
                agent_type = AgentType.CENTRAL_BANK
                capital = self.initial_capital * 20
            else:
                agent_type = np.random.choice(
                    [AgentType.COMMERCIAL_BANK, AgentType.INVESTMENT_BANK,
                     AgentType.HEDGE_FUND, AgentType.ASSET_MANAGER, AgentType.INSURANCE_COMPANY],
                    p=[0.55, 0.05, 0.10, 0.15, 0.15]
                )
                capital = max(1.0, capital_dist[i])
            
            agents[i] = AgentState(
                agent_id=i,
                agent_type=agent_type,
                capital=capital,
                assets=capital * np.random.uniform(1.5, 3.0),
                liabilities=capital * np.random.uniform(1.0, 2.5),
                risk_appetite=np.random.beta(2, 2),
                strategy=np.random.dirichlet(np.ones(5)),
                connections=[],
                health=1.0
            )
        
        return agents
    
    def _initialize_network(self, num_agents) -> nx.Graph:
        """Initialize the economic network using Barabási-Albert preferential attachment."""
        graph = nx.barabasi_albert_graph(num_agents, 3)
        
        # Initialize connection lists for all agents
        for i in range(num_agents):
            self.agents[i].connections = list(graph.neighbors(i))
        
        return graph.to_directed()
    
    def _calculate_systemic_risk(self) -> float:
        """
        Calculate systemic risk based on agent vulnerabilities and network centrality.
        
        Returns:
            Systemic risk score between 0 and 1
        """
        active_agents = [a for a in self.agents.values() if not a.is_zombie]
        
        if len(active_agents) < 2:
            return 0.0
        
        active_ids = [a.agent_id for a in active_agents]
        subgraph = self.network.subgraph(active_ids)
        
        if subgraph.number_of_nodes() < 2:
            return 0.0
        
        try:
            # Use PageRank for robustness with disconnected graphs
            centrality = nx.pagerank(subgraph, weight='weight')
            centralities = np.array([centrality.get(a.agent_id, 0) for a in active_agents])
            
            # Calculate vulnerability based on leverage
            vulnerabilities = np.array([
                min(1.0, (a.liabilities / a.capital if a.capital > 0 else 100) / 10)
                for a in active_agents
            ])
            
            sum_centralities = np.sum(centralities)
            if sum_centralities == 0:
                return 0.0
            
            # Weighted risk calculation
            return min(1.0, np.dot(centralities, vulnerabilities) / sum_centralities * len(active_agents) * 0.5)
        
        except Exception as e:
            logger.warning(f"Error in systemic risk calculation: {e}")
            return self.history['systemic_risk'][-1] if self.history['systemic_risk'] else 0.0
    
    def _update_network(self):
        """Update network topology by adding edges between healthy agents."""
        # Select healthy, non-central bank agents
        active_agents = [
            agent for agent_id, agent in self.agents.items()
            if not agent.is_zombie and agent.agent_type != AgentType.CENTRAL_BANK
        ]
        
        if len(active_agents) < 2:
            return
        
        agent1, agent2 = np.random.choice(active_agents, 2, replace=False)
        
        # Form new connections based on health
        if not self.network.has_edge(agent1.agent_id, agent2.agent_id):
            prob_formation = (agent1.health + agent2.health) / 4.0  # Max prob = 0.5
            if np.random.random() < prob_formation:
                self.network.add_edge(agent1.agent_id, agent2.agent_id,
                                    weight=np.random.exponential(0.5))
                agent1.connections.append(agent2.agent_id)
                logger.debug(f"Formed new link between {agent1.agent_id} and {agent2.agent_id}")
    
    def _update_agent_strategies(self):
        """Allow agents to learn and adapt strategies from successful neighbors."""
        for agent in self.agents.values():
            if agent.is_zombie or agent.agent_type == AgentType.CENTRAL_BANK:
                continue
            
            learning_rate = 0.1 * (1 + self.market_stress)
            
            if agent.connections:
                neighbors = [
                    self.agents[nid] for nid in agent.connections
                    if nid in self.agents and not self.agents[nid].is_zombie
                ]
                
                if neighbors:
                    best_neighbor = max(neighbors, key=lambda n: n.capital, default=None)
                    if best_neighbor and best_neighbor.capital > agent.capital:
                        agent.strategy = ((1 - learning_rate) * agent.strategy +
                                        learning_rate * best_neighbor.strategy)
                        agent.strategy /= agent.strategy.sum()
    
    def _simulate_market_interactions(self):
        """Simulate trading and market interactions between agents."""
        # Update asset prices
        price_changes = np.random.normal(0, 0.02 + self.market_stress * 0.1, 5)
        self.asset_prices = np.maximum(0.1, self.asset_prices * (1 + price_changes))
        
        for agent in self.agents.values():
            if agent.is_zombie or agent.agent_type == AgentType.CENTRAL_BANK:
                continue
            
            # Trading based on strategy and risk appetite
            trade_intensity = agent.strategy[0] * (1 - agent.risk_appetite * self.market_stress)
            trading_result = np.random.normal(0, trade_intensity * 0.2) * agent.capital
            
            # Network effects from neighbors
            network_effect = 0
            if agent.connections:
                neighbors = [
                    self.agents[nid] for nid in agent.connections
                    if nid in self.agents and not self.agents[nid].is_zombie
                ]
                if neighbors:
                    neighbor_health = np.mean([n.health for n in neighbors])
                    network_effect = (neighbor_health - 0.7) * agent.capital * 0.05
            
            agent.capital += trading_result + network_effect
            agent.capital = max(1.0, agent.capital)
            
            # Update health based on leverage
            leverage = agent.liabilities / agent.capital
            agent.health = max(0, 1 - min(1, leverage / 4.0))
            
            # Check for zombie status
            if agent.health < 0.1:
                agent.is_zombie = True
                agent.capital = 1.0
                logger.info(f"Agent {agent.agent_id} has become a zombie.")
    
    def _apply_central_bank_policy(self):
        """Implement central bank intervention during crises."""
        central_bank = self.agents.get(0)
        if not central_bank or central_bank.agent_type != AgentType.CENTRAL_BANK:
            return
        
        zombie_agents = [a for a in self.agents.values() if a.is_zombie]
        
        if self.market_stress > 0.3 and zombie_agents:
            logger.info(f"Central Bank intervening. Stress: {self.market_stress:.2f}. "
                       f"Zombies: {len(zombie_agents)}")
            
            liquidity_injection = central_bank.capital * 0.15
            
            if central_bank.capital > liquidity_injection:
                central_bank.capital -= liquidity_injection
                
                for zombie in zombie_agents:
                    recapitalization_amount = liquidity_injection / len(zombie_agents)
                    zombie.capital += recapitalization_amount
                    
                    if zombie.liabilities / zombie.capital < 4.0:
                        zombie.is_zombie = False
                        zombie.health = 0.5
                        logger.info(f"Agent {zombie.agent_id} resuscitated by Central Bank.")
    
    def step(self):
        """Execute one time step of the simulation."""
        self.time_step += 1
        
        self._update_agent_strategies()
        self._simulate_market_interactions()
        self._apply_central_bank_policy()
        self._update_network()
        
        # Record metrics
        zombie_count = sum(1 for a in self.agents.values() if a.is_zombie)
        systemic_risk = self._calculate_systemic_risk()
        self.market_stress = min(1.0, systemic_risk * 0.5 + (zombie_count / self.num_agents) * 0.5)
        
        self.history['market_stress'].append(self.market_stress)
        self.history['systemic_risk'].append(systemic_risk)
        self.history['zombie_agents'].append(zombie_count)
        self.history['network_density'].append(nx.density(self.network))
        
        active_capitals = [a.capital for a in self.agents.values() if not a.is_zombie]
        self.history['capital_distribution'].append(
            np.std(active_capitals) if active_capitals else 0
        )
        self.history['asset_prices'].append(self.asset_prices.copy())
        
        if self.time_step % 50 == 0:
            logger.info(f"Step {self.time_step}: Stress={self.market_stress:.2f}, "
                       f"Risk={systemic_risk:.2f}, Zombies={zombie_count}")
    
    def run(self, steps: int):
        """Run the simulation for a specified number of steps."""
        for _ in range(steps):
            self.step()
    
    def introduce_shock(self, magnitude: float = 0.6):
        """
        Introduce an exogenous shock to the system.
        
        Args:
            magnitude: Fraction of agents to affect (0 to 1)
        """
        active_agents = [
            a for a in self.agents.values()
            if not a.is_zombie and a.agent_type != AgentType.CENTRAL_BANK
        ]
        
        if not active_agents:
            return
        
        num_victims = int(len(active_agents) * magnitude)
        victims = np.random.choice(active_agents, size=num_victims, replace=False)
        
        for victim in victims:
            victim.capital *= np.random.uniform(0.05, 0.2)
        
        logger.info(f"Introduced liquidity shock to {num_victims} agents.")
    
    def visualize(self, steps_to_show: int):
        """Generate visualization of simulation results."""
        fig, axes = plt.subplots(2, 3, figsize=(18, 10))
        fig.suptitle('AENEP Framework Simulation Results (with Zombie Dynamics)', fontsize=16)
        
        # Plot time series
        axes[0, 0].plot(self.history['market_stress'])
        axes[0, 0].set_title('Market Stress')
        
        axes[0, 1].plot(self.history['systemic_risk'], 'r')
        axes[0, 1].set_title('Systemic Risk')
        
        axes[0, 2].plot(self.history['zombie_agents'], 'orange')
        axes[0, 2].set_title('Zombie Agents')
        
        axes[1, 0].plot(self.history['network_density'], 'g')
        axes[1, 0].set_title('Network Density')
        
        axes[1, 1].plot(self.history['capital_distribution'], 'purple')
        axes[1, 1].set_title('Capital Inequality (Std Dev)')
        
        # Asset prices
        asset_prices = np.array(self.history['asset_prices'])
        for i in range(5):
            axes[1, 2].plot(asset_prices[:, i], label=f'Asset {i+1}')
        axes[1, 2].legend()
        axes[1, 2].set_title('Asset Prices')
        
        # Format plots
        for ax_row in axes:
            for ax in ax_row:
                ax.grid(True)
                ax.set_xlabel("Time Steps")
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.show()
        
        # Network visualization
        plt.figure(figsize=(12, 10))
        node_colors = [agent.health for agent in self.agents.values()]
        node_sizes = [np.log(agent.capital + 1) * 100 for agent in self.agents.values()]
        pos = nx.spring_layout(self.network, seed=self.seed)
        
        nx.draw_networkx_nodes(self.network, pos,
                              node_color=node_colors,
                              node_size=node_sizes,
                              cmap=plt.cm.RdYlGn, vmin=0, vmax=1)
        nx.draw_networkx_edges(self.network, pos, alpha=0.2)
        
        plt.title('Final Agent Network (Color=Health, Size=Capital)', fontsize=14)
        
        sm = plt.cm.ScalarMappable(cmap=plt.cm.RdYlGn,
                                   norm=plt.Normalize(vmin=0, vmax=1))
        cbar = plt.colorbar(sm, ax=plt.gca())
        cbar.set_label('Agent Health')
        plt.show()


if __name__ == "__main__":
    # Initialize model
    model = AENEPModel(num_agents=50, seed=42)
    
    # Pre-shock simulation
    logger.info("Running pre-shock simulation...")
    model.run(steps=100)
    
    # Introduce shock
    logger.info("Introducing a severe liquidity shock...")
    model.introduce_shock(magnitude=0.5)
    
    # Post-shock recovery
    logger.info("Running post-shock crisis and recovery...")
    model.run(steps=400)
    
    # Generate visualizations
    logger.info("Generating visualizations...")
    model.visualize(steps_to_show=500)
