import csv

CHEMIN_FICHIER_MEDICAMENTS = 'medicaments.csv'  # On définit le nom du fichier ici

def charger_medicaments():
    """
    Charge les médicaments depuis le fichier CSV.

    Returns:
        list: Une liste de dictionnaires, où chaque dictionnaire représente un médicament.
        Retourne une liste vide en cas d'erreur de lecture du fichier.
    """
    medicaments = []
    try:
        with open(CHEMIN_FICHIER_MEDICAMENTS, mode='r', newline='', encoding='utf-8') as fichier_csv:
            lecteur_csv = csv.DictReader(fichier_csv)
            for ligne in lecteur_csv:
                # Assurez-vous que les clés correspondent à l'en-tête de votre fichier CSV
                medicaments.append(ligne)
    except FileNotFoundError:
        print(f"Erreur : Le fichier '{CHEMIN_FICHIER_MEDICAMENTS}' n'a pas été trouvé.")
        return []
    except Exception as e:
        print(f"Une erreur est survenue lors de la lecture du fichier CSV : {e}")
        return []
    return medicaments

if __name__ == '__main__':
    # Ceci est un bloc de test qui s'exécute uniquement si on lance directement ce fichier
    medicaments_charges = charger_medicaments()
    if medicaments_charges:
        print("Medicaments charges :")
        for medicament in medicaments_charges:
            print(medicament)
    else:
        print("Aucun médicament n'a été chargé.")

#Sauvegarde des médicaments dans le fichier CSV
def sauvegarder_medicaments(liste_medicaments):
    """
    Sauvegarde la liste des médicaments dans le fichier CSV.

    Args:
        liste_medicaments (list): Une liste de dictionnaires représentant les médicaments.
    """
    try:
        with open(CHEMIN_FICHIER_MEDICAMENTS, mode='w', newline='', encoding='utf-8') as fichier_csv:
            if liste_medicaments:
                noms_colonnes = liste_medicaments[0].keys()
                ecrivain_csv = csv.DictWriter(fichier_csv, fieldnames=noms_colonnes)
                ecrivain_csv.writeheader()
                ecrivain_csv.writerows(liste_medicaments)
            else:
                # Si la liste est vide, on peut soit vider le fichier, soit ne rien faire.
                # Ici, on choisit de vider le fichier en réécrivant juste l'en-tête.
                ecrivain_csv = csv.writer(fichier_csv)
                # Si on avait un en-tête statique, on pourrait l'écrire ici.
                # Sinon, un fichier vide serait aussi une option.
                pass
        print("Les médicaments ont été sauvegardés.")
    except Exception as e:
        print(f"Une erreur est survenue lors de la sauvegarde des médicaments : {e}")

if __name__ == '__main__':
    # Test de la sauvegarde (après avoir chargé)
    medicaments_charges = charger_medicaments()
    if medicaments_charges:
        # Simuler une modification (on augmente le stock du premier médicament)
        if medicaments_charges[0].get('stock'):
            try:
                medicaments_charges[0]['stock'] = int(medicaments_charges[0]['stock']) + 10
            except ValueError:
                print("Erreur : La valeur du stock n'est pas un nombre.")
        sauvegarder_medicaments(medicaments_charges)
        print("\nAprès sauvegarde :")
        medicaments_charges_apres_sauvegarde = charger_medicaments()
        for medicament in medicaments_charges_apres_sauvegarde:
            print(medicament)