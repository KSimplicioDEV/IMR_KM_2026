def converter_cmd_vel(v, omega, L=0.3, max_wheel_speed=1.5):
    # 1. Calcule v_e e v_d brutas
    v_e = v - (omega * L / 2)
    v_d = v + (omega * L / 2)

    # 2. Verifique se v_e ou v_d ultrapassam max_wheel_speed (positivo ou negativo)
    maior = max(abs(v_e), abs(v_d))

    # 3. Aplique a saturação/limitação necessária
    if maior > max_wheel_speed:
        fator = max_wheel_speed / maior
        v_e = v_e * fator
        v_d = v_d * fator

    return v_e, v_d


# Teste seu código:
if __name__ == "__main__":
    print(converter_cmd_vel(1.2, 3.0))  #Deve limitar sem travar o motor
    print(converter_cmd_vel(0.5, 0.0))
    print(converter_cmd_vel(-1.2, -3.0))