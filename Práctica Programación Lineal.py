#!/usr/bin/env python
# coding: utf-8

# <h1> <center>Práctica Programación Lineal</center> </h1> 

# En esta práctica el objetivo es resolver una situación particular del Transportation Problem.
# 
# Nuestra empresa tiene n depósitos y m locales de venta. Para simplificar, vamos a asumir que solo hay tres tipos de productos a comercializar. Por cada uno de los productos tendremos la información del stock disponible en cada depósito. Además, tendremos la demanda de cada local. Por último, por cada tipo de producto y por cada par depósito-local, tendremos el costo de enviar una unidad de mercadería.
# 
# El objetivo es encontrar la forma óptima de transporte desde los depósitos a los locales, cumpliendo las restricciones de stock y demanda. Se entiende por óptima a la forma que menor costo asociado tenga.

# In[1]:


import random
import numpy as np
from itertools import product


# #### 1. Crear diversas instancias con varios depósitos y locales para experimentar.
# 
# Creamos una clase llamada datos donde vamos a ingresar la cantidad de depósitos y de locales que tenemos, estos los elegimos de manera aleatoria poniendo un máximo de cantidad de locales y de depósitos. A partir de eso, vamos a obtener el stock y la demanda de cada establecimiento. Suponemos que el máximo posible de cada producto es de 200 unidades.
# 
# También calculamos las combinaciones posibles entre locales y los costos entre ellas.

# In[2]:


class datos():
    def __init__(self, nro_dep, nro_loc):
        #n = random.choice(np.arange(1,max_dep)) #depositos
        depositos = np.arange(1,nro_dep+1)
        #m = random.choice(np.arange(1,max_loc)) #locales
        locales = np.arange(1,nro_loc+1)
        print("Locales: ", nro_loc, "Depositos: ",nro_dep)
    
        #Stock de cada deposito
        self.stock = []
        for s in range(0,nro_dep):
            s = []
            for product in range(0,3):
                s.append(random.choice(np.arange(1,200)))
            self.stock.append(s)

        #Demanda de cada local
        self.demanda = []
        for l in range(0,nro_loc):
            d = []
            for product in range(0,3):
                d.append(random.choice(np.arange(1,200)))
            self.demanda.append(d)
        
        from itertools import product
        self.combinaciones = list(product(depositos, locales))
        
        #Costos de productos por local
        self.costos = []
        for comb in self.combinaciones:
            c = []
            for product in range(0,3):
                c.append(random.choice(np.arange(1,10)))
            self.costos.append(c)


# In[3]:


f = datos(5,5)
print("Demanda por local: ", f.demanda)
print("Stock por depósito: ", f.stock)
print("Combinaciones posibles entre locales y depósitos", f.combinaciones)
print("Costos por producto y por combinación", f.costos)


# #### 2. Modelar mediante Programación Lineal el problema de transporte propuesto.

# Objetivo: minimizar los costos. Y los costos son por cada uno de los productos dada una combinación de local y depósito. Constraints: Stock y demanda.
# 
# **Ejemplo manual:**
# 
# * Productos: x1, x2, x3
# * Locales:  1 Depositos:  1
# * Demanda por local:  [[1, 4, 4]]
# * Stock por depósito:  [[2, 5, 6]]
# * Combinaciones posibles entre locales y depósitos [(1, 1)]
# * Costos por producto y por combinación [[6, 9, 1]]
# 
# F.O.:
# 
#     min 6x1 + 9x2 + x3
# 
# s.a.:
# 
# los stocks y demandas:
# 
#     1 <= x1 <= 2
#     4 <= x2 <= 5
#     4 <= x3 <= 6

# #### 3. Implementar el modelo utilizando Google OR-Tools.
# 
# Aca hay data de como hacerlo con arrays: https://developers.google.com/optimization/mip/mip_var_array
# 
# Este post lo hace sonar MUY facil: https://towardsdatascience.com/operations-research-in-r-transportation-problem-1df59961b2ad

# In[4]:


from ortools.linear_solver import pywraplp


# In[5]:


#En primer lugar hago un ejemplo a mano, con 1 deposito y 1 local

def main():
    # Create the linear solver with the GLOP backend.
    solver = pywraplp.Solver.CreateSolver('GLOP')

    # Create the variables x and y.
    x1 = solver.NumVar(0, 10, 'x1')
    x2 = solver.NumVar(0, 10, 'x2')
    x3 = solver.NumVar(0, 10, 'x3')

    print('Number of variables =', solver.NumVariables())

    # Create the linear constraints, 1 <= x1 <= 2
    ct = solver.Constraint(1, 2, 'ct')
    ct.SetCoefficient(x1, 1)

    # Create the linear constraints, 4 <= x2 <= 5
    ct = solver.Constraint(4, 5, 'ct')
    ct.SetCoefficient(x2, 1)
    
    # Create the linear constraints, 4 <= x3 <= 6
    ct = solver.Constraint(4, 6, 'ct')
    ct.SetCoefficient(x3, 1)
    
    print('Number of constraints =', solver.NumConstraints())
    
    # Create the objective function, 6x1 + 9x2 + x3
    objective = solver.Objective()
    objective.SetCoefficient(x1, 6)
    objective.SetCoefficient(x2, 9)
    objective.SetCoefficient(x3, 3)
    objective.SetMinimization()

    solver.Solve()

    print('Solution:')
    print('Objective value =', objective.Value())
    print('x1 =', x1.solution_value())
    print('x2 =', x2.solution_value())
    print('x3 =', x3.solution_value())


if __name__ == '__main__':
    main()


# In[6]:


f = datos(5,5)
print("Demanda por local: ", f.demanda)
print("Stock por depósito: ", f.stock)
print("Combinaciones posibles entre depósitos y locales", f.combinaciones)
print("Costos por producto y por combinación", f.costos)


# In[17]:


resultados = []
# Create the linear solver with the GLOP backend.
solver = pywraplp.Solver.CreateSolver('GLOP')

# Create the variables x and y.
x = {}
for j in range(3):
    x[j] = solver.IntVar(0, 200, 'x[%i]' % j)  #Here I am already including the non-negativity constraint: x must be greater than 0
print('Number of variables =', solver.NumVariables())
    
# Create the linear constraints, stock: menor o igual
for p in range(3):
    for i in range(5):
        constraint = solver.RowConstraint(0, float(f.stock[i][p]), 'ct')
        constraint.SetCoefficient(x[j], 1)

# Create the linear constraints, demanda: igual
for p in range(3):
    for i in range(5):
        constraint = solver.RowConstraint(float(f.demanda[i][p]), float(f.demanda[i][p]), 'ct')
        constraint.SetCoefficient(x[j], 1)
print('Number of constraints =', solver.NumConstraints())


objective = solver.Objective()
for i in range(len(f.costos)):
    for p in range(3):
        objective.SetCoefficient(x[p], float(f.costos[i][p]))
objective.SetMinimization()
solver.Solve()
status = solver.Solve() 
        
print('Solution:')
print('Objective value =', objective.Value())

for p in range(3):
    print('x1 =', x[j].solution_value())
#r = [x1.solution_value(), x2.solution_value(), x3.solution_value(), objective.Value()]

# Check that the problem has an optimal solution.
if status != solver.OPTIMAL:
    print('The problem does not have an optimal solution!')
    if status == solver.FEASIBLE:
        print('A potentially suboptimal solution was found.')
    else:
        print('The solver could not solve the problem.')
        exit(1)


# In[ ]:





# In[ ]:




