# from django.db import models

# class OptimizationProblem(models.Model):
#     METHOD_CHOICES = [
#         ('simplex', 'Simplex Method'),
#         ('graphical', 'Graphical Method'),
#         ('transportation', 'Transportation Problem'),
#     ]
    
#     title = models.CharField(max_length=200)
#     method = models.CharField(max_length=20, choices=METHOD_CHOICES)
#     problem_data = models.JSONField()
#     solution = models.JSONField(null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
    
#     def __str__(self):
#         return f"{self.title} ({self.method})"
import json
from django.db import models

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bool):  # Handle boolean values
            return int(obj)  # Convert True -> 1, False -> 0
        return super().default(obj)

class OptimizationProblem(models.Model):
    METHOD_CHOICES = [
        ('simplex', 'Simplex Method'),
        ('graphical', 'Graphical Method'),
        ('transportation', 'Transportation Problem'),
    ]
    
    title = models.CharField(max_length=200)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    problem_data = models.JSONField()
    solution = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Ensure problem_data and solution are JSON serializable
        if isinstance(self.problem_data, str):
            self.problem_data = json.loads(self.problem_data)
        if isinstance(self.solution, str):
            self.solution = json.loads(self.solution)

        # Convert bool values to integers before saving
        self.problem_data = json.dumps(self.problem_data, cls=CustomJSONEncoder)
        self.solution = json.dumps(self.solution, cls=CustomJSONEncoder) if self.solution else None

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.method})"