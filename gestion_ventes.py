from datetime import datetime
from db_manager import DBManager

class GestionnaireVentes:
    def __init__(self):
        self.db = DBManager()
        self.ventes = [] # Cache optionnel

    def enregistrer_vente(self, medicament, quantite, prix_unitaire, vendeur_id=None):
        """
        Enregistre une vente dans la BD.
        """
        date_vente = datetime.now()
        prix_total = quantite * prix_unitaire
        
        # 1. Créer l'entrée dans la table 'ventes'
        # Pour simplifier on crée une vente par article ici, mais idéalement c'est un panier.
        # Restons sur le flow actuel : 1 clic = 1 vente.
        sql_vente = "INSERT INTO ventes (date_vente, vendeur_id, total) VALUES (%s, %s, %s)"
        # Note: mysql datetime format: 'YYYY-MM-DD HH:MM:SS'. datetime.now() works mostly ?
        # DBManager._adapt_query handles basics but parameter binding usually handles datetime objects correctly in python connectors.
        vente_id = self.db.execute_query(sql_vente, (date_vente, vendeur_id, prix_total))
        
        # 2. Créer la ligne de vente (optionnel si on suit le modèle simple actuel, mais demandé "lignes_vente")
        # Il faut l'ID du médicament.
        med_id = medicament.get('id') 
        # Si med_id manque (chargé depuis CSV legacy ou autre), faut le trouver.
        if not med_id:
             # Look it up
             res = self.db.fetch_one("SELECT id FROM medicaments WHERE nom = %s", (medicament['nom'],))
             if res:
                 med_id = res['id']
        
        if vente_id and med_id:
            sql_ligne = """
                INSERT INTO lignes_vente (vente_id, medicament_id, quantite, prix_unitaire, sous_total)
                VALUES (%s, %s, %s, %s, %s)
            """
            self.db.execute_query(sql_ligne, (vente_id, med_id, quantite, prix_unitaire, prix_total))

        # Retour pour affichage ticket
        vente_dict = {
            "id": vente_id,
            "date": date_vente.strftime("%Y-%m-%d %H:%M:%S"),
            "medicament": medicament['nom'],
            "quantite": quantite,
            "prix_unitaire": prix_unitaire,
            "prix_total": prix_total
        }
        print(f"Vente enregistrée : {medicament['nom']} x {quantite} = {prix_total:.2f}")
        return vente_dict

    def generer_ticket(self, vente):
        ticket = "      PHARMACIE Rach_Code\n" # Typo fix PHARACIE -> PHARMACIE
        ticket += f"----- Ticket de Vente ({vente.get('id', '?')}) -----\n"
        ticket += f"Date: {vente['date']}\n"
        ticket += f"Médicament: {vente['medicament']}\n"
        ticket += f"Quantité: {vente['quantite']}\n"
        ticket += f"Prix unitaire: {vente['prix_unitaire']:.2f}\n"
        ticket += f"Prix total: {vente['prix_total']:.2f}\n"
        ticket += f" Merci et bonne soiree a vous!\n"
        ticket += "-------------------------\n"
        return ticket

    def get_ventes_du_jour(self):
        # Récupérer depuis la BD date = today
        # Sur SQLite : strftime('%Y-%m-%d', date_vente)
        # Sur MySQL : DATE(date_vente)
        # On va tenter une approche python-side pour compatibilité max si le SQL differs trop
        # Ou SQL générique : 
        # SELECT * FROM ventes WHERE date_vente >= TODAY ...
        
        # Approche simple : Fetch all recent ? 
        # Let's try Query.
        today = datetime.now().strftime("%Y-%m-%d")
        # SQL : LIKE '2025-01-01%' works if stored as string/timestamp iso
        sql = "SELECT * FROM ventes WHERE date_vente LIKE %s ORDER BY date_vente DESC"
        formatted_date = f"{today}%"
        
        raw_ventes = self.db.fetch_all(sql, (formatted_date,))
        
        # Enrichir avec nom médicament (qui n'est pas dans la table vente directement si on normalise)
        # Mais dans le code actuel 'enregistrer_vente' retourne un dict riche.
        # Ici get_ventes_du_jour est utilisé pour l'export.
        
        # Reconstitution des objets ventes pour l'export
        ventes_enrichies = []
        for v in raw_ventes:
            # Get ligne de vente
            sql_lignes = """
                SELECT lv.*, m.nom as nom_medicament 
                FROM lignes_vente lv 
                JOIN medicaments m ON lv.medicament_id = m.id 
                WHERE lv.vente_id = %s
            """
            lignes = self.db.fetch_all(sql_lignes, (v['id'],))
            for l in lignes:
                ventes_enrichies.append({
                    "date": str(v['date_vente']),
                    "medicament": l['nom_medicament'],
                    "quantite": l['quantite'],
                    "prix_unitaire": float(l['prix_unitaire']),
                    "prix_total": float(l['sous_total'])
                })
        return ventes_enrichies

if __name__ == '__main__':
    gv = GestionnaireVentes()
    # Test simple sans mock medicament complex
    pass
