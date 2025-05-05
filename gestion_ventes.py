from datetime import datetime

class GestionnaireVentes:
    def __init__(self):
        self.ventes = []

    def enregistrer_vente(self, medicament, quantite, prix_unitaire):
        """
        Enregistre une vente.

        Args:
            medicament (dict): Le dictionnaire représentant le médicament vendu.
            quantite (int): La quantité vendue.
            prix_unitaire (float): Le prix unitaire du médicament au moment de la vente.
        """
        date_vente = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prix_total = quantite * prix_unitaire
        vente = {
            "date": date_vente,
            "medicament": medicament['nom'],
            "quantite": quantite,
            "prix_unitaire": prix_unitaire,
            "prix_total": prix_total
        }
        self.ventes.append(vente)
        print(f"Vente enregistrée : {medicament['nom']} x {quantite} à {prix_unitaire:.2f} = {prix_total:.2f}")
        return vente

    def generer_ticket(self, vente):
        """
        Génère un texte représentant le ticket de vente.

        Args:
            vente (dict): Les informations de la vente.

        Returns:
            str: Le texte formaté du ticket de vente.
        """
        ticket = "      PHARACIE Rach_Code\n"
        ticket += f"----- Ticket de Vente -----\n"
        ticket += f"Date: {vente['date']}\n"
        ticket += f"Médicament: {vente['medicament']}\n"
        ticket += f"Quantité: {vente['quantite']}\n"
        ticket += f"Prix unitaire: {vente['prix_unitaire']:.2f}\n"
        ticket += f"Prix total: {vente['prix_total']:.2f}\n"

        ticket += f" Merci et bonne soiree a vous!\n"
        ticket += "-------------------------\n"
        return ticket

    def get_ventes_du_jour(self):
        """
        Récupère la liste de toutes les ventes enregistrées.

        Returns:
            list: La liste des ventes.
        """
        return self.ventes

if __name__ == '__main__':
    # Exemple d'utilisation
    gestionnaire_ventes = GestionnaireVentes()
    medicament_vendu = {"nom": "Doliprane 1000mg"}
    vente1 = gestionnaire_ventes.enregistrer_vente(medicament_vendu, 2, 3.50)
    ticket1 = gestionnaire_ventes.generer_ticket(vente1)
    print("\n" + ticket1)

    medicament_vendu2 = {"nom": "Spasfon"}
    vente2 = gestionnaire_ventes.enregistrer_vente(medicament_vendu2, 1, 4.20)
    ticket2 = gestionnaire_ventes.generer_ticket(vente2)
    print("\n" + ticket2)

    print("\nVentes du jour :")
    for vente in gestionnaire_ventes.get_ventes_du_jour():
        print(vente)