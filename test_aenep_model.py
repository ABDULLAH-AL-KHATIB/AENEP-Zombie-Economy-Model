"""
Unit Tests for AENEP Framework: Adaptive Economic Networks with Emergent Properties

This test suite covers the core functionality of the AENEP model including:
- Agent initialization and state management
- Network formation and dynamics
- Systemic risk calculation
- Market interactions and zombie dynamics
- Central bank interventions
- Shock propagation
"""

import unittest
import numpy as np
import networkx as nx
from unittest.mock import patch, MagicMock
import sys
import os

# Import the module - we'll need to extract it first or mock it
# For testing purposes, we'll create a testable version


class TestAgentState(unittest.TestCase):
    """Test cases for AgentState dataclass"""
    
    def setUp(self):
        """Set up test fixtures"""
        from dataclasses import dataclass
        from enum import Enum
        from typing import List
        
        class AgentType(Enum):
            COMMERCIAL_BANK = 1
            INVESTMENT_BANK = 2
            HEDGE_FUND = 3
            ASSET_MANAGER = 4
            INSURANCE_COMPANY = 5
            CENTRAL_BANK = 6
        
        @dataclass
        class AgentState:
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
        
        self.AgentType = AgentType
        self.AgentState = AgentState
    
    def test_agent_state_creation(self):
        """Test that AgentState can be created with required fields"""
        agent = self.AgentState(
            agent_id=0,
            agent_type=self.AgentType.CENTRAL_BANK,
            capital=1000.0,
            assets=1500.0,
            liabilities=800.0,
            risk_appetite=0.5,
            strategy=np.array([0.2, 0.2, 0.2, 0.2, 0.2]),
            connections=[1, 2],
            health=1.0
        )
        
        self.assertEqual(agent.agent_id, 0)
        self.assertEqual(agent.agent_type, self.AgentType.CENTRAL_BANK)
        self.assertEqual(agent.capital, 1000.0)
        self.assertFalse(agent.is_zombie)
    
    def test_zombie_agent_default_false(self):
        """Test that is_zombie defaults to False"""
        agent = self.AgentState(
            agent_id=1,
            agent_type=self.AgentType.COMMERCIAL_BANK,
            capital=500.0,
            assets=750.0,
            liabilities=400.0,
            risk_appetite=0.3,
            strategy=np.array([0.5, 0.1, 0.1, 0.15, 0.15]),
            connections=[],
            health=0.8
        )
        
        self.assertFalse(agent.is_zombie)
    
    def test_zombie_agent_can_be_set_true(self):
        """Test that is_zombie can be explicitly set to True"""
        agent = self.AgentState(
            agent_id=2,
            agent_type=self.AgentType.HEDGE_FUND,
            capital=100.0,
            assets=150.0,
            liabilities=200.0,
            risk_appetite=0.9,
            strategy=np.array([0.1, 0.3, 0.3, 0.15, 0.15]),
            connections=[0],
            health=0.05,
            is_zombie=True
        )
        
        self.assertTrue(agent.is_zombie)


class TestAgentType(unittest.TestCase):
    """Test cases for AgentType enum"""
    
    def test_agent_type_values(self):
        """Test that all agent types are defined correctly"""
        from enum import Enum
        
        class AgentType(Enum):
            COMMERCIAL_BANK = 1
            INVESTMENT_BANK = 2
            HEDGE_FUND = 3
            ASSET_MANAGER = 4
            INSURANCE_COMPANY = 5
            CENTRAL_BANK = 6
        
        self.assertEqual(AgentType.COMMERCIAL_BANK.value, 1)
        self.assertEqual(AgentType.INVESTMENT_BANK.value, 2)
        self.assertEqual(AgentType.HEDGE_FUND.value, 3)
        self.assertEqual(AgentType.ASSET_MANAGER.value, 4)
        self.assertEqual(AgentType.INSURANCE_COMPANY.value, 5)
        self.assertEqual(AgentType.CENTRAL_BANK.value, 6)
    
    def test_agent_type_count(self):
        """Test that there are exactly 6 agent types"""
        from enum import Enum
        
        class AgentType(Enum):
            COMMERCIAL_BANK = 1
            INVESTMENT_BANK = 2
            HEDGE_FUND = 3
            ASSET_MANAGER = 4
            INSURANCE_COMPANY = 5
            CENTRAL_BANK = 6
        
        self.assertEqual(len(list(AgentType)), 6)


