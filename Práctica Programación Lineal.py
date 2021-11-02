#!/usr/bin/env python
# coding: utf-8

# <h1> <center>Práctica Programación Lineal</center> </h1> 
# <h2> <center> Alumnos: Florencia Ludueña, Paula Luvini, Facundo Marconi </center> </h2> 

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
# Creamos una clase llamada datos donde vamos a ingresar la cantidad de depósitos y de locales que tenemos. A partir de eso, vamos a obtener el stock y la demanda de cada establecimiento. Suponemos que el máximo posible de cada producto es de 200 unidades en los depósitos y 100 en los locales: esto podemos modificarlo si queremos.
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
                d.append(random.choice(np.arange(1,100)))
            self.demanda.append(d)
        
        from itertools import product
        self.combinaciones = list(product(depositos, locales))
        
        #Costos de productos por local y deposito
        
        rrows, rcols = len(self.demanda), len(self.stock)
        self.costos = [[[random.choice(np.arange(1,10)) for k in range(3)] for j in range(rrows)] for i in range(rcols)]
        
        #for comb in self.combinaciones:
        #    c = []
        #    for product in range(0,3):
        #        c.append(random.choice(np.arange(1,10)))
        #    self.costos.append(c)


# In[3]:


f = datos(4,5)
print("Demanda por local: ", f.demanda)
print("Stock por depósito: ", f.stock)
print("Costos por producto y por combinación", f.costos)


# #### 2. Modelar mediante Programación Lineal el problema de transporte propuesto.

# Objetivo: minimizar los costos. Y los costos son por cada uno de los productos dada una combinación de local y depósito. Constraints: Stock y demanda.
# 
# **Ejemplo manual con 1 tienda y 1 centro de almacenaje:**
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
# no-negatividad
#     
#     x1,2,3 >= 0
#     
# los stocks y demandas:
# 
#     1 <= x1 <= 2
#     4 <= x2 <= 5
#     4 <= x3 <= 6
#     
#     
# Para el caso genérico con n depósitos y m locales:
# 
# $ Min: \sum_{i=1}^{n} \sum_{j=1}^{m} \sum_{p=1}^{P} c_{pij}x_{pij} $
# 
# $s.a.:$
# 
# $\sum_{i=1}^{n} \sum_{j=1}^{m} \sum_{p=1}^{P} x_{pij} \leq S_{pi} $
# 
# $\sum_{i=1}^{n} \sum_{j=1}^{m} \sum_{p=1}^{P} x_{pij} \geq D_{pj} $
# 
# $ x_{pij} \geq 0 $
# 
# $ donde: $
# 
# $ c_{pij}:$ es el costo de envío por producto, tienda y depósito. 
# 
# $ x_{pij}:$ es la cantidad enviada por producto, tienda y depósito.
# 
# $ S_{pi}:$ es el stock de cada producto en cada depósito.
# 
# $ D_{pj}:$ es la demanda de cada producto en cada tienda.

# #### 3. Implementar el modelo utilizando Google OR-Tools.

# In[4]:


from ortools.linear_solver import pywraplp


# In[5]:


def LinearProgramming(demanda, stock, costos):
    rrows, rcols = len(demanda), len(stock)

    # Create the linear solver with the SCIP backend.
    solver = pywraplp.Solver.CreateSolver('SCIP')
    
    # Create the variables x: x_ij.
    x = {}
    for s in range(rcols): #deposito
        for d in range(rrows):  #local 
            for p in range(3):
                #Here I am already including the non-negativity constraint: x must be greater than 0
                x[(s,d,p)] = solver.IntVar(0, 200, 'x[%i][%i][%i]' % (s, d, p))  

    num_var = solver.NumVariables()

    print('Number of variables =', solver.NumVariables())
    
    # Create the linear constraints, stock: menor o igual. Demanda: mayor o igual
    for s in range(rcols): # depositos
        for p in range(3):
            solver.Add(solver.Sum([x[(s,d,p)] for d in range(rrows)]) <= float(stock[s][p]))

    for d in range(rrows): # locales
        for p in range(3):  # productos
            solver.Add(solver.Sum([x[(s,d,p)] for s in range(rcols)]) == float(demanda[d][p]))

    print('Number of constraints =', solver.NumConstraints())

    # Objective function
    objective_terms = []
    for s in range(rcols): #deposito
        for d in range(rrows):  #local 
            for p in range(3):   #producto
                objective_terms.append(x[(s,d,p)]*float(costos[s][d][p]))
    solver.Minimize(solver.Sum(objective_terms))

    # Solve
    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        print('Total cost = ', solver.Objective().Value(), '\n')
        for s in range(rcols):
            for d in range(rrows):
                for p in range(3):
                    print('Product %d in storage %d assigned to store %d: Cost = %d' % ((p+1), (s+1), (d+1), costos[s][d][p]), 'Quantity =', x[(s,d,p)].solution_value())
                
    print('Problem solved in %f milliseconds' % solver.wall_time())
    print('Problem solved in %d iterations' % solver.iterations())
    print('Problem solved in %d branch-and-bound nodes' % solver.nodes())

    # Check that the problem has an optimal solution.
    if status != solver.OPTIMAL:
        print('The problem does not have an optimal solution!')
        if status == solver.FEASIBLE:
            print('A potentially suboptimal solution was found.')
            print('Problem solved in %f milliseconds' % solver.wall_time())
        else:
            print('The solver could not solve the problem.')
            print('Problem solved in %f milliseconds' % solver.wall_time())
            exit(1)


