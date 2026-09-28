def controle_reativo(distancias):
    # distancias = {'frente': float, 'esquerda': float, 'direita': float}
    dist_critica = 0.4
    v_livre = 0.5
    ganho = 0.5

    frente = distancias['frente']
    esq = distancias['esquerda']
    dir = distancias['direita']

    if frente < dist_critica:
        v = 0.0
        if esq > dir:
            omega = 1.0
        else:
            omega = -1.0
    else:
        v = v_livre
        omega = ganho * (esq - dir)

    # Retorne v (linear) e omega (angular)
    return v, omega


if __name__ == "__main__":
    print(controle_reativo({'frente': 0.3, 'esquerda': 2.0, 'direita': 1.0}))
    print(controle_reativo({'frente': 0.3, 'esquerda': 1.0, 'direita': 2.0}))
    print(controle_reativo({'frente': 3.0, 'esquerda': 2.0, 'direita': 1.0}))