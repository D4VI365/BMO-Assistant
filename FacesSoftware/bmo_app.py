import pygame
import ollama
import threading
import os
import random

# Ottiene la cartella dove si trova lo script .py
base_path = os.path.dirname(os.path.abspath(__file__))

# --- Configurazione Iniziale ---
pygame.init()
screen = pygame.display.set_mode((800, 480)) # Risoluzione del tuo futuro schermo touch
pygame.display.set_caption("BMO Interface")

# --- Caricamento Immagini ---
string1 = "Rosto-"
ext = ".png"
facce=[]
for index in range(1, 31): # Cicla da 1 a 30
    nome_file = f"Rosto-{index}.png" # Costruisce Rosto-1.png, Rosto-2.png...
    percorso = os.path.join(base_path, "BMO_Faces", nome_file)
    
    if os.path.exists(percorso):
        img = pygame.image.load(percorso).convert_alpha()
        img_scaled = pygame.transform.smoothscale(img, (800, 480))
        facce.append(img_scaled) # Aggiunge l'immagine reale alla lista

# --- Variabili di Stato ---
testo_da_dire = ""
bmo_sta_pensando = False

ultimo_aggiornamento = pygame.time.get_ticks()
intervallo_faccia = 3000  # Cambia ogni 3 secondi (3000 millisecondi)

# Indici delle tue immagini (controlla quali numeri corrispondono nel tuo set)
FACCIA_NORMALE = 0     # Esempio: Rosto-1.png
FACCIA_CHIUSA = 3      # Esempio: Rosto-6.png (quella con gli occhi chiusi)

indice_faccia_attuale = FACCIA_NORMALE
ultimo_battito = pygame.time.get_ticks()

sta_sbattendo_palpebre = False

# Tempistiche
intervallo_tra_battiti = random.randint(3000, 7000)
durata_occhi_chiusi = 300      # 0.4 secondi (400 millisecondi)

def chiedi_a_ollama(prompt):
    global testo_da_dire, bmo_sta_pensando
    bmo_sta_pensando = True
    
    response = ollama.chat(model='bmo', messages=[{'role': 'user', 'content': prompt}])
    testo_da_dire = response['message']['content']
    
    print(f"BMO dice: {testo_da_dire}")
    bmo_sta_pensando = False


# --- Ciclo Principale ---
running = True
while running:
    tempo_attuale = pygame.time.get_ticks()

    # CASO 1: È ora di chiudere gli occhi?
    if not sta_sbattendo_palpebre and (tempo_attuale - ultimo_battito > intervallo_tra_battiti):
        indice_faccia_attuale = FACCIA_CHIUSA
        sta_sbattendo_palpebre = True
        ultimo_battito = tempo_attuale  # Segnamo quando abbiamo chiuso gli occhi

    # CASO 2: Gli occhi sono chiusi da abbastanza tempo (0.4s)? 
    if sta_sbattendo_palpebre and (tempo_attuale - ultimo_battito > durata_occhi_chiusi):
        indice_faccia_attuale = FACCIA_NORMALE
        sta_sbattendo_palpebre = False
        ultimo_battito = tempo_attuale  # Reset per aspettare i prossimi 5 secondi
        intervallo_tra_battiti = random.randint(3000, 7000)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Simula il tasto "Cerchio" di BMO con la Barra Spaziatrice
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                domanda = input("Tu: ") # Per ora scrivi nel terminale
                # Usiamo un thread così l'animazione non si blocca mentre l'IA pensa
                threading.Thread(target=chiedi_a_ollama, args=(domanda,)).start()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running =False

    # --- Disegno della Faccia ---
    screen.blit(facce[indice_faccia_attuale], (0, 0))
    
    # Se BMO sta pensando, aggiungiamo un piccolo indicatore (o cambiamo immagine)
    if bmo_sta_pensando:
        pygame.draw.circle(screen, (255, 255, 255), (400, 400), 20)
    
    pygame.display.flip()

pygame.quit()