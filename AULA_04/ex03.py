import math
import numpy as np
import pygame

LARGURA, ALTURA = 1000, 640
N_FEIXES = 7
FOV = math.pi                
ALCANCE_MAX = 200.0
LIMIAR_MIN = 10.0
SIGMA_RUIDO = 5.0
PASSO_RAY = 2.0

BRANCO = (248, 248, 248)
PRETO = (25, 25, 25)
CINZA = (120, 120, 120)
AZUL = (40, 90, 200)
VERMELHO = (205, 60, 60)
VERDE = (25, 145, 85)
LARANJA = (225, 140, 20)

OBSTACULOS = [
    pygame.Rect(520, 120, 60, 200),
    pygame.Rect(430, 400, 220, 50),
    pygame.Rect(700, 260, 50, 260),
    pygame.Rect(250, 90, 140, 40),
]


def raycast(x, y, ang, alcance=ALCANCE_MAX):
    """Marcha ao longo do feixe ate bater em algo ou estourar o alcance."""
    d = 0.0
    while d < alcance:
        px = x + math.cos(ang) * d
        py = y + math.sin(ang) * d
        if px < 0 or px > LARGURA or py < 0 or py > ALTURA:
            return d
        for obs in OBSTACULOS:
            if obs.collidepoint(px, py):
                return d
        d += PASSO_RAY
    return alcance


def filtro_limiar(d):
    """Devolve (valor_tratado, status). None = leitura descartada."""
    if d < LIMIAR_MIN:
        return None, "DESCARTADA"
    if d > ALCANCE_MAX:
        return ALCANCE_MAX, "CRAVADA"
    return d, "OK"


def varrer(x, y, th):
    """Roda a varredura completa e devolve uma lista de dicts por feixe."""
    leituras = []
    for i in range(N_FEIXES):
        
        offset = -FOV / 2 + i * (FOV / (N_FEIXES - 1))
        ang = th + offset
        d_real = raycast(x, y, ang)
        d_ruido = d_real + np.random.normal(0, SIGMA_RUIDO)
        d_filtrada, status = filtro_limiar(d_ruido)
        leituras.append({
            "i": i,
            "offset": offset,
            "ang": ang,
            "real": d_real,
            "bruta": d_ruido,
            "filtrada": d_filtrada,
            "status": status,
        })
    return leituras


def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Lab 3 - Varredura com ruido gaussiano + filtro")
    fonte = pygame.font.SysFont("consolas", 16)
    fonte_tit = pygame.font.SysFont("consolas", 19, bold=True)
    relogio = pygame.time.Clock()

    x, y, th = 200.0, 300.0, 0.0
    congelado = False
    leituras = varrer(x, y, th)
    rodando = True

    while rodando:
        dt = relogio.tick(30) / 1000.0

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                rodando = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    rodando = False
                elif ev.key == pygame.K_SPACE:
                    congelado = not congelado

        teclas = pygame.key.get_pressed()
        v = 0.0
        if teclas[pygame.K_UP]:
            v = 120.0
        if teclas[pygame.K_DOWN]:
            v = -120.0
        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
            th -= 1.6 * dt
        if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
            th += 1.6 * dt

        x = max(10, min(LARGURA - 10, x + v * math.cos(th) * dt))
        y = max(10, min(ALTURA - 10, y + v * math.sin(th) * dt))

        if not congelado:
            leituras = varrer(x, y, th)
          
        tela.fill(BRANCO)
        for obs in OBSTACULOS:
            pygame.draw.rect(tela, CINZA, obs)

        for lt in leituras:
            fim_real = (x + math.cos(lt["ang"]) * lt["real"],
                        y + math.sin(lt["ang"]) * lt["real"])
            pygame.draw.line(tela, (215, 215, 215), (x, y), fim_real, 1)

            if lt["filtrada"] is not None:
                fim_f = (x + math.cos(lt["ang"]) * lt["filtrada"],
                         y + math.sin(lt["ang"]) * lt["filtrada"])
                cor = LARANJA if lt["status"] == "CRAVADA" else VERDE
                pygame.draw.line(tela, cor, (x, y), fim_f, 2)
                pygame.draw.circle(tela, cor, (int(fim_f[0]), int(fim_f[1])), 4)
            else:
                fim_b = (x + math.cos(lt["ang"]) * max(lt["bruta"], 0),
                         y + math.sin(lt["ang"]) * max(lt["bruta"], 0))
                pygame.draw.line(tela, VERMELHO, (x, y), fim_b, 2)

        pygame.draw.circle(tela, AZUL, (int(x), int(y)), 11)
        pygame.draw.line(tela, PRETO, (x, y),
                         (x + 24 * math.cos(th), y + 24 * math.sin(th)), 3)

        # painel lateral com bruto x filtrado
        painel = pygame.Rect(LARGURA - 330, 10, 320, 250)
        pygame.draw.rect(tela, (255, 255, 255), painel)
        pygame.draw.rect(tela, PRETO, painel, 2)
        tela.blit(fonte_tit.render("FEIXE   BRUTO     FILTRADO", True, PRETO),
                  (painel.x + 12, painel.y + 10))
        for k, lt in enumerate(leituras):
            if lt["filtrada"] is None:
                txt_f, cor = "descartada", VERMELHO
            else:
                txt_f = f"{lt['filtrada']:7.2f}"
                cor = LARANJA if lt["status"] == "CRAVADA" else VERDE
            ang_deg = math.degrees(lt["offset"])
            linha = f"{ang_deg:+6.0f}deg {lt['bruta']:8.2f}   {txt_f}"
            tela.blit(fonte.render(linha, True, cor), (painel.x + 12, painel.y + 40 + k * 25))

        rodape = [
            f"ruido: N(0, {SIGMA_RUIDO}) | limiar min {LIMIAR_MIN} px | max {ALCANCE_MAX} px",
            "verde = OK   laranja = cravada no alcance   vermelho = descartada",
            f"setas = mover/girar   ESPACO = {'descongelar' if congelado else 'congelar'}   ESC = sair",
        ]
        for i, t in enumerate(rodape):
            tela.blit(fonte.render(t, True, PRETO), (15, ALTURA - 70 + i * 22))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
