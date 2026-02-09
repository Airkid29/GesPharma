from db_manager import DBManager

class GestionnaireStock:
    def __init__(self):
        """Initialise le gestionnaire de stock."""
        self.db = DBManager()
        self.medicaments = []
        self.charger_stock()

    def charger_stock(self):
        """Charge le stock de médicaments depuis la base de données."""
        query = "SELECT * FROM medicaments"
        try:
            self.medicaments = self.db.fetch_all(query)
            # Conversion des types pour compatibilité avec l'interface existante (prix en str, stock en str ?)
            # L'interface attend des dicts. fetch_all retourne déjà des dicts si configuré.
            # Cependant, mysql retourne Decimal, datetime etc.
            # On va s'assurer que c'est manipulable.
            for med in self.medicaments:
                # Normalisation pour l'affichage
                med['prix'] = str(med['prix'])
                med['stock'] = str(med['stock'])
                if 'date_expiration' in med and med['date_expiration']:
                    med['date_expiration'] = str(med['date_expiration'])
                
        except Exception as e:
            print(f"Erreur chargement stock: {e}")
            self.medicaments = []
        return self.medicaments

    def get_medicament(self, nom_medicament):
        """Recherche un médicament dans le cache."""
        # On pourrait faire une requête DB, mais pour l'instant on utilise le cache
        for medicament in self.medicaments:
            if medicament.get('nom') == nom_medicament:
                return medicament
        return None

    def search_medicaments(self, query_str):
        """Recherche DB directe (PLUS ROBUSTE)."""
        sql = "SELECT * FROM medicaments WHERE nom LIKE %s"
        # Note: DBManager._adapt_query gère le %s -> ? pour sqlite
        # Mais pour sqlite le LIKE est 'LIKE ?'.
        # Pour les wildcards, on passe '%query%'
        param = f"%{query_str}%"
        results = self.db.fetch_all(sql, (param,))
        return results

    def verifier_disponibilite(self, nom_medicament, quantite_demandee):
        med = self.get_medicament(nom_medicament) # Check cache first
        if med:
            # Vérification DB pour être sûr
            sql = "SELECT stock FROM medicaments WHERE nom = %s"
            db_res = self.db.fetch_one(sql, (nom_medicament,))
            if db_res:
                return int(db_res['stock']) >= quantite_demandee
        return False

    def vendre_medicament(self, nom_medicament, quantite_vendue):
        if self.verifier_disponibilite(nom_medicament, quantite_vendue):
            sql_update = "UPDATE medicaments SET stock = stock - %s WHERE nom = %s"
            self.db.execute_query(sql_update, (quantite_vendue, nom_medicament))
            self.charger_stock() # Rafraîchir le cache
            return True
        else:
            print(f"Stock insuffisant pour {nom_medicament}")
            return False

    def ajouter_medicament(self, nouveau_medicament):
        # Insert
        sql = """
            INSERT INTO medicaments (nom, prix, stock, date_expiration, numero_lot)
            VALUES (%s, %s, %s, %s, %s)
        """
        params = (
            nouveau_medicament.get('nom'),
            nouveau_medicament.get('prix'),
            nouveau_medicament.get('stock'),
            nouveau_medicament.get('date_expiration'),
            nouveau_medicament.get('numero_lot')
        )
        self.db.execute_query(sql, params)
        self.charger_stock()
        print(f"Médicament {nouveau_medicament.get('nom')} ajouté.")

    def modifier_medicament(self, nom_medicament, nouvelles_informations):
        # Update dynamique
        # On suppose que 'nouvelles_informations' contient les clés col.
        set_clauses = []
        params = []
        for key, value in nouvelles_informations.items():
            set_clauses.append(f"{key} = %s")
            params.append(value)
        
        if set_clauses:
            sql = f"UPDATE medicaments SET {', '.join(set_clauses)} WHERE nom = %s"
            params.append(nom_medicament)
            self.db.execute_query(sql, tuple(params))
            self.charger_stock()

if __name__ == '__main__':
    gs = GestionnaireStock()
    print("Stock actuel:", gs.medicaments)
