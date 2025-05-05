from base_de_donnees import charger_medicaments, sauvegarder_medicaments

class GestionnaireStock:
    def __init__(self):
        """Initialise le gestionnaire de stock en chargeant les médicaments."""
        self.medicaments = self._charger_stock()

    def _charger_stock(self):
        """Charge le stock de médicaments depuis la base de données."""
        return charger_medicaments()

    def _sauvegarder_stock(self):
        """Sauvegarde le stock de médicaments dans la base de données."""
        sauvegarder_medicaments(self.medicaments)

    def get_medicament(self, nom_medicament):
        """
        Recherche un médicament dans le stock par son nom (sensible à la casse).

        Args:
            nom_medicament (str): Le nom du médicament à rechercher.

        Returns:
            dict or None: Le dictionnaire représentant le médicament s'il est trouvé, sinon None.
        """
        for medicament in self.medicaments:
            if medicament.get('nom') == nom_medicament:
                return medicament
        return None

    def verifier_disponibilite(self, nom_medicament, quantite_demandee):
        """
        Vérifie si un médicament est disponible en quantité suffisante.

        Args:
            nom_medicament (str): Le nom du médicament.
            quantite_demandee (int): La quantité demandée.

        Returns:
            bool: True si le médicament est disponible en quantité suffisante, False sinon.
        """
        medicament = self.get_medicament(nom_medicament)
        if medicament and medicament.get('stock'):
            try:
                stock_actuel = int(medicament['stock'])
                return stock_actuel >= quantite_demandee
            except ValueError:
                print(f"Erreur : La valeur du stock pour '{nom_medicament}' n'est pas un nombre.")
                return False
        return False

    def vendre_medicament(self, nom_medicament, quantite_vendue):
        """
        Vend un médicament et met à jour le stock.

        Args:
            nom_medicament (str): Le nom du médicament vendu.
            quantite_vendue (int): La quantité vendue.

        Returns:
            bool: True si la vente a réussi (médicament trouvé et stock suffisant), False sinon.
        """
        medicament = self.get_medicament(nom_medicament)
        if medicament and medicament.get('stock'):
            try:
                stock_actuel = int(medicament['stock'])
                if stock_actuel >= quantite_vendue:
                    medicament['stock'] = str(stock_actuel - quantite_vendue)
                    self._sauvegarder_stock()
                    return True
                else:
                    print(f"Stock insuffisant pour '{nom_medicament}'. Stock actuel : {stock_actuel}, quantité demandée : {quantite_vendue}.")
                    return False
            except ValueError:
                print(f"Erreur : La valeur du stock pour '{nom_medicament}' n'est pas un nombre.")
                return False
        else:
            print(f"Médicament '{nom_medicament}' non trouvé.")
            return False

    def ajouter_medicament(self, nouveau_medicament):
        """
        Ajoute un nouveau médicament au stock.

        Args:
            nouveau_medicament (dict): Un dictionnaire représentant le nouveau médicament.
                                       Doit avoir les mêmes clés que les autres médicaments.
        """
        self.medicaments.append(nouveau_medicament)
        self._sauvegarder_stock()
        print(f"Le médicament '{nouveau_medicament.get('nom', 'Nouveau médicament')}' a été ajouté au stock.")

    def modifier_medicament(self, nom_medicament, nouvelles_informations):
        """
        Modifie les informations d'un médicament existant.

        Args:
            nom_medicament (str): Le nom du médicament à modifier.
            nouvelles_informations (dict): Un dictionnaire contenant les nouvelles informations.
                                        Les clés doivent correspondre aux noms des colonnes.
        """
        medicament = self.get_medicament(nom_medicament)
        if medicament:
            medicament.update(nouvelles_informations)
            self._sauvegarder_stock()
            print(f"Les informations pour '{nom_medicament}' ont été mises à jour.")
        else:
            print(f"Médicament '{nom_medicament}' non trouvé.")

if __name__ == '__main__':
    # Exemple d'utilisation du gestionnaire de stock
    gestionnaire = GestionnaireStock()

    # Afficher le stock initial
    print("Stock initial :")
    for medicament in gestionnaire.medicaments:
        print(medicament)

    # Vérifier la disponibilité
    nom_a_verifier = "Doliprane 1000mg"
    quantite_a_verifier = 5
    if gestionnaire.verifier_disponibilite(nom_a_verifier, quantite_a_verifier):
        print(f"\n{nom_a_verifier} est disponible en quantité suffisante ({quantite_a_verifier}).")
    else:
        print(f"\n{nom_a_verifier} n'est pas disponible en quantité suffisante ({quantite_a_verifier}).")

    # Vendre un médicament
    nom_a_vendre = "Spasfon"
    quantite_a_vendre = 2
    if gestionnaire.vendre_medicament(nom_a_vendre, quantite_a_vendre):
        print(f"\n{quantite_a_vendre} unités de {nom_a_vendre} ont été vendues.")

    # Afficher le stock après la vente
    print("\nStock après la vente :")
    for medicament in gestionnaire.medicaments:
        print(medicament)

    # Ajouter un nouveau médicament
    nouveau_medicament = {"nom": "Vitamine C 500mg", "prix": "5.00", "stock": "200", "date_expiration": "2028-06-30", "numero_lot": "LOT2025D"}
    gestionnaire.ajouter_medicament(nouveau_medicament)

    # Modifier un médicament
    gestionnaire.modifier_medicament("Doliprane 1000mg", {"prix": "3.75"})

    # Afficher le stock final
    print("\nStock final :")
    for medicament in gestionnaire.medicaments:
        print(medicament)