import openpyxl
from datetime import datetime

def exporter_ventes_excel(liste_ventes, nom_fichier="ventes_du_jour.xlsx"):
    """
    Exporte la liste des ventes vers un fichier Excel.

    Args:
        liste_ventes (list): La liste des dictionnaires de ventes.
        nom_fichier (str, optional): Le nom du fichier Excel à créer.
                                    Par défaut, "ventes_du_jour.xlsx".
    """
    if not liste_ventes:
        print("Aucune vente à exporter.")
        return

    classeur = openpyxl.Workbook()
    feuille = classeur.active
    feuille.title = "Ventes"

    # Ajouter l'en-tête
    en_tete = ["Date", "Médicament", "Quantité", "Prix Unitaire", "Prix Total"]
    feuille.append(en_tete)

    # Ajouter les données des ventes
    for vente in liste_ventes:
        ligne = [
            vente['date'],
            vente['medicament'],
            vente['quantite'],
            vente['prix_unitaire'],
            vente['prix_total']
        ]
        feuille.append(ligne)

    try:
        classeur.save(nom_fichier)
        print(f"Les ventes ont été exportées vers '{nom_fichier}'.")
    except Exception as e:
        print(f"Erreur lors de l'exportation vers Excel : {e}")

if __name__ == '__main__':
    # Exemple d'utilisation
    from gestion_ventes import GestionnaireVentes
    gestionnaire_ventes = GestionnaireVentes()
    medicament_vendu1 = {"nom": "Doliprane 1000mg"}
    gestionnaire_ventes.enregistrer_vente(medicament_vendu1, 2, 3.50)
    medicament_vendu2 = {"nom": "Spasfon"}
    gestionnaire_ventes.enregistrer_vente(medicament_vendu2, 1, 4.20)

    ventes_a_exporter = gestionnaire_ventes.get_ventes_du_jour()
    exporter_ventes_excel(ventes_a_exporter)