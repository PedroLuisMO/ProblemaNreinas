import math
import random
from matplotlib import pyplot as plt
import sys
import tkinter
from tkinter import *
from tkinter import messagebox
import pygame
from pygame.locals import *

def generaIndividuos(lim_inf, lim_sup, individuos, longitud):
    #Genera individuos de tam = longitud entre lim_inf = 0 y lim_sup = (Reinas-1)
    individuo = [] #individuo es una lista
    generacion = [] #generacion es una lista de listas
    for i in range(individuos):
        individuo.clear()
        for j in range (longitud):
            x = random.randint(lim_inf, lim_sup)
            individuo.append(x)
        generacion.append(individuo.copy())
    return generacion

def posicionesBuenas(generacionActual, individuos, longitud):
    '''la posicion del arreglo corrresponde a la columna, por ende aseguramos que nunca habra dos reinas en la misma columna
    mientras que el valor de cada posicion representa la fila
    solo nos interesa verificar que no haya mas de una reina por fila y comprobar las diagonales'''
    cubeta = []  #requerimos de un vector cubeta para saber el numero de posiciones (filas) repetidas
    v_individuo = [] # vector para copiar a un solo individuo
    v_fitness = []
    v_unos = []
    flag = False
    for i in range (individuos):
        v_individuo=generacionActual[i] #obtenemos al individuo i de la generacion
        cubeta.clear()
        for j in range (longitud): #llenamos la cubeta en 0 por cada individuo
            cubeta.append(0)
        #verificacion que no esten en el mismo renglon lo ideal es tener 1 reina por fila 
        for j in range (longitud): #llenamos la cubeta en las posiciones que se tiene
            cubeta[v_individuo[j]] +=1
        unos = cubeta.count(1) #contamos cuantas reinas hay en una misma fila 
        k=0
        pos=0
        v_unos.clear()
        reinasListas = 0
        #encontramos las reinas que solo estan en una misma fila(con esto cumple que no ataca a nadie ni en columna ni por renglon solo falta la diagonal)
        while (k<unos):
            if cubeta[pos]==1:
                v_unos.append(pos)
                k+=1
            pos+=1
        #de las reinas que pueden ser potenciales para nuestra solucion verificamos que no se ataquen en las diagonales
        for j in range(unos):
            flag = False
            flag = revisaDiagonales(v_individuo,v_unos[j], longitud)
            if flag:
                reinasListas+=1
        v_fitness.append(reinasListas)
    return v_fitness
     
def revisaDiagonales(v_individuo,pos, longitud):
    '''
    verificamos la diagonal de cada reina la formula esta en: http://www.it.uc3m.es/jvillena/irc/practicas/06-07/06.pdf pagina 8 
    '''
    i=0
    flag = True
    while(i<longitud and flag):
        #solo verificamos las diagoles diferentes de cada reina si comprobamos la diagonal de cada reina siempre será 0 por eso omitimos comprobarla con ella misma
        if i != longitud-1 and i==pos:
            i+=1
        elif i==longitud-1 and i==pos:
            break
        if(abs(i-pos) == abs (v_individuo[i]-v_individuo[pos])):
            flag = False
        i+=1
    return flag

