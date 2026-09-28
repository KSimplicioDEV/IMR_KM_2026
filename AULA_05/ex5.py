# Exercício 5: Máquina de Estados Finitos do Robô Autônomo
import math
from ex3 import controle_reativo
from ex4 import calcular_orientacao_alvo


def maquina_de_estados(x, y, theta, x_alvo, y_alvo, dist_frente, dist_esq, dist_dir):
    # Calcule a distancia ate o alvo: sqrt((x_alvo - x)^2 + (y_alvo - y)^2)
    dist_alvo = math.sqrt((x_alvo - x) ** 2 + (y_alvo - y) ** 2)

    # Determine as transições de estado entre 'IR_PARA_ALVO', 'DESVIAR_OBSTACULO' e 'OBJETIVO_ALCANÇADO'
    if dist_alvo < 0.2:
        estado_atual = 'OBJETIVO_ALCANÇADO'
        v_cmd = 0.0
        omega_cmd = 0.0

    elif dist_frente < 0.5:
        estado_atual = 'DESVIAR_OBSTACULO'
        distancias = {'frente': dist_frente, 'esquerda': dist_esq, 'direita': dist_dir}
        v_cmd, omega_cmd = controle_reativo(distancias)

    else:
        estado_atual = 'IR_PARA_ALVO'
        v_cmd = 0.5
        omega_cmd = calcular_orientacao_alvo(x, y, theta, x_alvo, y_alvo)

    return estado_atual, v_cmd, omega_cmd


if __name__ == "__main__":
    print(maquina_de_estados(0, 0, 0, 5, 5, 3.0, 2.0, 2.0))
    print(maquina_de_estados(0, 0, 0, 5, 5, 0.3, 2.0, 1.0))
    print(maquina_de_estados(4.9, 4.9, 0, 5, 5, 3.0, 2.0, 2.0))