# In[6]:


#Vamos a confirmar con este ejemplo sencillo que funciona nuestro algoritmo

demanda_test = [[35, 31, 68]]
stock_test = [[168, 21, 185], [198, 106, 150]]
costos_test = [[[6, 9, 6]], [[1, 7, 9]]]
print("Demanda por local: ", demanda_test)
print("Stock por depósito: ", stock_test)
print("Costos por producto y por combinación", costos_test)


# In[7]:


LinearProgramming(demanda_test, stock_test, costos_test)


# Ahora chequeamos si la asignación es eficiente y por menores costos de tienda-depósito. Entonces por ejemplo tomamos la demanda del producto 1 de la tienda 3: 82
# ¿Cómo es esto asignado? Vemos según la resolución:
# * Product 1 in storage 1 assigned to store 3: Cost = 5 Quantity = 58.0
# * Product 1 in storage 3 assigned to store 3: Cost = 8 Quantity = 24.0
# 
# 58 se obtienen del depósito cuya costo de envío a la tienda 3 es 5 y los restantes 24 se obtienen del depósito 3 cuyo costo de envío es 8.
# 
# Si miramos cómo son los costos de los 5 depósitos con la tienda 3 para el producto 1 vemos que estos son: 5, 8, 8, 9 y 9. Es decir, el primer depósito es el más barato para esta tienda y por ello obtiene de allí 58 unidades. Las 24 restantes vienen del depósito 3 cuyos costos son los siguientes más baratos.

# In[8]:


demanda_test2 = [[42, 92, 37], [30, 30, 3], [82, 43, 35]]
stock_test2 = [[58, 131, 64], [66, 188, 160], [167, 30, 183], [147, 17, 189], [130, 85, 64]]
costos_test2 = [[[6, 5, 3], [5, 5, 8], [5, 3, 8]], [[5, 4, 1], [4, 4, 6], [8, 6, 9]], [[5, 5, 5], [2, 6, 3], [8, 7, 5]], [[7, 6, 8], [9, 5, 9], [9, 1, 7]], [[9, 5, 5], [6, 4, 1], [9, 2, 3]]]
print("Demanda por local: ", demanda_test2)
print("Stock por depósito: ", stock_test2)
print("Costos por producto y por combinación", costos_test2)


# In[9]:


print(demanda_test2[2][0])


# In[10]:


costos_test2


# In[11]:


LinearProgramming(demanda_test2, stock_test2, costos_test2)


# #### 4. Experimentar con las instancias para analizar los tiempos de cómputo requeridos para resolver el problema con diferentes cantidades de depósitos y locales.
# 
# Para esto, basta con que tomemos la clase datos y que ingresemos el número de depósitos o tiendas que deseemos.

# Ahora voy a probar resolver el problema con más tiendas y depósitos. Comprobamos en el print que hacemos al final de la optimización, que el tiempo de procesamiento aumenta linealmente con la cantidad de nuevos establecimientos, es decir que son varios minutos.

# In[12]:


f = datos(500,300)
LinearProgramming(f.demanda, f.stock, f.costos)


# El problema presentado está íntimamente relacionado con el Problema de Asignación. Este problema también se puede resolver con un modelo de Programación Lineal, pero también existen algoritmos procedurales para resolver directamente el problema. Por
# ejemplo, el Algoritmo Húngaro es un algoritmo que sirve para resolver el Problema de Asignación en un tiempo polinomial. ¿Por qué podría seguir siendo interesante el uso de un modelo de Programación Lineal para atacar el problema?
# 
# En el caso de algoritmos procedurales, si bien pueden resolver nuestro problema están diseñados proceduralmente para ser una solución única a ese problema. Es decir, el Algoritmo Húngaro podrá resolver el Problema de Asignación pero pierde generalidad a la hora de resolver otros problemas. A medida que nos abstraemos, avanzando hacia heurísticas y metaheurísticas podremos resolver una mayor cantidad de problemas con el mismo procedimiento. Tal es así que en un algoritmo genético una función objetivo lineal puede significar muchas aplicaciones distintas. Programación Lineal es el mayor nivel de abstracción que podemos alcanzar en este sentido.
# 
# Programación Lineal además va a ser relevante para resolver estos problemas porque nos va a brindar una solución **exacta**. Si bien ciertos algoritmos o metaheurísticas proponen aproximaciones muy buenas y que se resuelven en un tiempo atractivo, muchas veces las soluciones distan de ser las mejores.

# #### Fuentes y posts consultados:
# 
# * Google OR Tools documentation: https://developers.google.com/optimization/lp/lp_example?hl=en
# * https://pysal.org/spaghetti/notebooks/transportation-problem.html
# * https://towardsdatascience.com/operations-research-in-r-transportation-problem-1df59961b2ad