def seleccionPorRuleta(generacionActual, longitud, individuos):
    '''
    generacion actual posicion de cada individuo
    [0,longitud-1] = cromosomas
    [longitud] = reinasListas = fitness
    [longitud+1] = probabilidad
    [longitud+2] = acumulado
    Se escogio ruleta por la convergencia prematura, en 8 reinas, solo son 92 soluciones posibles entre 8^8 combinaciones posibles
    '''
    v_aux = []
    hijos = []
    suma = 0
    prom = 0
    suma1 = 0

    #calculamos la suma de todas las reinas listas mientras mas reinas listas mejor ponderacion
    for i in range(individuos):
        suma+=generacionActual[i][longitud]
    v_aux.clear()
    #calculamos probabilidad de cada individuo
    for i in range (individuos):
        prob = generacionActual[i][longitud] / suma
        generacionActual[i].append(round(prob,3))
    #calculamos el acumulado
    acumulado = 0
    suma_ve=0
    for i in range(individuos):
        acumulado+=round(generacionActual[i][longitud+1],3)
        generacionActual[i].append(acumulado)
        suma_ve+=round(acumulado,3)
    #por manejo de decimales puede darse que no sea 1 sino mayor como 1.01    
    if acumulado>=1:
        acumulado = 1
    suma_ve = round(suma_ve,3) #redondeamos a 3 decimales solamente 
    #escogemos a 2 padres por genracion
    for i in range(int(individuos//2)):
        flag = True
        while(flag):
            aleatorio = round(random.uniform(0,suma_ve),3) #se caclcula un aleatorio entre 0 y el valor esperado
            if(aleatorio<=1):
                flag=False
        if aleatorio >=0.99: #en el acumulado puede que no sea 1 sino 0.98 por ello se resta 
            aleatorio-=0.02
        flag = True
        j=0
        #escogemos al primer padre
        while (flag):
            if(aleatorio<=generacionActual[j][longitud+2]):
                pos = j
                flag = False
            j+=1
        flag = True
        rep = True #diferene del padre 1
        #escogemos un padre diferente al padre 1
        while(rep):
            flag=True
            while(flag):
                aleatorio = round(random.uniform(0,suma_ve),3) #se caclcula un aleatorio entre 0 y el valor esperado
                if(aleatorio<=1):
                    flag=False
            if aleatorio >= 0.99: #en el acumulado puede que no sea 1 sino 0.98 por ello se resta 
                aleatorio-=0.02
            j=0
            flag=True
            #Se escoge un padre 
            while (flag):
                if(aleatorio<=generacionActual[j][longitud+2]):
                    pos2 = j
                    flag = False
                j+=1
            #si el padre escogido es diferente al otro, termina el ciclo, sino repetimos hasta escoger 2 padres diferentes
            if pos != pos2:
                rep=False
        hijos.append(generacionActual[pos][0:longitud]) #solo copiamos a los cromosomas
        hijos.append(generacionActual[pos2][0:longitud])
    
    return hijos
        
def cruza2puntos(hijos,longitud, individuos):
    ls = longitud-1
    li = 0
    for i in range(int(individuos//2)):
        pc1 = random.randint(li,ls) #escogemos un punto de corte entre 0 y (reinas-1)
        flag = True
        #se escoge un punto de corte diferente al primero
        while (flag):
            pc2 = random.randint(li,ls)
            if pc2 != pc1:
                flag=False
        #puede que el segundo punto de corte es menor, por ello solo se cambian los valores entre pc1 y pc2
        if (pc2<pc1):
            aux = pc1
            pc1 = pc2
            pc2 = aux
        j = pc1
        #mientras el pc1 sea sea menor o igual a pc2 se cambian los valores de cada hijo 
        while (j <=pc2):
            hijos[(i*2)][j], hijos[(i*2)+1][j] = hijos[(i*2)+1][j], hijos[(i*2)][j]
            j+=1  

def mutacionEstandar(hijos, longitud, individuosMutan):
    ''' se escogio mutacion canonica por que puede modificar el valor de un solo cromosoma, a diferencia de solo permutarlo
    '''
    i = 1
    v_individuo = []
    posiciones = []
    aux = (len(hijos)) - 1
    x = random.randint(0,aux) #obtenemos el primer individuo a mutar de toda la generacion
    posiciones.append(x)
    #escogemos los demas individuos a mutar siempre y cuando no se repita alguno
    while i < individuosMutan:
        x = random.randint(0,aux)
        if x not in posiciones:
            posiciones.append(x)
            i+=1
    #mutacion de los individuos
    for i in range(individuosMutan):
        v_individuo = hijos[posiciones[i]] #obtenemos al individuo 
        pos = random.randint(0,longitud-1) #generamos la posicion que mutara
        nuevoValor = random.randint(0,longitud-1) #obtenemos el nuevo valor "cromosoma"
        v_individuo[pos] = nuevoValor #asignamos el nuevo cromosoma en la posicione seleccionada
        hijos[posiciones[i]] = v_individuo.copy() #reemplazamos al hijo por el mutado

def mutacionIntercambio(hijos, longitud, individuosMutan):
    i = 1
    v_individuo = []
    posiciones = []
    aux = (len(hijos)) - 1
    x = random.randint(0,aux) #obtenemos el primer individuo a mutar de toda la generacion
    posiciones.append(x)
    #escogemos los demas individuos a mutar siempre y cuando no se repita alguno
    while i < individuosMutan:
        x = random.randint(0,aux)
        if x not in posiciones:
            posiciones.append(x)
            i+=1
    #mutacion de los individuos
    for i in range(individuosMutan):
        v_individuo = hijos[posiciones[i]] #obtenemos al individuo 
        pos1 = random.randint(0,longitud-1) #generamos la posicion que mutara
        flag = True
        while (flag):
            pos2 = random.randint(0,longitud-1) #obtenemos el nuevo valor "cromosoma"
            if pos2 != pos1:
                flag = False
        v_individuo[pos1], v_individuo[pos2] = v_individuo[pos2], v_individuo[pos1]
        hijos[posiciones[i]] = v_individuo.copy() #reemplazamos al hijo por el mutado

def mejores(hijos,longitud, individuos):
    pos = 0
    mejor = hijos[0][longitud]
    i=1
    #se revisa el ayor numero de reinas listas
    while (i>individuos):
        if hijos[i][longitud]<mejor:
            pos = i
            mejor = hijos[i][longitud]
        i+=1
    return pos

def imprimeTablero(inidivudoaAimprimir,longitud):
    cuadros = longitud+2
    media = 50
    venta = cuadros*media
    pygame.init()
    ventana = pygame.display.set_mode((venta,venta))
    mensaje = "Problema N reinas"
    pygame.display.set_caption(mensaje)
    BLANCO = (255,255,255)
    NEGRO = (0,0,0)
    REINA = (204, 170,238)
    FONDO = (11,41,116)
    solucion = inidivudoaAimprimir
    while True:
        ventana.fill(FONDO)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                juego_terminado = True
                sys.exit()
        numero=1
        for i in range(longitud):
            reina = solucion[i]
            for j in range (longitud):
                x = (i*media) + media
                y = (j*media) + media
                if reina == j:
                    pygame.draw.rect(ventana,REINA,[x,y,media,media])
                elif (numero%2==0):
                    pygame.draw.rect(ventana,NEGRO,[x,y,media,media])
                else:
                    pygame.draw.rect(ventana,BLANCO,[x,y,media,media])
                numero+=1
            if (longitud%2==0):
                numero+=1
        pygame.display.update()

def main ():
    reinasListas = 0
    seis = 0
    siete = 0
    PC = 0.7  # % cruza
    PM = 1 - PC # % mutacion
    generacionActual = []
    v_aux = []
    hijos = []
    v_mejores = []
    mejoresPorGeneracion = []
    generacion = 0
    flag = True
    longitud = int(tamtk.get())
    lim_inf = 0
    lim_sup = longitud-1
    base = 10
    individuos = int(individuostk.get())

    #primera generacion
    generacionActual = generaIndividuos(lim_inf, lim_sup, individuos,longitud) #Generamos la primera generacion de individuos enteros entre 0 y tam de tablero-1
    v_aux = posicionesBuenas(generacionActual, individuos, longitud) #Es funcion fitness revisa que las reinas no esten en las mismas filas
    individuosMutan = math.ceil(individuos*PM) #individuos que mutaran
    for i in range (individuos):
        generacionActual[i].append(v_aux[i])  #por individuo agregamos las reinas que estan posicionadas adecuadamente
    ############################################################################################
    while (flag):
        hijos = seleccionPorRuleta(generacionActual, longitud, individuos) #el nombre lo dice
        for i in range(individuos):
            generacionActual[i][longitud+2] = round(generacionActual[i][longitud+2],3) # [L+2] es la probabilidad acumulada y se redondea a 3 decimales 
        cruza2puntos(hijos,longitud, individuos)#el nombre lo dice
        v_aux.clear() 
        #mutacionEstandar(hijos, longitud, individuosMutan)#el nombre lo dice
        mutacionIntercambio(hijos, longitud, individuosMutan)
        #v_aux.clear()
        v_aux = posicionesBuenas(hijos, individuos, longitud) #ahora llamamos a la funcion "fitness" pero con los hijos
        for i in range (individuos):
            hijos[i].append(v_aux[i])  #por individuo agregamos las reinas que estan posicionadas adecuadamente
        #seleccion jerarquica
        #se agregan a los mejores hijos o padres que formaran la nueva generacion
        mejoresPorGeneracion.clear()
        for i in range (individuos):
            if (generacionActual[i][longitud]>=hijos[i][longitud]):
                mejoresPorGeneracion.append(generacionActual[i][0:longitud+1]) 
            else:
                mejoresPorGeneracion.append(hijos[i][0:longitud+1])
    
        pos = mejores(mejoresPorGeneracion,longitud, individuos)#devuelve la posicion del mejor individuo por generacion
        v_mejores.append(mejoresPorGeneracion[pos]) #agregamos el mejor individuo de cada generacion
        reinasListas = mejoresPorGeneracion[pos][longitud] #obtenemos el numero de reinas que estan posicionadas de forma correcta de acuerdo al mejor individuo
        #generacionActual.clear()
        #copiamos a los mejores de esta nueva generacion a la siguiente generacion
        for l in range (individuos):
            generacionActual[l]=mejoresPorGeneracion[l].copy()
        hijos.clear()
        #condiciones para parar el programa
        if reinasListas == (longitud-1) or reinasListas == longitud: #solo parará cuando haya (N-1) reinas listas y que haya intentado alcanzar el maximo 5 veces
            flag = False
        if generacion == 2000: #si no encuentra una solucion el programa muere, por eso se decidio terminarlo en 2k mostrando al mejor hasta el momento
            messagebox.showerror(message="Se llego a 2000 generaciones y no convergio :c", title="Informe de resultados")
            pos = mejores(v_mejores,longitud, individuos)
            break
        generacion+=1
        
    mensaje =  "El programa finalizo con: " + str(reinasListas) + " Reinas listas colocadas en el tablero \n Se requirieron de: " + str(generacion)+" generaciones para finalizar el programa"
    #aviso de que el programa termino con K reinas en N generaciones
    messagebox.showinfo(message=mensaje, title="Informe de resultados")
    inidivudoaAimprimir = v_mejores[generacion-1][0:longitud].copy() #individuo que se mostrara en el tablero
    imprimeTablero(inidivudoaAimprimir,longitud)#la funcion lo dice se hizo uso de pygame 


#ventana
root = tkinter.Tk()
root.geometry('750x350')
root.title("Practica 3. Problema de las 8 reinas")
color = "#0B2974"
textcol = "white"
root.configure(bg=color)
tamtk=IntVar()
individuostk = IntVar()

Label(root,text='Instituto Politecnico Nacional',bg=color,fg=textcol).place(x=210,y=30)
Label(root, text="Escuela Superior de Computo",bg=color,fg=textcol).place(x=210,y=60)
Label(root, text="Asignatura: Algoritmos Geneticos",bg=color,fg=textcol).place(x=210,y=90)
Label(root, text="Profesora: Cruz Meza Maria Elena",bg=color,fg=textcol).place(x=210,y=120)

Label(text='Seleccione el tam del tablero: ',bg=color,fg=textcol).place(x=220,y=170)
Entry(root,textvariable=tamtk).place(x=380,y=170)

Label(text='No. de individuos',bg=color,fg=textcol).place(x=220,y=210)
Entry(root,textvariable=individuostk).place(x=320,y=210)

Button(root,text='Comenzar', command= lambda: main()).pack(side=BOTTOM)

root.mainloop()

