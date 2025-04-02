import numpy as np
from pulp import LpMaximize, LpMinimize, LpProblem, LpVariable, LpStatus, value
import re

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

def solve_simplex(problem_data):
    """Solve a linear programming problem using the Simplex method."""
    objective_function = problem_data['objective_function']
    objective_type = problem_data['objective_type']
    constraints = problem_data['constraints']
    
    # Create the LP problem
    if objective_type == 'maximize':
        prob = LpProblem("LinearProgrammingProblem", LpMaximize)
    else:
        prob = LpProblem("LinearProgrammingProblem", LpMinimize)
    
    # Parse the objective function to get coefficients
    obj_coeffs = parse_expression(objective_function)
    
    # Create variables
    variables = {}
    for var_name in obj_coeffs.keys():
        variables[var_name] = LpVariable(var_name, lowBound=0)
    
    # Add objective function
    prob += sum(obj_coeffs[var_name] * variables[var_name] for var_name in obj_coeffs)
    
    # Add constraints
    for constraint in constraints:
        lhs, op, rhs = parse_constraint(constraint)
        lhs_coeffs = parse_expression(lhs)
        
        # Make sure all variables are defined
        for var_name in lhs_coeffs.keys():
            if var_name not in variables:
                variables[var_name] = LpVariable(var_name, lowBound=0)
        
        # Add the constraint
        if op == '<=':
            prob += sum(lhs_coeffs[var_name] * variables[var_name] for var_name in lhs_coeffs) <= rhs
        elif op == '>=':
            prob += sum(lhs_coeffs[var_name] * variables[var_name] for var_name in lhs_coeffs) >= rhs
        elif op == '=':
            prob += sum(lhs_coeffs[var_name] * variables[var_name] for var_name in lhs_coeffs) == rhs
    
    # Solve the problem
    prob.solve()
    
    # Prepare the solution
    solution = {
        'status': LpStatus[prob.status],
        'objective_value': value(prob.objective),
        'variables': {var_name: value(var) for var_name, var in variables.items()},
        'constraints': [str(constraint) for constraint in prob.constraints.values()]
    }
    
    return solution