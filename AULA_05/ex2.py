import numpy as np


def menor_valida(valores):
    validas = [d for d in valores if 0.1 <= d <= 5.0]
    if len(validas) == 0:
        return 5.0
    return float(min(validas))


def processar_scan(leituras_lidar):
    # leituras_lidar é uma lista/array com 360 floats
    leituras = np.array(leituras_lidar, dtype=float)

    setor_frente = list(leituras[345:360]) + list(leituras[0:16])
    setor_esq = list(leituras[45:136])
    setor_dir = list(leituras[225:316])

    min_frente = menor_valida(setor_frente)
    min_esq = menor_valida(setor_esq)
    min_dir = menor_valida(setor_dir)

    # Retorne dict com: {'frente': min_frente, 'esquerda': min_esq, 'direita': min_dir}
    return {'frente': min_frente, 'esquerda': min_esq, 'direita': min_dir}


if __name__ == "__main__":
    scan = np.full(360, 3.0)
    scan[0] = 0.0
    scan[5] = 0.8
    scan[10] = np.inf
    scan[90] = 1.2
    scan[270] = 0.05
    print(processar_scan(scan))