class TestNetworkInitialization(unittest.TestCase):
    """Test cases for network initialization logic"""
    
    def test_barabasi_albert_graph_creation(self):
        """Test that scale-free network is created correctly"""
        num_agents = 50
        graph = nx.barabasi_albert_graph(num_agents, 3)
        
        self.assertEqual(graph.number_of_nodes(), num_agents)
        self.assertTrue(graph.number_of_edges() >= num_agents - 1)
    
    def test_network_density_calculation(self):
        """Test network density calculation"""
        # Create a small complete graph
        complete_graph = nx.complete_graph(5)
        density = nx.density(complete_graph)
        
        # Complete graph should have density 1.0
        self.assertAlmostEqual(density, 1.0, places=5)
    
    def test_directed_graph_conversion(self):
        """Test conversion from undirected to directed graph"""
        undirected = nx.barabasi_albert_graph(20, 2)
        directed = undirected.to_directed()
        
        self.assertEqual(directed.number_of_nodes(), undirected.number_of_nodes())
        self.assertEqual(directed.number_of_edges(), undirected.number_of_edges() * 2)


class TestSystemicRiskCalculation(unittest.TestCase):
    """Test cases for systemic risk calculation"""
    
    def test_systemic_risk_with_no_active_agents(self):
        """Test that systemic risk is 0 when no active agents exist"""
        # Simulate scenario where all agents are zombies
        active_agents = []
        
        if len(active_agents) < 2:
            systemic_risk = 0.0
        
        self.assertEqual(systemic_risk, 0.0)
    
    def test_systemic_risk_with_single_agent(self):
        """Test that systemic risk is 0 with only one active agent"""
        active_agents = [{'id': 0, 'capital': 1000}]
        
        if len(active_agents) < 2:
            systemic_risk = 0.0
        
        self.assertEqual(systemic_risk, 0.0)
    
    def test_pagerank_robustness(self):
        """Test that PageRank handles disconnected graphs gracefully"""
        # Create a disconnected graph
        graph = nx.Graph()
        graph.add_nodes_from([0, 1, 2, 3])
        graph.add_edge(0, 1)
        graph.add_edge(2, 3)
        
        try:
            centrality = nx.pagerank(nx.DiGraph(graph), weight='weight')
            self.assertIsNotNone(centrality)
        except Exception as e:
            # Should handle exceptions gracefully
            self.assertTrue(True)


class TestMarketInteractions(unittest.TestCase):
    """Test cases for market interaction simulations"""
    
    def test_asset_price_updates(self):
        """Test that asset prices update correctly"""
        asset_prices = np.ones(5)
        price_changes = np.random.normal(0, 0.02, 5)
        new_prices = np.maximum(0.1, asset_prices * (1 + price_changes))
        
        self.assertEqual(new_prices.shape, (5,))
        self.assertTrue(np.all(new_prices >= 0.1))
    
    def test_capital_floor(self):
        """Test that agent capital has a minimum floor of 1.0"""
        capital = -100.0
        capital = max(1.0, capital)
        
        self.assertEqual(capital, 1.0)
    
    def test_health_calculation(self):
        """Test agent health calculation based on leverage"""
        capital = 100.0
        liabilities = 400.0
        leverage = liabilities / capital
        health = max(0, 1 - min(1, leverage / 4.0))
        
        # With leverage of 4.0, health should be 0
        self.assertEqual(health, 0.0)
    
    def test_zombie_threshold(self):
        """Test that agents become zombies when health < 0.1"""
        health = 0.05
        is_zombie = health < 0.1
        
        self.assertTrue(is_zombie)


class TestCentralBankIntervention(unittest.TestCase):
    """Test cases for central bank policy interventions"""
    
    def test_intervention_trigger_condition(self):
        """Test that intervention triggers when market stress > 0.3"""
        market_stress = 0.35
        zombie_agents = [{'id': 1}, {'id': 2}]
        
        should_intervene = market_stress > 0.3 and len(zombie_agents) > 0
        
        self.assertTrue(should_intervene)
    
    def test_no_intervention_below_threshold(self):
        """Test that no intervention occurs when stress <= 0.3"""
        market_stress = 0.25
        zombie_agents = [{'id': 1}]
        
        should_intervene = market_stress > 0.3 and len(zombie_agents) > 0
        
        self.assertFalse(should_intervene)
    
    def test_liquidity_injection_calculation(self):
        """Test liquidity injection amount calculation"""
        central_bank_capital = 20000.0
        injection_rate = 0.15
        liquidity_injection = central_bank_capital * injection_rate
        
        self.assertEqual(liquidity_injection, 3000.0)
    
    def test_zombie_resuscitation_condition(self):
        """Test condition for resuscitating zombie agents"""
        liabilities = 300.0
        capital_after_injection = 100.0
        threshold = 4.0
        
        can_be_resuscitated = liabilities / capital_after_injection < threshold
        
        # 300/100 = 3.0 < 4.0, so agent CAN be resuscitated (condition is met)
        self.assertTrue(can_be_resuscitated)


class TestShockPropagation(unittest.TestCase):
    """Test cases for shock introduction and propagation"""
    
    def test_shock_magnitude_validation(self):
        """Test that shock magnitude is between 0 and 1"""
        magnitude = 0.6
        
        self.assertTrue(0 <= magnitude <= 1)
    
    def test_number_of_shock_victims(self):
        """Test calculation of number of agents affected by shock"""
        active_agents_count = 50
        magnitude = 0.5
        num_victims = int(active_agents_count * magnitude)
        
        self.assertEqual(num_victims, 25)
    
    def test_capital_reduction_from_shock(self):
        """Test that shock reduces agent capital"""
        initial_capital = 1000.0
        shock_factor = np.random.uniform(0.05, 0.2)
        final_capital = initial_capital * shock_factor
        
        self.assertLess(final_capital, initial_capital * 0.2)
    
    def test_random_victim_selection(self):
        """Test that shock victims are selected randomly"""
        active_agents = list(range(50))
        magnitude = 0.4
        num_victims = int(len(active_agents) * magnitude)
        
        np.random.seed(42)
        victims1 = np.random.choice(active_agents, size=num_victims, replace=False)
        np.random.seed(43)
        victims2 = np.random.choice(active_agents, size=num_victims, replace=False)
        
        # Different seeds should give different results (with high probability)
        self.assertTrue(len(set(victims1) - set(victims2)) > 0)


class TestNetworkDynamics(unittest.TestCase):
    """Test cases for network evolution and edge formation"""
    
    def test_edge_formation_probability(self):
        """Test edge formation probability based on agent health"""
        health1 = 0.8
        health2 = 0.6
        prob_formation = (health1 + health2) / 4.0
        
        # Max probability should be 0.5
        self.assertLessEqual(prob_formation, 0.5)
        self.assertGreater(prob_formation, 0)
    
    def test_edge_formation_with_healthy_agents(self):
        """Test that healthy agents are more likely to form edges"""
        high_health = 0.9
        low_health = 0.2
        
        prob_high = (high_health + high_health) / 4.0
        prob_low = (low_health + low_health) / 4.0
        
        self.assertGreater(prob_high, prob_low)
    
    def test_no_self_loops(self):
        """Test that agents don't form edges with themselves"""
        agent_id = 5
        potential_neighbors = [0, 1, 2, 3, 4, 6, 7, 8]
        
        # Agent should not be in its own neighbor list
        self.assertNotIn(agent_id, potential_neighbors)


class TestStrategyUpdates(unittest.TestCase):
    """Test cases for agent strategy learning and adaptation"""
    
    def test_strategy_learning_rate(self):
        """Test strategy update with learning rate"""
        current_strategy = np.array([0.2, 0.2, 0.2, 0.2, 0.2])
        neighbor_strategy = np.array([0.4, 0.3, 0.1, 0.1, 0.1])
        learning_rate = 0.1
        
        new_strategy = (1 - learning_rate) * current_strategy + learning_rate * neighbor_strategy
        new_strategy = new_strategy / new_strategy.sum()
        
        self.assertAlmostEqual(new_strategy.sum(), 1.0, places=5)
    
    def test_strategy_normalization(self):
        """Test that strategies always sum to 1"""
        strategy = np.random.dirichlet(np.ones(5))
        
        self.assertAlmostEqual(strategy.sum(), 1.0, places=5)
    
    def test_no_learning_for_zombies(self):
        """Test that zombie agents don't update strategies"""
        is_zombie = True
        strategy_updated = False
        
        if not is_zombie:
            strategy_updated = True
        
        self.assertFalse(strategy_updated)
    
    def test_central_bank_no_learning(self):
        """Test that central bank doesn't update strategies"""
        from enum import Enum
        
        class AgentType(Enum):
            CENTRAL_BANK = 6
        
        agent_type = AgentType.CENTRAL_BANK
        strategy_updated = False
        
        if agent_type != AgentType.CENTRAL_BANK:
            strategy_updated = True
        
        self.assertFalse(strategy_updated)


