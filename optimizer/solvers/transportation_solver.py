import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from scipy.optimize import linprog

def solve_transportation(problem_data):
    """Solve a transportation problem."""
    supply = problem_data['supply']
    demand = problem_data['demand']
    costs = problem_data['costs']
    
    # Convert to numpy arrays
    supply = np.array(supply)
    demand = np.array(demand)
    costs = np.array(costs)
    
    # Check if the problem is balanced
    is_balanced = np.sum(supply) == np.sum(demand)
    total_supply = np.sum(supply)
    total_demand = np.sum(demand)
    
    # If not balanced, add a dummy source or destination
    original_shape = costs.shape
    if not is_balanced:
        if total_supply < total_demand:
            # Add a dummy source
            dummy_supply = total_demand - total_supply
            supply = np.append(supply, dummy_supply)
            dummy_costs = np.zeros((1, len(demand)))
            costs = np.vstack([costs, dummy_costs])
        else:
            # Add a dummy destination
            dummy_demand = total_supply - total_demand
            demand = np.append(demand, dummy_demand)
            dummy_costs = np.zeros((len(supply), 1))
            costs = np.hstack([costs, dummy_costs])
    
    # Prepare for scipy.optimize.linprog
    num_sources = len(supply)
    num_destinations = len(demand)
    
    # Flatten the cost matrix for linprog
    c = costs.flatten()
    
    # Create A_eq and b_eq for the constraints
    A_eq = np.zeros((num_sources + num_destinations, num_sources * num_destinations))
    b_eq = np.concatenate([supply, demand])
    
    # Source constraints
    for i in range(num_sources):
        A_eq[i, i*num_destinations:(i+1)*num_destinations] = 1
    
    # Destination constraints
    for j in range(num_destinations):
        for i in range(num_sources):
            A_eq[num_sources + j, i*num_destinations + j] = 1
    
    # Solve the problem
    bounds = [(0, None) for _ in range(num_sources * num_destinations)]
    result = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
    
    # Reshape the solution
    x = result.x.reshape((num_sources, num_destinations))
    
    # Calculate total cost
    total_cost = np.sum(x * costs)
    
    # Prepare the solution
    solution = {
        'status': 'Optimal' if result.success else 'Failed',
        'total_cost': float(total_cost),  # Convert to float for JSON serialization
        'allocations': x.tolist(),  # Convert numpy array to list
        'costs': costs.tolist(),    # Convert numpy array to list
        'is_balanced': int(is_balanced),  # Convert boolean to integer
    }
    
    return solution