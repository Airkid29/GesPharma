import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from gestion_stock import GestionnaireStock
from gestion_ventes import GestionnaireVentes
from auth_manager import AuthManager
from rapports import exporter_ventes_excel

class FenetreConnexion:
    def __init__(self, master, on_login_success):
        self.master = master
        self.on_login_success = on_login_success
        self.auth_manager = AuthManager()
        
        self.master.title("Connexion - GesPharma")
        self.master.geometry("300x220")
        self.master.resizable(False, False)
        
        # Centrer la fenêtre
        self.center_window()

        main_frame = ttk.Frame(self.master, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Nom d'utilisateur:").pack(anchor=tk.W, pady=(0, 5))
        self.username_entry = ttk.Entry(main_frame)
        self.username_entry.pack(fill=tk.X, pady=(0, 10))
        self.username_entry.focus()

        ttk.Label(main_frame, text="Mot de passe:").pack(anchor=tk.W, pady=(0, 5))
        self.password_entry = ttk.Entry(main_frame, show="*")
        self.password_entry.pack(fill=tk.X, pady=(0, 15))
        self.password_entry.bind('<Return>', lambda e: self.tenter_connexion())

        self.login_button = ttk.Button(main_frame, text="Se connecter", command=self.tenter_connexion)
        self.login_button.pack(fill=tk.X)
        
        # Default status
        self.status_label = ttk.Label(main_frame, text="", foreground="red")
        self.status_label.pack(pady=(10, 0))

    def center_window(self):
        self.master.update_idletasks()
        width = self.master.winfo_width()
        height = self.master.winfo_height()
        x = (self.master.winfo_screenwidth() // 2) - (width // 2)
        y = (self.master.winfo_screenheight() // 2) - (height // 2)
        self.master.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def tenter_connexion(self):
        user = self.username_entry.get()
        pwd = self.password_entry.get()
        
        success, user_data = self.auth_manager.login(user, pwd)
        if success:
            self.on_login_success(user_data)
        else:
            self.status_label.config(text="Identifiants incorrects")
            self.password_entry.delete(0, tk.END)

class FenetrePrincipale:
    def __init__(self, master, current_user):
        self.master = master
        self.current_user = current_user
        master.title(f"Gestion de Pharmacie - {current_user['nom_complet']} ({current_user['role_nom']})")
        
        # Maximize window
        master.state('zoomed')

        self.gestionnaire_stock = GestionnaireStock()
        self.gestionnaire_ventes = GestionnaireVentes()
        self.medicament_selectionne = None

        # --- Barre de menus (Déconnexion / Admin) ---
        menubar = tk.Menu(master)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Déconnexion", command=self.deconnexion)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=master.quit)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        
        if self.current_user['role_nom'] == 'Admin':
            admin_menu = tk.Menu(menubar, tearoff=0)
            from admin_interface import FenetreGestionUtilisateurs
            admin_menu.add_command(label="Gestion Utilisateurs", command=lambda: FenetreGestionUtilisateurs(master))
            menubar.add_cascade(label="Administration", menu=admin_menu)

        master.config(menu=menubar)

        # --- Zone de recherche ---
        self.frame_top = ttk.Frame(master, padding="10")
        self.frame_top.grid(row=0, column=0, columnspan=3, sticky="ew")
        
        ttk.Label(self.frame_top, text="Nom du médicament :").pack(side=tk.LEFT, padx=5)
        self.entry_recherche = ttk.Entry(self.frame_top)
        self.entry_recherche.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.entry_recherche.bind('<Return>', lambda e: self.rechercher_medicament())
        
        ttk.Button(self.frame_top, text="Rechercher", command=self.rechercher_medicament).pack(side=tk.LEFT, padx=5)

        # --- Zone d'affichage du stock complet ---
        self.label_stock_complet = ttk.LabelFrame(master, text="Stock Disponibles", padding="10")
        self.label_stock_complet.grid(row=1, column=0, columnspan=3, padx=10, pady=5, sticky="nsew")

        self.treeview_stock = ttk.Treeview(self.label_stock_complet, columns=("Nom", "Prix", "Stock", "Expiration", "Lot"))
        self.treeview_stock.heading("#1", text="Nom")
        self.treeview_stock.heading("#2", text="Prix")
        self.treeview_stock.heading("#3", text="Stock")
        self.treeview_stock.heading("#4", text="Expiration")
        self.treeview_stock.heading("#5", text="Lot")
        self.treeview_stock.column("#1", stretch=tk.YES)
        self.treeview_stock.column("#2", stretch=tk.NO, width=100)
        self.treeview_stock.column("#3", stretch=tk.NO, width=80)
        self.treeview_stock.column("#4", stretch=tk.NO, width=120)
        self.treeview_stock.column("#5", stretch=tk.NO, width=100)
        
        scrollbar = ttk.Scrollbar(self.label_stock_complet, orient=tk.VERTICAL, command=self.treeview_stock.yview)
        self.treeview_stock.configure(yscroll=scrollbar.set)
        
        self.treeview_stock.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.charger_stock_dans_liste()

        # --- Panneau Inférieur (Infos & Vente & Ajout) ---
        self.frame_bottom = ttk.Frame(master, padding="10")
        self.frame_bottom.grid(row=2, column=0, columnspan=3, sticky="nsew")

        # Infos Médicament (Gauche)
        self.frame_info = ttk.LabelFrame(self.frame_bottom, text="Infos Médicament", padding="10")
        self.frame_info.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.nom_var = tk.StringVar()
        self.prix_var = tk.StringVar()
        self.stock_var = tk.StringVar()
        
        ttk.Label(self.frame_info, text="Nom:").grid(row=0, column=0, sticky="w")
        ttk.Label(self.frame_info, textvariable=self.nom_var, font=('bold')).grid(row=0, column=1, sticky="w")
        ttk.Label(self.frame_info, text="Prix:").grid(row=1, column=0, sticky="w")
        ttk.Label(self.frame_info, textvariable=self.prix_var).grid(row=1, column=1, sticky="w")
        ttk.Label(self.frame_info, text="Stock:").grid(row=2, column=0, sticky="w")
        ttk.Label(self.frame_info, textvariable=self.stock_var).grid(row=2, column=1, sticky="w")

        # Vente (Centre)
        self.frame_vente = ttk.LabelFrame(self.frame_bottom, text="Vente", padding="10")
        self.frame_vente.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        ttk.Label(self.frame_vente, text="Quantité:").pack(anchor=tk.W)
        self.entry_quantite_vente = ttk.Entry(self.frame_vente)
        self.entry_quantite_vente.pack(fill=tk.X, pady=5)
        
        self.bouton_vendre = ttk.Button(self.frame_vente, text="Vendre", command=self.vendre_et_imprimer)
        self.bouton_vendre.pack(fill=tk.X, pady=5)
        
        # Ajout (Droite) - Seulement si Admin
        if self.current_user['role_nom'] == 'Admin':
            self.frame_ajout = ttk.LabelFrame(self.frame_bottom, text="Ajout Stock", padding="10")
            self.frame_ajout.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
            
            # Champs d'ajout compacts
            self.entry_nouveau_nom = self.create_labeled_entry(self.frame_ajout, "Nom:", 0)
            self.entry_nouveau_prix = self.create_labeled_entry(self.frame_ajout, "Prix:", 1)
            self.entry_nouveau_stock = self.create_labeled_entry(self.frame_ajout, "Stock:", 2)
            self.entry_nouveau_expiration = self.create_labeled_entry(self.frame_ajout, "Exp:", 3)
            self.entry_nouveau_lot = self.create_labeled_entry(self.frame_ajout, "Lot:", 4)
            
            ttk.Button(self.frame_ajout, text="Ajouter", command=self.ajouter_nouveau_medicament).grid(row=5, column=0, columnspan=2, pady=5, sticky="ew")

        # Bouton export global
        ttk.Button(master, text="Exporter Ventes Jour", command=self.exporter_rapport).grid(row=3, column=0, columnspan=3, pady=10)

        # Configuration Grille
        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(1, weight=1)

        self.treeview_stock.bind("<Double-1>", self.selectionner_medicament_dans_liste)
        self.treeview_stock.bind("<<TreeviewSelect>>", self.selectionner_medicament_dans_liste)

    def create_labeled_entry(self, parent, text, row):
        ttk.Label(parent, text=text).grid(row=row, column=0, sticky="w")
        entry = ttk.Entry(parent, width=15)
        entry.grid(row=row, column=1, sticky="ew")
        return entry

    def deconnexion(self):
        self.master.destroy()
        main() # Restart

    def charger_stock_dans_liste(self):
        for item in self.treeview_stock.get_children():
            self.treeview_stock.delete(item)
        
        # On peut avoir une liste filtrée si recherche e.e
        stock = self.gestionnaire_stock.medicaments
        # Si recherche active (mais ici on recharge tout pour clean)
        
        for medicament in stock:
            self.treeview_stock.insert("", tk.END, values=(
                medicament.get('nom', ''),
                medicament.get('prix', ''),
                medicament.get('stock', ''),
                medicament.get('date_expiration', ''),
                medicament.get('numero_lot', '')
            ))

    def rechercher_medicament(self):
        query = self.entry_recherche.get()
        if query:
            results = self.gestionnaire_stock.search_medicaments(query)
            # Update treeview only
            for item in self.treeview_stock.get_children():
                self.treeview_stock.delete(item)
            for medicament in results:
                self.treeview_stock.insert("", tk.END, values=(
                    medicament.get('nom', ''),
                    medicament.get('prix', ''),
                    medicament.get('stock', ''),
                    medicament.get('date_expiration', ''),
                    medicament.get('numero_lot', '')
                ))
        else:
            self.charger_stock_dans_liste() # Reset

    def selectionner_medicament_dans_liste(self, event):
        selection = self.treeview_stock.selection()
        if selection:
            item = selection[0]
            values = self.treeview_stock.item(item, 'values')
            # Reconstruit dict (ou fetch from list lookup if ID was hidden)
            # Ici on utilise values, attention si values tronqués ? Non ça va.
            medicament = {
                "nom": values[0],
                "prix": values[1],
                "stock": values[2],
                "date_expiration": values[3],
                "numero_lot": values[4],
                # Idéalement conserver ID en hidden column
            }
            # Need ID for sale logic in DBManager if we want to be strict, but search by name works for now in our adapted logic
            # However, logic 'enregistrer_vente' needs ID to link lines_vente.
            # On va faire un lookup dans le manager.
            
            self.medicament_selectionne = medicament
            self.nom_var.set(medicament['nom'])
            self.prix_var.set(medicament['prix'])
            self.stock_var.set(medicament['stock'])

    def vendre_et_imprimer(self):
        if not self.medicament_selectionne:
            messagebox.showwarning("Attention", "Sélectionnez un médicament")
            return
            
        try:
            qty = int(self.entry_quantite_vente.get())
            if qty <= 0: raise ValueError
            
            # Auth check on backend ? No need here, User is logged in.
            
            nom = self.medicament_selectionne['nom']
            prix = float(self.medicament_selectionne['prix'])
            
            if self.gestionnaire_stock.vendre_medicament(nom, qty):
                self.gestionnaire_ventes.enregistrer_vente(
                    self.medicament_selectionne, 
                    qty, 
                    prix,
                    vendeur_id=self.current_user['id']
                )
                messagebox.showinfo("Succès", "Vente enregistrée")
                self.charger_stock_dans_liste()
                self.stock_var.set(str(int(self.stock_var.get()) - qty))
                self.entry_quantite_vente.delete(0, tk.END)
            else:
                messagebox.showerror("Erreur", "Stock insuffisant")
                
        except ValueError:
            messagebox.showerror("Erreur", "Quantité invalide")

    def ajouter_nouveau_medicament(self):
        # ... Logique similaire à avant ...
        try:
            nouv = {
                "nom": self.entry_nouveau_nom.get(),
                "prix": float(self.entry_nouveau_prix.get()),
                "stock": int(self.entry_nouveau_stock.get()),
                "date_expiration": self.entry_nouveau_expiration.get(),
                "numero_lot": self.entry_nouveau_lot.get()
            }
            self.gestionnaire_stock.ajouter_medicament(nouv)
            self.charger_stock_dans_liste()
            messagebox.showinfo("Succès", "Médicament ajouté")
            # Clear entries...
        except ValueError:
             messagebox.showerror("Erreur", "Vérifiez les formats numériques")

    def exporter_rapport(self):
        try:
            ventes = self.gestionnaire_ventes.get_ventes_du_jour()
            if not ventes:
                messagebox.showinfo("Info", "Aucune vente aujourd'hui")
                return
            fn = filedialog.asksaveasfilename(defaultextension=".xlsx")
            if fn:
                exporter_ventes_excel(ventes, fn)
                messagebox.showinfo("Succès", "Export réussi")
        except Exception as e:
            messagebox.showerror("Erreur", f"Export échoué: {e}")

def main():
    login_root = tk.Tk()
    
    def on_login(user):
        login_root.destroy()
        # Launch main app
        main_root = tk.Tk()
        app = FenetrePrincipale(main_root, user)
        main_root.mainloop()

    login_app = FenetreConnexion(login_root, on_login)
    login_root.mainloop()

if __name__ == '__main__':
    main()
