#!/usr/bin/env python
# coding: utf-8

# <h1> <center>Práctica Programación Lineal</center> </h1> 

# En esta práctica el objetivo es resolver una situación particular del Transportation Problem.
# 
# Nuestra empresa tiene n depósitos y m locales de venta. Para simplificar, vamos a asumir que solo hay tres tipos de productos a comercializar. Por cada uno de los productos tendremos la información del stock disponible en cada depósito. Además, tendremos la demanda de cada local. Por último, por cada tipo de producto y por cada par depósito-local, tendremos el costo de enviar una unidad de mercadería.
# 
# El objetivo es encontrar la forma óptima de transporte desde los depósitos a los locales, cumpliendo las restricciones de stock y demanda. Se entiende por óptima a la forma que menor costo asociado tenga.

# In[2]:


import random
import numpy as np
from itertools import product


# #### 1. Crear diversas instancias con varios depósitos y locales para experimentar.
# 
# Creamos una clase llamada datos donde vamos a ingresar la cantidad de depósitos y de locales que tenemos, estos los elegimos de manera aleatoria poniendo un máximo de cantidad de locales y de depósitos. A partir de eso, vamos a obtener el stock y la demanda de cada establecimiento. Suponemos que el máximo posible de cada producto es de 200 unidades.
# 
# También calculamos las combinaciones posibles entre locales y los costos entre ellas.

# In[1]:


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


# In[4]:


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

# In[8]:


from ortools.linear_solver import pywraplp


# In[9]:


#En primer lugar hago un ejemplo a mano

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


# Ahora hago un ejemplo con todos

# In[97]:


f = datos(5,5)
print("Demanda por local: ", f.demanda)
print("Stock por depósito: ", f.stock)
print("Combinaciones posibles entre depósitos y locales", f.combinaciones)
print("Costos por producto y por combinación", f.costos)


# In[99]:


f.demanda


# In[109]:


matriz = np.empty((4,3))

for prod in range(3):
    demanda = []
    for local in range(4):
        #print(f.demanda[local][prod])
        demanda.append(f.demanda[local][prod])
    print(demanda)
#for i in np.array(f.combinaciones):
#    matriz.append(list(i))
#    matriz.append(f.stock[i[0]-1])
#    matriz.append(f.demanda[i[1]-1])


# In[14]:


print("Total de combinaciones posibles: ", len(f.combinaciones))

resultados = []
t=0
#Optimize all the combinations and scenarios
for a in f.combinaciones:
    t = t + 1
    # Create the linear solver with the GLOP backend.
    solver = pywraplp.Solver.CreateSolver('GLOP')

    # Create the variables x and y.
    x1 = solver.NumVar(0, 10, 'x1')
    x2 = solver.NumVar(0, 10, 'x2')
    x3 = solver.NumVar(0, 10, 'x3')
    
    # Create the linear constraints, a <= x1 <= b
    ct = solver.Constraint(float(f.demanda[a[1]-1][0]),float(f.stock[a[0]-1][0]), 'ct')
    ct.SetCoefficient(x1, 1)
    
    # Create the linear constraints, a <= x2 <= b
    ct = solver.Constraint(float(f.demanda[a[1]-1][1]), float(f.stock[a[0]-1][1]), 'ct')
    ct.SetCoefficient(x2, 1)
   
    # Create the linear constraints, a <= x3 <= b
    ct = solver.Constraint(float(f.demanda[a[1]-1][2]), float(f.stock[a[0]-1][2]), 'ct')
    ct.SetCoefficient(x3, 1)
    
    # Create the linear constraints, a <= x1 <= b
    ct = solver.Constraint(float(f.demanda[a[1]-1][0]),float(f.stock[a[0]-1][0]), 'ct')
    ct.SetCoefficient(x1, 1)
    
    # Create the linear constraints, a <= x2 <= b
    ct = solver.Constraint(float(f.demanda[a[1]-1][1]), float(f.stock[a[0]-1][1]), 'ct')
    ct.SetCoefficient(x2, 1)
   
    # Create the linear constraints, a <= x3 <= b
    ct = solver.Constraint(float(f.demanda[a[1]-1][2]), float(f.stock[a[0]-1][2]), 'ct')
    ct.SetCoefficient(x3, 1)
        
    print('Number of constraints =', solver.NumConstraints())
    
    # Create the objective function: cx1 + dx2 + ex3
    objective = solver.Objective()
    objective.SetCoefficient(x1, float(f.costos[t-1][0]))
    objective.SetCoefficient(x2, float(f.costos[t-1][1]))
    objective.SetCoefficient(x3, float(f.costos[t-1][2]))
    objective.SetMinimization()
    
    solver.Solve()
        
        
    print('Solution:')
    print('Objective value =', objective.Value())
    print('x1 =', x1.solution_value())
    print('x2 =', x2.solution_value())
    print('x3 =', x3.solution_value())
    r = [x1.solution_value(), x2.solution_value(), x3.solution_value(), objective.Value()]
    resultados.append(r)


# In[24]:


#Me quedo con la combinacion que minimiza el costo, es decir la anteultima
np.where((result[3]==np.min(result[3])))


# In[25]:


np.min(result[3])


# In[ ]:




