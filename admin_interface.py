import tkinter as tk
from tkinter import ttk, messagebox
from auth_manager import AuthManager

class FenetreGestionUtilisateurs:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Administration - Gestion des Utilisateurs")
        self.window.geometry("600x400")
        
        self.auth_manager = AuthManager()
        
        # Layout
        self.left_frame = ttk.Frame(self.window, padding="10")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.right_frame = ttk.Frame(self.window, padding="10")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # --- Liste des utilisateurs ---
        self.tree = ttk.Treeview(self.left_frame, columns=("ID", "Utilisateur", "Nom", "Rôle"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Utilisateur", text="Login")
        self.tree.heading("Nom", text="Nom Complet")
        self.tree.heading("Rôle", text="Rôle")
        
        self.tree.column("ID", width=30)
        self.tree.column("Utilisateur", width=100)
        self.tree.column("Nom", width=150)
        self.tree.column("Rôle", width=80)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Bouton Supprimer
        ttk.Button(self.left_frame, text="Supprimer Sélectionné", command=self.supprimer_utilisateur).pack(pady=5)
        
        # --- Formulaire Ajout ---
        ttk.Label(self.right_frame, text="Nouvel Utilisateur", font=("bold")).pack(pady=(0, 10))
        
        ttk.Label(self.right_frame, text="Login:").pack(anchor=tk.W)
        self.entry_login = ttk.Entry(self.right_frame)
        self.entry_login.pack(fill=tk.X, pady=2)
        
        ttk.Label(self.right_frame, text="Mot de passe:").pack(anchor=tk.W)
        self.entry_mdp = ttk.Entry(self.right_frame, show="*")
        self.entry_mdp.pack(fill=tk.X, pady=2)
        
        ttk.Label(self.right_frame, text="Nom Complet:").pack(anchor=tk.W)
        self.entry_nom = ttk.Entry(self.right_frame)
        self.entry_nom.pack(fill=tk.X, pady=2)
        
        ttk.Label(self.right_frame, text="Rôle:").pack(anchor=tk.W)
        self.combo_role = ttk.Combobox(self.right_frame, state="readonly")
        # Charger les rôles
        roles = self.auth_manager.get_roles()
        self.roles_map = {r['nom']: r['id'] for r in roles}
        self.combo_role['values'] = list(self.roles_map.keys())
        if self.roles_map:
            self.combo_role.current(0)
        self.combo_role.pack(fill=tk.X, pady=2)
        
        ttk.Button(self.right_frame, text="Créer Utilisateur", command=self.creer_utilisateur).pack(pady=10, fill=tk.X)
        
        self.charger_liste()

    def charger_liste(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        users = self.auth_manager.get_all_users()
        for u in users:
            self.tree.insert("", tk.END, values=(u['id'], u['nom_utilisateur'], u['nom_complet'], u['role_nom']))

    def creer_utilisateur(self):
        login = self.entry_login.get()
        mdp = self.entry_mdp.get()
        nom = self.entry_nom.get()
        role_nom = self.combo_role.get()
        
        if login and mdp and role_nom:
            try:
                role_id = self.roles_map[role_nom]
                if self.auth_manager.create_user(login, mdp, nom, role_id):
                    messagebox.showinfo("Succès", "Utilisateur créé")
                    self.entry_login.delete(0, tk.END)
                    self.entry_mdp.delete(0, tk.END)
                    self.entry_nom.delete(0, tk.END)
                    self.charger_liste()
                else:
                    messagebox.showerror("Erreur", "Echec création (Login existe déjà ?)")
            except Exception as e:
                messagebox.showerror("Erreur", str(e))
        else:
            messagebox.showwarning("Attention", "Veuillez remplir login et mot de passe")

    def supprimer_utilisateur(self):
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            user_id = self.tree.item(item, 'values')[0]
            if messagebox.askyesno("Confirmation", "Supprimer cet utilisateur ?"):
                if self.auth_manager.delete_user(user_id):
                    self.charger_liste()
                else:
                    messagebox.showerror("Erreur", "Impossible de supprimer (Admin principal ?)")
