# simple-port-scanner - Scanner de Ports TCP Multi-threadé

Un scanner de ports réseaux simple, rapide et efficace écrit en **Python 3**. Ce script utilise le multi-threading pour scanner rapidement des plages de ports TCP et identifie les services associés aux ports ouverts.

## Fonctionnalités

* **Multi-threading** : Utilise jusqu'à 100 threads simultanés pour accélérer considérablement le scan.
* **Plage de ports flexible** : Scannez un seul port, une plage spécifique (ex: 20-100) ou la plage par défaut.
* **Résolution de nom** : Accepte les adresses IP (IPv4) ou les noms de domaine (ex: `google.com`).
* **Identification de service** : Tente de déterminer le nom du service standard (HTTP, SSH, FTP, etc.) pour chaque port ouvert.
* **Export de rapport** : Possibilité de sauvegarder les résultats dans un fichier `.txt` propre.
* **Aucune dépendance externe** : Utilise uniquement les bibliothèques standards de Python.

## Prérequis

- Python 3.9+

## Installation

1.  Clonez ce dépôt ou téléchargez le fichier `scanner.py`.
```bash
git clone https://github.com/matthieupcyb/simple-port-scanner.git
```
3.  Assurez-vous d'avoir Python installé :
```bash
python --version
```

## Utilisation

La syntaxe de base est la suivante :
```bash
python scanner.py <CIBLE> [OPTIONS]
```

### Arguments

|Argument|Description|
|---|---|
|`target`|(Obligatoire) L'adresse IP ou le nom de domaine à scanner.|
|`-p`, `--ports`|Plage de ports à scanner. Format Début-Fin (ex: 1-1024). Défaut : 1-1024.|
|`-f`, `--file`|Nom du fichier pour sauvegarder les résultats (ex: rapport.txt).|
|`-h`, `--help`|Affiche l'aide et la liste des commandes.|

### Exemples 

1. Scan basique (ports 1 à 1024 par défaut) :
```Bashpython 
scanner.py 192.168.1.1
```

2. Scan d'une plage spécifique sur un domaine :
```Bashpython 
scanner.py google.com -p 80-443
```

3. Scan avec sauvegarde des résultats dans un fichier :
```Bashpython
scanner.py 127.0.0.1 -p 1-5000 -f resultat_scan.txt
```


### Exemple de Résultats

```Plaintext
--------------------------------------------------
La cible de ce scan est : google.com (142.250.75.238)
Heure de début : 10-12-2023 14:30:00
--------------------------------------------------
[i] Lancement de 100 threads pour scanner 1000 ports...

--- RÉSULTATS ---
[+] Port 80    : OUVERT (http)
[+] Port 443   : OUVERT (https)

[i] Résultats sauvegardés dans resultat_scan.txt
```
