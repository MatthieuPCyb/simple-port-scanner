import socket
import threading
from queue import Queue, Empty
import argparse
import sys
from datetime import datetime
from typing import Optional


def scan_port(ip: str, port: int) -> Optional[str]:
    """Tente d'établir une connexion TCP sur un port spécifique.

    Cette fonction essaie de se connecter à l'adresse IP et au port donnés.
    Si la connexion réussit (code 0), elle tente de résoudre le nom du service.

    Args:
        ip (str): L'adresse IP cible (format IPv4).
        port (int): Le numéro de port à scanner.

    Returns:
        Optional[str]: Le nom du service (ou "Inconnu") si le port est ouvert, 
        None si le port est fermé ou filtré.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            state = s.connect_ex((ip, port))
            # On ferme explicitement, bien que le contexte 'with' le fasse aussi
            s.close() 
            
            if state == 0:
                try:
                    service = socket.getservbyport(port, 'tcp')
                except OSError:
                    service = 'Inconnu'
                return service
    except Exception:
        # En cas d'erreur critique de socket, on considère le port comme non accessible
        pass
    return None


def port_scanner(ip: str, q: Queue, results: list) -> None:
    """Fonction worker exécutée par les threads pour traiter la file d'attente.

    Récupère les numéros de ports depuis la file d'attente (Queue), lance le scan
    via `scan_port`, et ajoute les résultats positifs à la liste partagée.

    Args:
        ip (str): L'adresse IP cible.
        q (Queue): La file d'attente contenant les ports à scanner.
        results (list): La liste partagée pour stocker les résultats (thread-safe pour append).
    """
    while True:
        try:
            # Récupère un port de la file sans bloquer
            port = q.get_nowait()
        except Empty:
            # Si la file est vide, le thread s'arrête
            return
        
        try:
            service = scan_port(ip, port)
            if service:
                results.append((port, 'OUVERT', service))
        finally:
            # Indique à la queue que la tâche est traitée
            q.task_done()
        

def main() -> None:
    """Fonction principale pour l'initialisation et l'exécution du scanner.

    Gère :
    1. L'analyse des arguments en ligne de commande (argparse).
    2. La résolution de l'adresse IP cible.
    3. La création et le remplissage de la file d'attente (Queue).
    4. Le lancement des threads (workers).
    5. L'affichage et l'enregistrement des résultats.
    """
    parser = argparse.ArgumentParser(description='TCP port scanner')
    parser.add_argument('target', help='Adresse IP ou nom de domaine à scanner.')
    parser.add_argument('-p', '--ports', default='1-1024', help='Plage de ports à scanner (Ex: 1-100). Défaut: 1-1024')
    parser.add_argument('-f', '--file', dest="output_file", help='Enregistrement des résultats dans un fichier .txt')
    
    args = parser.parse_args()
    
    # --- Analyse de la plage de ports ---
    try:
        if '-' in args.ports:
            start_port, end_port = map(int, args.ports.split('-'))
        else:
            start_port = end_port = int(args.ports)
    except ValueError:
        print(f"[-] Erreur: Format de port invalide. Utilisez 'Debut-Fin' (ex: 1-100).")
        sys.exit(1)
    
    # --- Résolution IP ---
    try:
        target_ip = socket.gethostbyname(args.target)
    except socket.gaierror:
        print(f"[-] L'adresse IP ou le nom d'hôte spécifié {args.target} est introuvable")
        sys.exit(1)
        
    # --- Préparation de l'affichage ---
    header = '-' * 50
    scan_info = [
        header,
        f'La cible de ce scan est : {args.target} ({target_ip})',
        f"Heure de début : {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}",
        header
    ]
    
    for line in scan_info:
        print(line)

    # --- Initialisation de la Queue et des Threads ---
    q = Queue()
    results = []
    
    # Remplissage de la queue
    for i in range(start_port, end_port + 1):
        q.put(i)
        
    n_threads = min(100, q.qsize())
    print(f"[i] Lancement de {n_threads} threads pour scanner {q.qsize()} ports...")
    
    threads = []
    for _ in range(n_threads):
        t = threading.Thread(target=port_scanner, args=(target_ip, q, results))
        t.daemon = True
        t.start()
        threads.append(t)
        
    # --- Attente de la fin du scan ---
    try:
        q.join()
    except KeyboardInterrupt:
        print("\n[!] Interrompu par l'utilisateur")
        # On ne quitte pas immédiatement pour permettre l'affichage des résultats partiels
        
    # --- Traitement des résultats ---
    # Note : J'ai sorti le tri du bloc 'except' pour qu'il s'exécute aussi en cas de succès normal
    results.sort(key=lambda x: x[0])

    print("\n--- RÉSULTATS ---")
    if not results:
        print("Aucun port ouvert trouvé.")
    
    for port, status, service in results:
        print(f"[+] Port {port:<5} : {status} ({service})")

    # --- Écriture dans le fichier ---
    if args.output_file:
        try:
            with open(args.output_file, 'w') as f:
                # Écrire l'en-tête
                for line in scan_info:
                    f.write(line + '\n')
                
                f.write("Port,Status,Service\n")
                
                # Écrire les résultats
                for port, status, service in results:
                    f.write(f"{port},{status},{service}\n")
            
            print(f"\n[i] Résultats sauvegardés dans {args.output_file}")
        except IOError as e:
            print(f"[-] Erreur d'écriture fichier : {e}")
        
if __name__ == "__main__":
    main()