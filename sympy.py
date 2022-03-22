import simpy 
import random
#Definicion de variables iniciales y variables que se miden
despachadores = 3
cajero = 2
empleados = despachadores + cajero
tiempo = 60
colaPago = 0
colaPreparacion = 0
tiempoTotal = 0
clienteDesServicio = 0
sumTiempo = 0
tiempoMax = 0
tiempodespachadoresocu = 0
tiempoCajeroOcu = 0
tiempoEmpleadosOcu = 0


#Metodo que genera el tiempo en el que se demora un cliente en pagar
def pagoCliente(env, client):
  time=random.normalvariate(3/4,1/6)
  yield env.timeout(time)
  print(client + ' pago en  %.3f minutos' %(time))


#Metodo que genera el tiempo que se demora la preparacion de la comida
def prepComida(env, client):
  time=random.uniform(3,5)
  yield env.timeout(time)
  print('La comida para el ' + client + ' fue preparada en  %.3f minutos.' %(time))

#Metodo del proceso de compra de un cliente, primero utiliza un empleado y se demora un tiempo
#para pagar, luego tambien utiliza un empleado y se demora un tiempo en preparar la comida.
#Se toman los tiempos necesarios para calcular promedios y maximos
def clientes(env, client, empleado):
    global tiempo, colaPago, colaPreparacion, tiempoTotal, clienteDesServicio, sumTiempo, tiempoMax
    global tiempoEmpleadosOcu
    tiempoLlegada = env.now
    print(client + ' llego a las %.1f ' %(tiempoLlegada))

    with empleado.request() as usoEmpleado:
      yield usoEmpleado
      tiempoComienzo = env.now
      colaPagoTiempo = env.now - tiempoLlegada
      colaPago += colaPagoTiempo
      if colaPagoTiempo == 0:
        print(client+ ' no espero en fila para pagar')
      else:
        print(client + ' espero en fila por %.3f para el pago' %(colaPagoTiempo))
      yield env.process(pagoCliente(env, client))
      empleado.release(usoEmpleado)
      tiempofinal = env.now
      tiempoEmpleadosOcu += (tiempofinal - tiempoComienzo)
    
    finalTiempoPago = env.now
    
    with empleado.request() as usoEmpleado:
      yield usoEmpleado

      tiempoComienzo = env.now
      colaPrepaComida = env.now - finalTiempoPago
      colaPreparacion += colaPrepaComida

      if colaPrepaComida == 0:
        print(client+ ' no espero para la preparacion')
      else:
        print(client + ' espero en fila por %.3f para la preparacion' %(colaPrepaComida))

      yield env.process(prepComida(env, client))
      empleado.release(usoEmpleado)
      tiempofinal = env.now
      tiempoEmpleadosOcu += (tiempofinal - tiempoComienzo)

    clienteDesServicio += 1
    tiempoSalida = env.now
    tiempoTotal = tiempoSalida - tiempoLlegada
    print(client + ' estuvo en el sistema por %.2f minutos' %(tiempoTotal))

    sumTiempo += tiempoTotal
    if tiempoTotal > tiempoMax:
      tiempoMax = tiempoTotal


def genDeClientes (env, empleado):
  cont = 0
  tiempoLlegada = 0

  while True:
    tiempoLlegada = random.expovariate(1)
    yield env.timeout(tiempoLlegada)
    cont+=1
    client= 'Cliente ' +str(cont)
    env.process(clientes(env, client, empleado))

    
def resumen():
  print('Resumen')

  pagoPromedio = colaPago / clienteDesServicio
  print('Tiempo promedio de pago %.3f' %(pagoPromedio))

  prepaPromedio = colaPreparacion / clienteDesServicio
  print('Tiempo promedio de preparacion comida %.3f'  %(prepaPromedio))

  promTiempotot = sumTiempo / clienteDesServicio
  print('Tiempo promedio en el sistema %.3f' %(promTiempotot))

  print('Tiempo maximo en el sistema %.3f' %(tiempoMax))

  ocupacionEmpl = ((tiempoEmpleadosOcu/empleados)/ (tiempo))
  print('Ocupacion de empleados %.2f en porciento' %(ocupacionEmpl))

def modelo():
  env = simpy.Environment()
  a = 0.8
  random.seed(a)
  empleado = simpy.Resource(env, empleados)
  env.process(genDeClientes(env, empleado))
  env.run(until = tiempo)

modelo()
resumen()