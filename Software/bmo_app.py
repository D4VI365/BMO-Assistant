import pygame
import ollama
import threading
import os
import random
import speech_recognition as sr # NUOVO: Per il riconoscimento vocale

WAKE_WORDS = ["bmo", "bi mo", "beemo", "bimo", "demo", "nemo", "memo", "di mo", "vi amo"]

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

def gestore_risposta_vocale():
    """Funzione che viene chiamata quando viene rilevata la Wake Word"""
    global bmo_sta_parlando
    # Qui chiamiamo la funzione di ascolto che abbiamo creato prima
    # BMO potrebbe fare una faccia "interrogativa" qui
    ascolta_voce() 

def loop_ascolto_passivo():
    r = sr.Recognizer()
    mic = sr.Microphone()
    
    print(f"BMO ti ascolta... (puoi dire: {WAKE_WORDS})")
    
    while True:
        with mic as source:
            r.adjust_for_ambient_noise(source, duration=0.5)
            # timeout=None significa che aspetta all'infinito
            try:
                audio = r.listen(source, timeout=None, phrase_time_limit=3)
            except sr.WaitTimeoutError:
                continue
        
        try:
            # Stampiamo cosa ha capito Google per fare debug
            frase = r.recognize_google(audio, language="it-IT").lower()
            print(f"Ho sentito: '{frase}'") 
            
            # Controlla se ALMENO UNA delle parole nella lista è nella frase
            if any(parola in frase for parola in WAKE_WORDS):
                print("Wake word rilevata! 🤖")
                gestore_risposta_vocale()
                
        except sr.UnknownValueError:
            continue
        except Exception as e:
            print(f"Errore: {e}")
            continue

# --- FUNZIONE DI ASCOLTO ---
def ascolta_voce():
    global bmo_sta_parlando
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("BMO ti ascolta...")
        # Regola il rumore di fondo
        r.adjust_for_ambient_noise(source, duration=1)
        audio = r.listen(source)

    try:
        # Trasforma l'audio in testo usando Google (richiede internet)
        domanda = r.recognize_google(audio, language="it-IT")
        print(f"Tu hai detto: {domanda}")
        # Avvia Ollama con quello che ha capito
        threading.Thread(target=chiedi_a_ollama, args=(domanda,)).start()
    except sr.UnknownValueError:
        print("BMO non ha capito cosa hai detto.")
    except sr.RequestError as e:
        print(f"Errore del servizio di riconoscimento; {e}")

def chiedi_a_ollama(prompt):
    global bmo_sta_parlando
    bmo_sta_parlando = True  # Inizia l'animazione della bocca
    
    try:
        response = ollama.chat(model='bmo', messages=[{'role': 'user', 'content': prompt}])
        print(f"BMO: {response['message']['content']}")
    except Exception as e:
        print(f"Errore Ollama: {e}")
    
    bmo_sta_parlando = False # Ferma la bocca

threading.Thread(target=loop_ascolto_passivo, daemon=True).start()

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
            """domanda = input("Tu: ")
            threading.Thread(target=chiedi_a_ollama, args=(domanda,)).start()"""
            threading.Thread(target=ascolta_voce).start()

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