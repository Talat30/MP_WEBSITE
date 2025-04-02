import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import OptimizationProblem, CustomJSONEncoder
from .solvers.simplex_solver import solve_simplex
from .solvers.graphical_solver import solve_graphical
from .solvers.transportation_solver import solve_transportation
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from scipy.optimize import linprog

# Custom JSON encoder to handle booleans
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bool):
            return int(obj)  # Convert True -> 1, False -> 0
        return super().default(obj)

def home(request):
    return render(request, 'optimizer/home.html')

def simplex_view(request):
    if request.method == 'POST':
        try:
            # Parse form data
            objective_function = request.POST.get('objective_function')
            objective_type = request.POST.get('objective_type')
            constraints = request.POST.getlist('constraints[]')
            
            # Prepare problem data
            problem_data = {
                'objective_function': objective_function,
                'objective_type': objective_type,
                'constraints': constraints
            }
            
            # Solve the problem
            solution = solve_simplex(problem_data)

            # Convert to JSON-serializable format
            problem_data_json = json.dumps(problem_data)
            solution_json = json.dumps(solution)

            # Create problem instance
            problem = OptimizationProblem.objects.create(
                title=f"Simplex Problem - {objective_type}",
                method='simplex',
                problem_data=problem_data_json,
                solution=solution_json
            )
            
            return redirect('results', problem_id=problem.id)
        except Exception as e:
            return render(request, 'optimizer/simplex.html', {'error': str(e)})
    
    return render(request, 'optimizer/simplex.html')

def graphical_view(request):
    if request.method == 'POST':
        try:
            # Parse form data
            objective_function = request.POST.get('objective_function')
            objective_type = request.POST.get('objective_type')
            constraints = request.POST.getlist('constraints[]')
            
            # Prepare problem data
            problem_data = {
                'objective_function': objective_function,
                'objective_type': objective_type,
                'constraints': constraints
            }
            
            # Solve the problem
            solution = solve_graphical(problem_data)

            # Convert to JSON-serializable format
            problem_data_json = json.dumps(problem_data)
            solution_json = json.dumps(solution)

            # Create problem instance
            problem = OptimizationProblem.objects.create(
                title=f"Graphical Problem - {objective_type}",
                method='graphical',
                problem_data=problem_data_json,
                solution=solution_json
            )
            
            return redirect('results', problem_id=problem.id)
        except Exception as e:
            return render(request, 'optimizer/graphical.html', {'error': str(e)})
    
    return render(request, 'optimizer/graphical.html')

# def transportation_view(request):
#     if request.method == 'POST':
#         try:
#             # Parse form data
#             sources = int(request.POST.get('sources'))
#             destinations = int(request.POST.get('destinations'))
            
#             supply = [float(request.POST.get(f'supply_{i}')) for i in range(sources)]
#             demand = [float(request.POST.get(f'demand_{j}')) for j in range(destinations)]
            
#             costs = []
#             for i in range(sources):
#                 row = [float(request.POST.get(f'cost_{i}_{j}')) for j in range(destinations)]
#                 costs.append(row)
            
#             # Prepare problem data
#             problem_data = {
#                 'supply': supply,
#                 'demand': demand,
#                 'costs': costs
#             }

#             # Solve the problem
#             solution = solve_transportation(problem_data)

#             # Convert to JSON-serializable format
#             problem_data_json = json.dumps(problem_data)
#             solution_json = json.dumps(solution)

#             # Create problem instance
#             problem = OptimizationProblem.objects.create(
#                 title="Transportation Problem",
#                 method='transportation',
#                 problem_data=problem_data_json,
#                 solution=solution_json
#             )
            
#             return redirect('results', problem_id=problem.id)
#         except Exception as e:
#             return render(request, 'optimizer/transportation.html', {'error': str(e)})
    
#     return render(request, 'optimizer/transportation.html')


def transportation_view(request):
    if request.method == 'POST':
        try:
            # Parse form data
            sources = int(request.POST.get('sources'))
            destinations = int(request.POST.get('destinations'))
            
            supply = [float(request.POST.get(f'supply_{i}')) for i in range(sources)]
            demand = [float(request.POST.get(f'demand_{j}')) for j in range(destinations)]
            
            costs = []
            for i in range(sources):
                row = [float(request.POST.get(f'cost_{i}_{j}')) for j in range(destinations)]
                costs.append(row)
            
            # Prepare problem data
            problem_data = {
                'supply': supply,
                'demand': demand,
                'costs': costs
            }

            # Solve the problem
            solution = solve_transportation(problem_data)

            # Convert to JSON-serializable format using CustomJSONEncoder
            problem_data_json = json.dumps(problem_data, cls=CustomJSONEncoder)
            solution_json = json.dumps(solution, cls=CustomJSONEncoder)

            # Create problem instance
            problem = OptimizationProblem.objects.create(
                title="Transportation Problem",
                method='transportation',
                problem_data=problem_data_json,
                solution=solution_json
            )
            
            return redirect('results', problem_id=problem.id)
        except Exception as e:
            return render(request, 'optimizer/transportation.html', {'error': str(e)})
    
    return render(request, 'optimizer/transportation.html')

def results_view(request, problem_id):
    problem = get_object_or_404(OptimizationProblem, id=problem_id)

    # Deserialize JSON data before passing to template
    problem_data = json.loads(problem.problem_data)
    solution = json.loads(problem.solution) if problem.solution else None

    context = {
        'problem': problem,
        'problem_data': problem_data,
        'solution': solution,
        'method': problem.method
    }

    return render(request, 'optimizer/results.html', context)

def results_view(request, problem_id):
    problem = get_object_or_404(OptimizationProblem, id=problem_id)

    # Deserialize JSON data before passing to template
    problem_data = json.loads(problem.problem_data)
    solution = json.loads(problem.solution) if problem.solution else None

    context = {
        'problem': problem,
        'problem_data': problem_data,
        'solution': solution,
        'method': problem.method
    }

    return render(request, 'optimizer/results.html', context)
