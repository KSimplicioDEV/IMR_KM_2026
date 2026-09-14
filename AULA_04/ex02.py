import math
import pygame

LARGURA, ALTURA = 1000, 680
ESCALA = 45.0            
L = 2.0                  
PHI_MAX = math.radians(30.0)
DPHI = math.radians(1.0)
DV = 0.2

BRANCO = (248, 248, 248)
PRETO = (25, 25, 25)
CINZA = (205, 205, 205)
AZUL = (40, 90, 200)
VERMELHO = (200, 60, 60)
VERDE = (30, 150, 90)
LARANJA = (220, 130, 30)


def metros_para_tela(x, y):
    return int(LARGURA / 2 + x * ESCALA), int(ALTURA / 2 - y * ESCALA)


def desenhar_veiculo(tela, x, y, th, phi, modo):
    """Desenha um retangulo com as duas rodas dianteiras esterçadas."""
    meia_larg, meio_comp = 0.45, L / 2
    cantos = [(-meio_comp, -meia_larg), (meio_comp, -meia_larg),
              (meio_comp, meia_larg), (-meio_comp, meia_larg)]
    pts = []
    for cx, cy in cantos:
        gx = x + cx * math.cos(th) - cy * math.sin(th)
        gy = y + cx * math.sin(th) + cy * math.cos(th)
        pts.append(metros_para_tela(gx, gy))
    pygame.draw.polygon(tela, AZUL, pts)

    # rodas dianteiras (esterçadas so no modo Ackermann)
    ang_roda = th + (phi if modo == "ackermann" else 0.0)
    for lado in (-meia_larg, meia_larg):
        cx, cy = meio_comp, lado
        gx = x + cx * math.cos(th) - cy * math.sin(th)
        gy = y + cx * math.sin(th) + cy * math.cos(th)
        p0 = metros_para_tela(gx - 0.3 * math.cos(ang_roda), gy - 0.3 * math.sin(ang_roda))
        p1 = metros_para_tela(gx + 0.3 * math.cos(ang_roda), gy + 0.3 * math.sin(ang_roda))
        pygame.draw.line(tela, PRETO, p0, p1, 5)


def desenhar_grade(tela):
    passo = int(ESCALA)
    for px in range(0, LARGURA, passo):
        pygame.draw.line(tela, CINZA, (px, 0), (px, ALTURA), 1)
    for py in range(0, ALTURA, passo):
        pygame.draw.line(tela, CINZA, (0, py), (LARGURA, py), 1)


def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Lab 2 - Ackermann x Diferencial")
    fonte = pygame.font.SysFont("consolas", 18)
    fonte_tit = pygame.font.SysFont("consolas", 22, bold=True)
    relogio = pygame.time.Clock()

    x, y, th = 0.0, 0.0, 0.0
    v = 1.0
    phi = math.radians(15.0)
    omega_dif = 0.5           # entrada direta quando o modo é diferencial
    modo = "ackermann"
    rastro = []
    rodando = True

    while rodando:
        dt = relogio.tick(60) / 1000.0

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                rodando = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    rodando = False
                elif ev.key == pygame.K_TAB:
                    modo = "diferencial" if modo == "ackermann" else "ackermann"
                    rastro.clear()
                elif ev.key == pygame.K_r:
                    x, y, th = 0.0, 0.0, 0.0
                    rastro.clear()

        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_UP]:
            v += DV * dt * 10
        if teclas[pygame.K_DOWN]:
            v -= DV * dt * 10
        v = max(-3.0, min(3.0, v))

        if modo == "ackermann":
            if teclas[pygame.K_LEFT]:
                phi += DPHI * dt * 30
            if teclas[pygame.K_RIGHT]:
                phi -= DPHI * dt * 30
            phi = max(-PHI_MAX, min(PHI_MAX, phi))
            omega = (v / L) * math.tan(phi)
        else:
            if teclas[pygame.K_LEFT]:
                omega_dif += 1.0 * dt
            if teclas[pygame.K_RIGHT]:
                omega_dif -= 1.0 * dt
            omega_dif = max(-2.0, min(2.0, omega_dif))
            omega = omega_dif

        # integra a pose
        x += v * math.cos(th) * dt
        y += v * math.sin(th) * dt
        th += omega * dt

        # mantem o veiculo dentro da arena (wrap simples)
        lim_x = (LARGURA / 2) / ESCALA
        lim_y = (ALTURA / 2) / ESCALA
        if abs(x) > lim_x or abs(y) > lim_y:
            x, y = 0.0, 0.0
            rastro.clear()

        rastro.append(metros_para_tela(x, y))
        if len(rastro) > 4000:
            rastro.pop(0)

        # raio de curvatura
        if modo == "ackermann":
            raio = float("inf") if abs(math.tan(phi)) < 1e-6 else L / math.tan(phi)
        else:
            raio = float("inf") if abs(omega) < 1e-6 else v / omega

        tela.fill(BRANCO)
        desenhar_grade(tela)
        if len(rastro) > 1:
            pygame.draw.lines(tela, VERMELHO, False, rastro, 2)

        # centro instantaneo de curvatura (ICC)
        if math.isfinite(raio) and abs(raio) < 40:
            icc = metros_para_tela(x - raio * math.sin(th), y + raio * math.cos(th))
            pygame.draw.circle(tela, VERDE, icc, 6)
            pygame.draw.line(tela, VERDE, metros_para_tela(x, y), icc, 1)

        desenhar_veiculo(tela, x, y, th, phi, modo)

        cor_modo = LARANJA if modo == "ackermann" else VERDE
        tela.blit(fonte_tit.render(f"MODELO: {modo.upper()}  (TAB alterna)", True, cor_modo), (15, 12))

        raio_txt = "infinito (reta)" if not math.isfinite(raio) else f"{raio:7.3f} m"
        linhas = [
            f"v     = {v:6.2f} m/s        (setas cima/baixo)",
            f"phi   = {math.degrees(phi):6.2f} deg  (limite +-30, setas esq/dir)"
            if modo == "ackermann" else
            f"omega = {omega:6.2f} rad/s   (entrada direta, setas esq/dir)",
            f"omega = {omega:6.3f} rad/s",
            f"R     = {raio_txt}",
            "",
            f"R minimo Ackermann (phi=30 deg): {L / math.tan(PHI_MAX):.3f} m",
            "Diferencial: com v=0 e omega!=0 -> R=0 (gira no proprio eixo)",
            "Ackermann  : tan(phi) saturado -> R nunca chega a zero",
            "",
            "R = reposiciona   ESC = sair",
        ]
        for i, txt in enumerate(linhas):
            tela.blit(fonte.render(txt, True, PRETO), (15, 46 + i * 22))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    # tabela de apoio impressa no terminal (entra no relatorio)
    print("phi (deg) |   tan(phi) |    R = L/tan(phi) [m] | omega p/ v=1 m/s")
    print("-" * 66)
    for g in (0, 5, 10, 15, 20, 25, 30):
        t = math.tan(math.radians(g))
        r = float("inf") if t == 0 else L / t
        w = (1.0 / L) * t
        r_txt = "       infinito" if math.isinf(r) else f"{r:15.3f}"
        print(f"{g:9d} | {t:10.4f} | {r_txt}       | {w:8.4f}")
    print()
    main()
