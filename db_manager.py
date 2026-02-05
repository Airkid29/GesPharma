import mysql.connector
from mysql.connector import Error
import sqlite3
import os
from db_config import DB_CONFIG
import hashlib

class DBManager:
    def __init__(self):
        self.connection = None
        self.mode = 'mysql' # 'mysql' or 'sqlite'
        self.sqlite_file = 'gespharma.db'

    def create_connection(self):
        """Etablit la connexion (MySQL ou Fallback SQLite)."""
        temp_config = DB_CONFIG.copy()
        db_name = temp_config.pop('database')

        # Tentative MySQL
        try:
            if self.mode == 'mysql':
                try:
                    self.connection = mysql.connector.connect(**temp_config)
                    if self.connection.is_connected():
                        cursor = self.connection.cursor()
                        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
                        self.connection.database = db_name
                        return self.connection
                except Error as e:
                    print(f"MySQL unavailable ({e}). Switching to SQLite fallback.")
                    self.mode = 'sqlite'
        
        except Exception as e:
             print(f"Connection error: {e}. Switching to SQLite.")
             self.mode = 'sqlite'

        # Fallback SQLite
        if self.mode == 'sqlite':
            try:
                self.connection = sqlite3.connect(self.sqlite_file)
                return self.connection
            except sqlite3.Error as e:
                print(f"SQLite error: {e}")
                return None
        return None

    def close_connection(self):
        if self.connection:
            self.connection.close()

    def _adapt_query(self, query):
        """Adapte la requête SQL selon le mode (MySQL vs SQLite)."""
        if self.mode == 'sqlite':
            # Remplacement basique des placeholders
            query = query.replace('%s', '?')
            # Ajustements syntaxiques pour la création de tables si nécessaire
            # SQLite gère 'INTEGER PRIMARY KEY' comme auto-increment.
            # MySQL utilise 'INT AUTO_INCREMENT PRIMARY KEY'.
            # On peut nettoyer 'AUTO_INCREMENT' pour SQLite car ignoré ou erreur.
            query = query.replace('AUTO_INCREMENT', '') 
            query = query.replace('DATETIME DEFAULT CURRENT_TIMESTAMP', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
        return query

    def init_db(self):
        """Initialise la structure de la base de données."""
        if not self.create_connection():
            return False

        try:
            cursor = self.connection.cursor()
            
            # --- Tables ---
            # Pour SQLite, on doit s'assurer que les clés étrangères sont activées
            if self.mode == 'sqlite':
                cursor.execute("PRAGMA foreign_keys = ON;")

            tables = [
                """CREATE TABLE IF NOT EXISTS roles (
                    id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    nom VARCHAR(50) NOT NULL UNIQUE,
                    description TEXT
                )""",
                """CREATE TABLE IF NOT EXISTS utilisateurs (
                    id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    nom_utilisateur VARCHAR(50) NOT NULL UNIQUE,
                    mot_de_passe_hache VARCHAR(255) NOT NULL,
                    nom_complet VARCHAR(100),
                    role_id INTEGER,
                    FOREIGN KEY (role_id) REFERENCES roles(id)
                )""",
                """CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    nom VARCHAR(50) NOT NULL UNIQUE,
                    description TEXT
                )""",
                """CREATE TABLE IF NOT EXISTS medicaments (
                    id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    nom VARCHAR(100) NOT NULL,
                    prix DECIMAL(10, 2) NOT NULL,
                    stock INTEGER NOT NULL DEFAULT 0,
                    date_expiration DATE,
                    numero_lot VARCHAR(50),
                    category_id INTEGER,
                    FOREIGN KEY (category_id) REFERENCES categories(id)
                )""",
                """CREATE TABLE IF NOT EXISTS ventes (
                    id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    date_vente TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    vendeur_id INTEGER,
                    total DECIMAL(10, 2) NOT NULL,
                    FOREIGN KEY (vendeur_id) REFERENCES utilisateurs(id)
                )""",
                """CREATE TABLE IF NOT EXISTS lignes_vente (
                    id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    vente_id INTEGER,
                    medicament_id INTEGER,
                    quantite INTEGER NOT NULL,
                    prix_unitaire DECIMAL(10, 2) NOT NULL,
                    sous_total DECIMAL(10, 2) NOT NULL,
                    FOREIGN KEY (vente_id) REFERENCES ventes(id),
                    FOREIGN KEY (medicament_id) REFERENCES medicaments(id)
                )"""
            ]

            for query in tables:
                final_query = self._adapt_query(query)
                # Correction spécifique pour SQLite 'INTEGER PRIMARY KEY'
                if self.mode == 'sqlite':
                     final_query = final_query.replace('INTEGER PRIMARY KEY AUTO_INCREMENT', 'INTEGER PRIMARY KEY')
                     final_query = final_query.replace('INT AUTO_INCREMENT PRIMARY KEY', 'INTEGER PRIMARY KEY')
                else: 
                     # MySQL: INTEGER PRIMARY KEY AUTO_INCREMENT est valide ou INT ...
                     final_query = final_query.replace('INTEGER PRIMARY KEY AUTO_INCREMENT', 'INT AUTO_INCREMENT PRIMARY KEY')

                cursor.execute(final_query)

            # --- Données par défaut ---
            # Insertions (IGNORE pour MySQL, OR IGNORE pour SQLite)
            insert_ignore = "INSERT IGNORE" if self.mode == 'mysql' else "INSERT OR IGNORE"
            
            # Rôles
            cursor.execute(f"{insert_ignore} INTO roles (id, nom, description) VALUES (1, 'Admin', 'Administrateur système')")
            cursor.execute(f"{insert_ignore} INTO roles (id, nom, description) VALUES (2, 'Caissier', 'Vendeur')")

            # Admin
            mdp_admin = hashlib.sha256("admin".encode()).hexdigest()
            # Note: ? vs %s est géré par _adapt_query mais ici on construit la string direct ou on utilise les params
            # Utilisons les params pour être propre
            q_user = f"{insert_ignore} INTO utilisateurs (nom_utilisateur, mot_de_passe_hache, nom_complet, role_id) VALUES (%s, %s, %s, %s)"
            params_user = ('admin', mdp_admin, 'Administrateur', 1)
            cursor.execute(self._adapt_query(q_user), params_user)

            # Catégorie
            cursor.execute(f"{insert_ignore} INTO categories (id, nom, description) VALUES (1, 'Général', 'Produits généraux')")

            self.connection.commit()
            print(f"Base de données initialisée ({self.mode}).")
            return True

        except Exception as e: # Catch all for simplicity in this fallback logic
            print(f"Erreur init_db ({self.mode}) : {e}")
            return False
        finally:
            cursor.close()
            self.close_connection()

    def execute_query(self, query, params=None):
        if not self.create_connection():
            return None
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(self._adapt_query(query), params or ())
            self.connection.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Erreur execute_query ({self.mode}) : {e}")
            return None
        finally:
            cursor.close()
            self.close_connection()

    def fetch_all(self, query, params=None):
        if not self.create_connection():
            return []
            
        try:
            # SQLite cursor doesn't support dictionary=True natively in constructor easily across versions without row_factory
            if self.mode == 'sqlite':
                self.connection.row_factory = sqlite3.Row
                cursor = self.connection.cursor()
            else:
                cursor = self.connection.cursor(dictionary=True)
                
            cursor.execute(self._adapt_query(query), params or ())
            
            if self.mode == 'sqlite':
                # Convert sqlite3.Row to dict
                results = [dict(row) for row in cursor.fetchall()]
            else:
                results = cursor.fetchall()
            return results
        except Exception as e:
            print(f"Erreur fetch_all ({self.mode}) : {e}")
            return []
        finally:
            cursor.close()
            self.close_connection()

    def fetch_one(self, query, params=None):
        results = self.fetch_all(query, params)
        if results:
            return results[0]
        return None

if __name__ == '__main__':
    db = DBManager()
    db.init_db()
