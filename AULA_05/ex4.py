import math


def calcular_orientacao_alvo(x, y, theta, x_alvo, y_alvo, Kp=1.5):
    # 1. Calcule o angulo desejado usando math.atan2
    theta_alvo = math.atan2(y_alvo - y, x_alvo - x)

    # 2. Calcule o erro e_theta e normalize no intervalo [-pi, pi]
    e_theta = theta_alvo - theta
    e_theta = math.atan2(math.sin(e_theta), math.cos(e_theta))

    # 3. Calcule omega = Kp * e_theta
    omega = Kp * e_theta
    return omega


if __name__ == "__main__":
    print(calcular_orientacao_alvo(0, 0, 0, 1, 1))
    print(calcular_orientacao_alvo(0, 0, math.pi, 1, -0.1))