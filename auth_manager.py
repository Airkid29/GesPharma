import hashlib
from db_manager import DBManager

class AuthManager:
    def __init__(self):
        self.db = DBManager()
        self.utilisateur_connecte = None

    def login(self, username, password):
        """Tente de connecter un utilisateur."""
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        
        query = """
            SELECT u.id, u.nom_utilisateur, u.nom_complet, u.role_id, r.nom as role_nom
            FROM utilisateurs u
            JOIN roles r ON u.role_id = r.id
            WHERE u.nom_utilisateur = %s AND u.mot_de_passe_hache = %s
        """
        user = self.db.fetch_one(query, (username, hashed_pw))
        
        if user:
            self.utilisateur_connecte = user
            return True, user
        return False, None

    def logout(self):
        self.utilisateur_connecte = None

    def get_current_user(self):
        return self.utilisateur_connecte

    def create_user(self, username, password, nom_complet, role_id):
        """Crée un nouvel utilisateur (Admin only)."""
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        query = "INSERT INTO utilisateurs (nom_utilisateur, mot_de_passe_hache, nom_complet, role_id) VALUES (%s, %s, %s, %s)"
        return self.db.execute_query(query, (username, hashed_pw, nom_complet, role_id))

    def get_all_users(self):
        query = """
            SELECT u.id, u.nom_utilisateur, u.nom_complet, r.nom as role_nom
            FROM utilisateurs u
            JOIN roles r ON u.role_id = r.id
        """
        return self.db.fetch_all(query)

    def delete_user(self, user_id):
        """Supprime un utilisateur par ID."""
        # Empêcher de supprimer l'admin principal (id=1 par convention ici)
        if str(user_id) == "1":
            print("Impossible de supprimer l'admin principal.")
            return False
            
        return self.db.execute_query("DELETE FROM utilisateurs WHERE id = %s", (user_id,))

    def get_roles(self):
        """Récupère la liste des rôles disponibles."""
        return self.db.fetch_all("SELECT * FROM roles")

