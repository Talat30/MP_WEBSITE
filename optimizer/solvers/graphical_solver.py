import numpy as np
import matplotlib.pyplot as plt
import io
import base64
from matplotlib.patches import Polygon
import re
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt

from pulp import LpMaximize, LpMinimize, LpProblem, LpVariable, LpStatus, value

def parse_expression(expr):
    """Parse a linear expression string into coefficients and variables."""
    # Replace minus with plus minus for easier splitting
    expr = expr.replace('-', '+-').replace('++', '+')
    if expr.startswith('+'):
        expr = expr[1:]
    
    terms = expr.split('+')
    coefficients = {}
    
    for term in terms:
        if not term:
            continue
        
        # Match coefficient and variable
        match = re.match(r'([-]?\d*\.?\d*)?([a-zA-Z]\w*)?', term.strip())
        if match:
            coef_str, var = match.groups()
            
            if not var:  # Constant term
                continue
            
            if coef_str in ['', '+']:
                coef = 1
            elif coef_str == '-':
                coef = -1
            else:
                coef = float(coef_str)
            
            coefficients[var] = coef
    
    return coefficients

def parse_constraint(constraint):
    """Parse a constraint string into LHS, operator, and RHS."""
    if '<=' in constraint:
        lhs, rhs = constraint.split('<=')
        op = '<='
    elif '>=' in constraint:
        lhs, rhs = constraint.split('>=')
        op = '>='
    elif '=' in constraint:
        lhs, rhs = constraint.split('=')
        op = '='
    else:
        raise ValueError(f"Invalid constraint: {constraint}")
    
    return lhs.strip(), op, float(rhs.strip())

def solve_graphical(problem_data):
    """Solve a linear programming problem using the Graphical method."""
    objective_function = problem_data['objective_function']
    objective_type = problem_data['objective_type']
    constraints = problem_data['constraints']
    
    # First, solve using PuLP to get the optimal solution
    if objective_type == 'maximize':
        prob = LpProblem("GraphicalProblem", LpMaximize)
    else:
        prob = LpProblem("GraphicalProblem", LpMinimize)
    
    # Parse the objective function to get coefficients
    obj_coeffs = parse_expression(objective_function)
    
    # Check if we have exactly 2 variables for graphical method
    if len(obj_coeffs) != 2:
        raise ValueError("Graphical method requires exactly 2 variables")
    
    # Get the variable names
    var_names = list(obj_coeffs.keys())
    x_var_name, y_var_name = var_names
    
    # Create variables
    variables = {}
    for var_name in var_names:
        variables[var_name] = LpVariable(var_name, lowBound=0)
    
    # Add objective function
    prob += sum(obj_coeffs[var_name] * variables[var_name] for var_name in var_names)
    
    # Parse constraints and add to the problem
    constraint_lines = []
    for constraint in constraints:
        lhs, op, rhs = parse_constraint(constraint)
        lhs_coeffs = parse_expression(lhs)
        
        # Add the constraint to the LP problem
        if op == '<=':
            prob += sum(lhs_coeffs.get(var_name, 0) * variables[var_name] for var_name in var_names) <= rhs
        elif op == '>=':
            prob += sum(lhs_coeffs.get(var_name, 0) * variables[var_name] for var_name in var_names) >= rhs
        elif op == '=':
            prob += sum(lhs_coeffs.get(var_name, 0) * variables[var_name] for var_name in var_names) == rhs
        
        # Store the constraint for plotting
        a = lhs_coeffs.get(x_var_name, 0)
        b = lhs_coeffs.get(y_var_name, 0)
        constraint_lines.append((a, b, rhs, op))
    
    # Solve the problem
    prob.solve()
    
    # Generate the graphical solution
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Find the bounds for the plot
    max_bound = 10  # Default
    if prob.status == 1:  # Optimal solution found
        x_opt = value(variables[x_var_name])
        y_opt = value(variables[y_var_name])
        max_bound = max(max_bound, x_opt * 1.5, y_opt * 1.5)
    
    # Set up the plot
    x = np.linspace(0, max_bound, 1000)
    
    # Plot each constraint
    for i, (a, b, c, op) in enumerate(constraint_lines):
        if b == 0:
            # Vertical line
            if a != 0:
                x_val = c / a
                ax.axvline(x=x_val, color=f'C{i}', label=f'Constraint {i+1}')
        else:
            # Plot the line
            y = (c - a * x) / b
            ax.plot(x, y, label=f'Constraint {i+1}')
            
            # Shade the feasible region
            if op == '<=':
                y_test = (c - a * max_bound/2) / b
                test_point = (max_bound/2, y_test - 1 if b > 0 else y_test + 1)
            else:  # '>='
                y_test = (c - a * max_bound/2) / b
                test_point = (max_bound/2, y_test + 1 if b > 0 else y_test - 1)
    
    # Add non-negativity constraints
    ax.axvline(x=0, color='black', linestyle='-', alpha=0.3)
    ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    
    # Plot the optimal solution if found
    if prob.status == 1:  # Optimal solution found
        ax.plot(x_opt, y_opt, 'ro', markersize=10, label='Optimal Solution')
        ax.annotate(f'({x_opt:.2f}, {y_opt:.2f})', 
                    (x_opt, y_opt), 
                    xytext=(10, 10), 
                    textcoords='offset points')
    
    # Plot the objective function
    if obj_coeffs[x_var_name] != 0 and obj_coeffs[y_var_name] != 0:
        # Plot a few objective function lines
        z_values = np.linspace(0, value(prob.objective) * 1.5, 5)
        for z in z_values:
            y_obj = (z - obj_coeffs[x_var_name] * x) / obj_coeffs[y_var_name]
            ax.plot(x, y_obj, 'g--', alpha=0.3)
        
        # Plot the optimal objective function line
        if prob.status == 1:
            z_opt = value(prob.objective)
            y_obj_opt = (z_opt - obj_coeffs[x_var_name] * x) / obj_coeffs[y_var_name]
            ax.plot(x, y_obj_opt, 'g-', label=f'Objective (z={z_opt:.2f})')
    
    # Set up the plot
    ax.set_xlim(0, max_bound)
    ax.set_ylim(0, max_bound)
    ax.set_xlabel(x_var_name)
    ax.set_ylabel(y_var_name)
    ax.set_title('Graphical Solution')
    ax.grid(True)
    ax.legend()
    
    # Save the plot to a base64 string
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plot_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close()
    
    # Prepare the solution
    solution = {
        'status': LpStatus[prob.status],
        'objective_value': value(prob.objective) if prob.status == 1 else None,
        'variables': {var_name: value(var) for var_name, var in variables.items()},
        'plot': plot_data
    }
    
    return solution