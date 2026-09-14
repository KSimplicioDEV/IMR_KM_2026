import math
import pygame

LARGURA, ALTURA = 1000, 620

Y_PAREDE_SUP = 200
Y_PAREDE_INF = 420
ESPESSURA = 8

KP_PADRAO = 0.01
V_LINEAR = 40.0
ALCANCE = 400.0
PASSO_RAY = 1.0

BRANCO = (248, 248, 248)
PRETO = (25, 25, 25)
CINZA = (110, 110, 110)
AZUL = (40, 90, 200)
VERMELHO = (205, 60, 60)
VERDE = (25, 145, 85)

PAREDES = [
    pygame.Rect(0, Y_PAREDE_SUP - ESPESSURA, LARGURA, ESPESSURA),
    pygame.Rect(0, Y_PAREDE_INF, LARGURA, ESPESSURA),
]
CENTRO_Y = (Y_PAREDE_SUP + Y_PAREDE_INF) / 2.0


def raycast(x, y, ang):
    d = 0.0
    while d < ALCANCE:
        px = x + math.cos(ang) * d
        py = y + math.sin(ang) * d
        if py < 0 or py > ALTURA:
            return d
        for p in PAREDES:
            if p.collidepoint(px, py):
                return d
        d += PASSO_RAY
    return ALCANCE


def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Lab 5 - Centralizacao em corredor (controle P)")
    fonte = pygame.font.SysFont("consolas", 17)
    fonte_tit = pygame.font.SysFont("consolas", 20, bold=True)
    relogio = pygame.time.Clock()

    def reiniciar():

        return 60.0, Y_PAREDE_SUP + 45.0, math.radians(-12.0)

    x, y, th = reiniciar()
    kp = KP_PADRAO
    controle_ligado = True
    rastro = []
    historico_erro = []
    rodando = True

    while rodando:
        dt = relogio.tick(60) / 1000.0

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                rodando = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    rodando = False
                elif ev.key == pygame.K_r:
                    x, y, th = reiniciar()
                    rastro.clear()
                    historico_erro.clear()
                elif ev.key == pygame.K_SPACE:
                    controle_ligado = not controle_ligado
                elif ev.key == pygame.K_UP:
                    kp += 0.002
                elif ev.key == pygame.K_DOWN:
                    kp = max(0.0, kp - 0.002)

        d_esq = raycast(x, y, th - math.pi / 2)
        d_dir = raycast(x, y, th + math.pi / 2)

        erro = d_esq - d_dir
        omega = kp * erro if controle_ligado else 0.0
        v = V_LINEAR

        x += v * math.cos(th) * dt
        y += v * math.sin(th) * dt
        th += omega * dt

        if x > LARGURA:               
            x, y, th = reiniciar()
            rastro.clear()
            historico_erro.clear()

        rastro.append((int(x), int(y)))
        historico_erro.append(erro)
        if len(historico_erro) > 700:
            historico_erro.pop(0)

        tela.fill(BRANCO)
        for p in PAREDES:
            pygame.draw.rect(tela, CINZA, p)
        pygame.draw.line(tela, (200, 220, 200), (0, CENTRO_Y), (LARGURA, CENTRO_Y), 1)

        if len(rastro) > 1:
            pygame.draw.lines(tela, VERMELHO, False, rastro, 2)

        for ang, d, cor in ((th - math.pi / 2, d_esq, VERDE),
                            (th + math.pi / 2, d_dir, AZUL)):
            fim = (x + math.cos(ang) * d, y + math.sin(ang) * d)
            pygame.draw.line(tela, cor, (x, y), fim, 2)

        pygame.draw.circle(tela, AZUL, (int(x), int(y)), 11)
        pygame.draw.line(tela, PRETO, (x, y),
                         (x + 24 * math.cos(th), y + 24 * math.sin(th)), 3)

        base_y = ALTURA - 70
        pygame.draw.line(tela, (180, 180, 180), (20, base_y), (LARGURA - 20, base_y), 1)
        for i, e in enumerate(historico_erro):
            px = 20 + i
            py = base_y - max(-55, min(55, e * 0.45))
            pygame.draw.circle(tela, VERDE, (int(px), int(py)), 1)

        estado = "LIGADO" if controle_ligado else "DESLIGADO"
        tela.blit(fonte_tit.render(f"CONTROLE P: {estado}", True, PRETO), (15, 12))
        linhas = [
            f"d_esq = {d_esq:6.1f} px      d_dir = {d_dir:6.1f} px",
            f"erro e = d_esq - d_dir = {erro:7.2f} px",
            f"Kp = {kp:.4f}   ->   omega = Kp*e = {omega:7.4f} rad/s",
            f"v = {v:.1f} px/s (constante)",
            "",
            "R = reiniciar desalinhado   ESPACO = liga/desliga controle",
            "setas cima/baixo = ajusta Kp   ESC = sair",
            "(curva verde embaixo = erro ao longo do tempo)",
        ]
        for i, t in enumerate(linhas):
            tela.blit(fonte.render(t, True, PRETO), (15, 44 + i * 21))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