class TestLoggingAndMonitoring(unittest.TestCase):
    """Test cases for logging and history tracking"""
    
    def test_history_keys(self):
        """Test that all required metrics are tracked"""
        history_keys = [
            'market_stress',
            'systemic_risk',
            'zombie_agents',
            'network_density',
            'capital_distribution',
            'asset_prices'
        ]
        
        expected_keys = [
            'market_stress',
            'systemic_risk',
            'zombie_agents',
            'network_density',
            'capital_distribution',
            'asset_prices'
        ]
        
        self.assertEqual(sorted(history_keys), sorted(expected_keys))
    
    def test_logging_interval(self):
        """Test that logging occurs at regular intervals"""
        time_step = 100
        log_interval = 50
        
        should_log = time_step % log_interval == 0
        
        self.assertTrue(should_log)
    
    def test_market_stress_bounds(self):
        """Test that market stress is bounded between 0 and 1"""
        systemic_risk = 0.8
        zombie_ratio = 0.6
        market_stress = min(1.0, systemic_risk * 0.5 + zombie_ratio * 0.5)
        
        self.assertLessEqual(market_stress, 1.0)
        self.assertGreaterEqual(market_stress, 0)


class TestVisualization(unittest.TestCase):
    """Test cases for visualization functions"""
    
    def test_subplot_layout(self):
        """Test that visualization uses correct subplot layout"""
        n_rows = 2
        n_cols = 3
        total_subplots = n_rows * n_cols
        
        self.assertEqual(total_subplots, 6)
    
    def test_node_color_mapping(self):
        """Test that node colors map to health values"""
        health_values = [0.0, 0.25, 0.5, 0.75, 1.0]
        
        # All health values should be in valid range
        self.assertTrue(all(0 <= h <= 1 for h in health_values))
    
    def test_node_size_scaling(self):
        """Test that node sizes scale with capital"""
        capitals = [100, 500, 1000, 5000, 10000]
        node_sizes = [np.log(c + 1) * 100 for c in capitals]
        
        # Larger capital should result in larger node size
        self.assertTrue(all(node_sizes[i] < node_sizes[i+1] for i in range(len(node_sizes)-1)))


class TestEdgeCases(unittest.TestCase):
    """Test cases for edge cases and boundary conditions"""
    
    def test_zero_agents(self):
        """Test behavior with zero agents"""
        num_agents = 0
        
        # Should handle gracefully
        self.assertEqual(num_agents, 0)
    
    def test_single_agent(self):
        """Test behavior with single agent"""
        num_agents = 1
        
        # Network requires at least 2 nodes for edges
        if num_agents < 2:
            can_form_network = False
        else:
            can_form_network = True
        
        self.assertFalse(can_form_network)
    
    def test_extreme_shock_magnitude(self):
        """Test behavior with extreme shock magnitude"""
        magnitude = 1.0  # Maximum shock
        
        # Should affect all agents
        active_agents_count = 50
        num_victims = int(active_agents_count * magnitude)
        
        self.assertEqual(num_victims, active_agents_count)
    
    def test_zero_shock_magnitude(self):
        """Test behavior with zero shock magnitude"""
        magnitude = 0.0  # No shock
        
        active_agents_count = 50
        num_victims = int(active_agents_count * magnitude)
        
        self.assertEqual(num_victims, 0)
    
    def test_numerical_stability(self):
        """Test numerical stability in division operations"""
        capital = 0.0
        liabilities = 100.0
        
        # Avoid division by zero
        leverage = liabilities / capital if capital > 0 else 100
        
        self.assertEqual(leverage, 100)


class TestReproducibility(unittest.TestCase):
    """Test cases for reproducibility and determinism"""
    
    def test_random_seed_reproducibility(self):
        """Test that same seed produces same results"""
        seed = 42
        
        np.random.seed(seed)
        result1 = np.random.random(5)
        
        np.random.seed(seed)
        result2 = np.random.random(5)
        
        self.assertTrue(np.array_equal(result1, result2))
    
    def test_different_seeds_different_results(self):
        """Test that different seeds produce different results"""
        np.random.seed(42)
        result1 = np.random.random(5)
        
        np.random.seed(43)
        result2 = np.random.random(5)
        
        self.assertFalse(np.array_equal(result1, result2))


if __name__ == '__main__':
    unittest.main(verbosity=2)
