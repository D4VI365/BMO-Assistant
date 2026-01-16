import pygame
import ollama
import threading
import os
import random

# --- Configurazione Percorsi ---
base_path = os.path.dirname(os.path.abspath(__file__))

# --- Inizializzazione Pygame ---
pygame.init()
screen = pygame.display.set_mode((800, 480))
pygame.display.set_caption("BMO Interface")

# --- Caricamento Assets ---
facce = []
for index in range(1, 31):
    nome_file = f"Rosto-{index}.png"
    percorso = os.path.join(base_path, "BMO_Faces", nome_file)
    if os.path.exists(percorso):
        img = pygame.image.load(percorso).convert_alpha()
        facce.append(pygame.transform.smoothscale(img, (800, 480)))

# --- Indici Immagini (ADATTA QUESTI NUMERI ALLE TUE IMMAGINI) ---
FACCIA_NORMALE = 0    # Indice della faccia base
FACCIA_CHIUSA = 3     # Indice occhi chiusi per blink
BOCCA_PARLA_1 = 1    # Indice bocca aperta 1
BOCCA_PARLA_2 = 4    # Indice bocca aperta 2

# --- Variabili di Stato e Timer ---
indice_attuale = FACCIA_NORMALE
bmo_sta_parlando = False
sta_sbattendo_palpebre = False

ultimo_battito = pygame.time.get_ticks()
ultimo_movimento_bocca = pygame.time.get_ticks()
intervallo_battito = random.randint(3000, 6000)

def chiedi_a_ollama(prompt):
    global bmo_sta_parlando
    bmo_sta_parlando = True  # Inizia l'animazione della bocca
    
    try:
        response = ollama.chat(model='bmo', messages=[{'role': 'user', 'content': prompt}])
        print(f"BMO: {response['message']['content']}")
    except Exception as e:
        print(f"Errore Ollama: {e}")
    
    bmo_sta_parlando = False # Ferma la bocca

# --- Ciclo Principale ---
running = True
while running:
    tempo_attuale = pygame.time.get_ticks()
    screen.fill((150, 220, 180)) # Colore corpo BMO

    # 1. GESTIONE EVENTI
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            domanda = input("Tu: ")
            threading.Thread(target=chiedi_a_ollama, args=(domanda,)).start()

    # 2. LOGICA ANIMAZIONE (Macchina a Stati)
    
    # Priorità 1: Se sta parlando, muovi la bocca velocemente
    if bmo_sta_parlando:
        if tempo_attuale - ultimo_movimento_bocca > 150: # Cambia bocca ogni 150ms
            if indice_attuale == BOCCA_PARLA_1:
                indice_attuale = BOCCA_PARLA_2
            else:
                indice_attuale = BOCCA_PARLA_1
            ultimo_movimento_bocca = tempo_attuale
            
    # Priorità 2: Se non parla, gestisci il battito di ciglia
    else:
        # Controllo per CHIUDERE gli occhi
        if not sta_sbattendo_palpebre and (tempo_attuale - ultimo_battito > intervallo_battito):
            indice_attuale = FACCIA_CHIUSA
            sta_sbattendo_palpebre = True
            ultimo_battito = tempo_attuale
        
        # Controllo per RIAPRIRE gli occhi
        if sta_sbattendo_palpebre and (tempo_attuale - ultimo_battito > 400): # 0.4 secondi
            indice_attuale = FACCIA_NORMALE
            sta_sbattendo_palpebre = False
            ultimo_battito = tempo_attuale
            intervallo_battito = random.randint(3000, 6000) # Nuovo intervallo casuale

    # 3. DISEGNO
    if facce:
        screen.blit(facce[indice_attuale], (0, 0))
    
    pygame.display.flip()

pygame.quit()