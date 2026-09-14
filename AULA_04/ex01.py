import math
import pygame

POSE_INICIAL = (0.0, 0.0, 0.0)         

# (duracao_s, v_m_s, omega_rad_s)
TRECHOS = [
    (4.0, 0.5, 0.0),
    (2.0, 0.0, 0.7854),                 
    (3.0, 0.4, 0.0),
]

DT = 0.01                              
ESCALA = 120                            
LARGURA, ALTURA = 900, 600
ORIGEM = (150, 450)                     

BRANCO = (245, 245, 245)
PRETO = (20, 20, 20)
CINZA = (190, 190, 190)
AZUL = (40, 90, 200)
VERMELHO = (200, 50, 50)
VERDE = (30, 150, 90)

def pose_teorica(pose, trechos):
    """Resolve cada trecho em forma fechada.

    Se omega == 0 -> movimento retilineo:  x += v*t*cos(theta)
    Se omega != 0 -> arco de circunferencia de raio R = v/omega.
    """
    x, y, th = pose
    for t, v, w in trechos:
        if abs(w) < 1e-9:
            x += v * t * math.cos(th)
            y += v * t * math.sin(th)
        else:
            th_novo = th + w * t
            R = v / w
            x += R * (math.sin(th_novo) - math.sin(th))
            y += -R * (math.cos(th_novo) - math.cos(th))
            th = th_novo
    return x, y, th

def gerar_trajetoria(pose, trechos, dt=DT):
    """Devolve a lista de poses passo a passo (usada para desenhar)."""
    x, y, th = pose
    caminho = [(x, y, th)]
    for t, v, w in trechos:
        passos = int(round(t / dt))
        for _ in range(passos):
            x += v * math.cos(th) * dt
            y += v * math.sin(th) * dt
            th += w * dt
            caminho.append((x, y, th))
    return caminho


def normalizar(ang):
    """Deixa o angulo entre -pi e +pi, so pra impressao ficar legivel."""
    return (ang + math.pi) % (2 * math.pi) - math.pi


def para_tela(x, y):
    """Converte metros (y para cima) em pixels (y para baixo)."""
    return int(ORIGEM[0] + x * ESCALA), int(ORIGEM[1] - y * ESCALA)


def desenhar_robo(tela, x, y, th):
    px, py = para_tela(x, y)
    pygame.draw.circle(tela, AZUL, (px, py), 12)
    fx = px + int(22 * math.cos(th))
    fy = py - int(22 * math.sin(th))
    pygame.draw.line(tela, PRETO, (px, py), (fx, fy), 3)


def desenhar_grade(tela, fonte):
    for i in range(-1, 6):
        px, _ = para_tela(i, 0)
        pygame.draw.line(tela, CINZA, (px, 0), (px, ALTURA), 1)
    for j in range(-1, 4):
        _, py = para_tela(0, j)
        pygame.draw.line(tela, CINZA, (0, py), (LARGURA, py), 1)
    # eixos
    ox, oy = ORIGEM
    pygame.draw.line(tela, PRETO, (0, oy), (LARGURA, oy), 2)
    pygame.draw.line(tela, PRETO, (ox, 0), (ox, ALTURA), 2)
    tela.blit(fonte.render("1 quadrado = 1 m", True, PRETO), (LARGURA - 190, ALTURA - 28))


def main():
    caminho = gerar_trajetoria(POSE_INICIAL, TRECHOS)
    xt, yt, tht = pose_teorica(POSE_INICIAL, TRECHOS)
    xs, ys, ths = caminho[-1]

    # --- saida no terminal -------------------------------------------
    print("=" * 62)
    print("EXERCICIO 1 - POSE EM MALHA ABERTA")
    print("=" * 62)
    print(f"Pose inicial : x={POSE_INICIAL[0]:.4f} m  y={POSE_INICIAL[1]:.4f} m  "
          f"theta={POSE_INICIAL[2]:.4f} rad")
    for i, (t, v, w) in enumerate(TRECHOS, start=1):
        print(f"  Trecho {i}: t={t:.1f}s  v={v:.2f} m/s  omega={w:.4f} rad/s "
              f"(giro de {math.degrees(w * t):.1f} graus)")
    print("-" * 62)
    print(f"Pose final TEORICA : x={xt:.4f} m  y={yt:.4f} m  "
          f"theta={normalizar(tht):.4f} rad ({math.degrees(normalizar(tht)):.2f} graus)")
    print(f"Pose final SIMULADA: x={xs:.4f} m  y={ys:.4f} m  "
          f"theta={normalizar(ths):.4f} rad ({math.degrees(normalizar(ths)):.2f} graus)")
    print(f"Erro absoluto      : dx={abs(xt - xs):.6f}  dy={abs(yt - ys):.6f}  "
          f"dtheta={abs(normalizar(tht - ths)):.6f}")
    print("=" * 62)

    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Lab 1 - Pose em malha aberta")
    fonte = pygame.font.SysFont("consolas", 18)
    relogio = pygame.time.Clock()

    idx = 0
    passos_por_frame = max(1, int((1 / 60) / DT))   # anima em tempo real (~60 fps)
    rodando = True

    while rodando:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                rodando = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    rodando = False
                elif ev.key == pygame.K_SPACE:
                    idx = 0

        if idx < len(caminho) - 1:
            idx = min(idx + passos_por_frame, len(caminho) - 1)

        tela.fill(BRANCO)
        desenhar_grade(tela, fonte)

        # rastro ja percorrido
        if idx > 1:
            pontos = [para_tela(p[0], p[1]) for p in caminho[:idx + 1]]
            pygame.draw.lines(tela, VERMELHO, False, pontos, 3)

        x, y, th = caminho[idx]
        desenhar_robo(tela, x, y, th)

        # marcador da pose final teorica
        pygame.draw.circle(tela, VERDE, para_tela(xt, yt), 6, 2)

        linhas = [
            f"t = {idx * DT:5.2f} s de {sum(t for t, _, _ in TRECHOS):.1f} s",
            f"pose atual   : ({x:6.3f}, {y:6.3f}) m  theta={math.degrees(normalizar(th)):7.2f} deg",
            f"pose teorica : ({xt:6.3f}, {yt:6.3f}) m  theta={math.degrees(normalizar(tht)):7.2f} deg",
            "ESPACO = reiniciar   ESC = sair",
        ]
        for i, txt in enumerate(linhas):
            tela.blit(fonte.render(txt, True, PRETO), (15, 15 + i * 22))

        pygame.display.flip()
        relogio.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
