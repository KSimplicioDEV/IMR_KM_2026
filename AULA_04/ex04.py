import math
import pygame

LARGURA, ALTURA = 1000, 640

V0 = 30.0          
ALPHA = 90.0         
D_MAX = 220.0        
EIXO = 26.0          
ANG_SENSOR = math.radians(35)   
PASSO_RAY = 2.0

BRANCO = (248, 248, 248)
PRETO = (25, 25, 25)
AZUL = (40, 90, 200)
VERMELHO = (205, 60, 60)
VERDE = (25, 145, 85)
CINZA = (130, 130, 130)


class Obstaculo:
    def __init__(self, x, y, r=45):
        self.x, self.y, self.r = x, y, r

    def contem(self, px, py):
        return (px - self.x) ** 2 + (py - self.y) ** 2 <= self.r ** 2


def raycast(x, y, ang, obst):
    d = 0.0
    while d < D_MAX:
        px = x + math.cos(ang) * d
        py = y + math.sin(ang) * d
        if px < 0 or px > LARGURA or py < 0 or py > ALTURA:
            return d
        if obst.contem(px, py):
            return d
        d += PASSO_RAY
    return D_MAX


def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Lab 4 - Braitenberg (conexoes diretas)")
    fonte = pygame.font.SysFont("consolas", 17)
    fonte_tit = pygame.font.SysFont("consolas", 20, bold=True)
    relogio = pygame.time.Clock()

    x, y, th = 120.0, 320.0, 0.0
    obst = Obstaculo(680, 300)
    cruzado = False         
    rastro = []
    rodando = True

    while rodando:
        dt = relogio.tick(60) / 1000.0

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                rodando = False
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                obst.x, obst.y = ev.pos
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    rodando = False
                elif ev.key == pygame.K_r:
                    x, y, th = 120.0, 320.0, 0.0
                    rastro.clear()
                elif ev.key == pygame.K_c:
                    cruzado = not cruzado
                    rastro.clear()

        ang_esq = th - ANG_SENSOR
        ang_dir = th + ANG_SENSOR
        d_esq = raycast(x, y, ang_esq, obst)
        d_dir = raycast(x, y, ang_dir, obst)

        e_esq = 1.0 - d_esq / D_MAX
        e_dir = 1.0 - d_dir / D_MAX

        if cruzado:

            vL = V0 + ALPHA * e_dir
            vR = V0 + ALPHA * e_esq
        else:

            vL = V0 + ALPHA * e_esq
            vR = V0 + ALPHA * e_dir

        v = (vR + vL) / 2.0
        omega = (vR - vL) / EIXO

        x += v * math.cos(th) * dt
        y += v * math.sin(th) * dt
        th += omega * dt


        if obst.contem(x, y):
            v = omega = 0.0

        if x < 0: x = LARGURA
        if x > LARGURA: x = 0
        if y < 0: y = ALTURA
        if y > ALTURA: y = 0

        rastro.append((int(x), int(y)))
        if len(rastro) > 3000:
            rastro.pop(0)

        tela.fill(BRANCO)
        if len(rastro) > 1:
            pygame.draw.lines(tela, (230, 190, 190), False, rastro, 2)

        pygame.draw.circle(tela, CINZA, (int(obst.x), int(obst.y)), obst.r)

        for ang, d, cor in ((ang_esq, d_esq, VERDE), (ang_dir, d_dir, VERMELHO)):
            fim = (x + math.cos(ang) * d, y + math.sin(ang) * d)
            pygame.draw.line(tela, cor, (x, y), fim, 2)

        pygame.draw.circle(tela, AZUL, (int(x), int(y)), 13)
        pygame.draw.line(tela, PRETO, (x, y),
                         (x + 26 * math.cos(th), y + 26 * math.sin(th)), 3)
        for sinal, vel, cor in ((-1, vL, VERDE), (1, vR, VERMELHO)):
            rx = x + sinal * (EIXO / 2) * math.cos(th + math.pi / 2)
            ry = y + sinal * (EIXO / 2) * math.sin(th + math.pi / 2)
            pygame.draw.circle(tela, cor, (int(rx), int(ry)), max(3, int(vel / 25)))

        modo = "CRUZADA (aversao - aula 03)" if cruzado else "DIRETA (agressao - aula 04)"
        tela.blit(fonte_tit.render(f"CONEXAO {modo}", True, PRETO), (15, 12))
        linhas = [
            f"d_esq = {d_esq:6.1f} px   ->  vL = {vL:6.2f} px/s",
            f"d_dir = {d_dir:6.1f} px   ->  vR = {vR:6.2f} px/s",
            f"v = {v:6.2f} px/s     omega = {omega:6.3f} rad/s",
            "",
            "obstaculo mais perto de um lado -> aquela roda ACELERA",
            "-> o robo curva PARA o obstaculo (atracao/agressao)",
            "",
            "clique = mover obstaculo   R = reiniciar   C = alternar conexao   ESC = sair",
        ]
        for i, t in enumerate(linhas):
            tela.blit(fonte.render(t, True, PRETO), (15, 44 + i * 22))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
