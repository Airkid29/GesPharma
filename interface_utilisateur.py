import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
from gestion_stock import GestionnaireStock
from gestion_ventes import GestionnaireVentes
from tkinter import ttk, messagebox, filedialog, font
from rapports import exporter_ventes_excel

class FenetrePrincipale:
    def __init__(self, master):
        self.master = master
        master.title("Gestion de Pharmacie")

        self.gestionnaire_stock = GestionnaireStock()
        self.gestionnaire_ventes = GestionnaireVentes()
        self.medicament_selectionne = None

        # --- Zone de recherche ---
        self.label_recherche = ttk.Label(master, text="Nom du médicament :")
        self.label_recherche.grid(row=0, column=0, padx=5, pady=3, sticky="w")

        self.entry_recherche = ttk.Entry(master)
        self.entry_recherche.grid(row=0, column=1, padx=5, pady=3, sticky="ew")


        self.bouton_rechercher = ttk.Button(master, text="Rechercher", command=self.rechercher_medicament)
        self.bouton_rechercher.grid(row=0, column=2, padx=5, pady=2, sticky="ew")

        # --- Zone d'affichage du stock complet ---
        self.label_stock_complet = ttk.LabelFrame(master, text="Stock Complet")
        self.label_stock_complet.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")

        self.treeview_stock = ttk.Treeview(self.label_stock_complet, columns=("Nom", "Prix", "Stock", "Expiration", "Lot"))
        self.treeview_stock.heading("#1", text="Nom")
        self.treeview_stock.heading("#2", text="Prix")
        self.treeview_stock.heading("#3", text="Stock")
        self.treeview_stock.heading("#4", text="Expiration")
        self.treeview_stock.heading("#5", text="Lot")
        self.treeview_stock.column("#1", stretch=tk.YES)
        self.treeview_stock.column("#2", stretch=tk.NO, width=80)
        self.treeview_stock.column("#3", stretch=tk.NO, width=60)
        self.treeview_stock.column("#4", stretch=tk.NO, width=100)
        self.treeview_stock.column("#5", stretch=tk.NO, width=100)
        self.treeview_stock.grid(row=0, column=0, sticky="nsew")
        self.label_stock_complet.grid_rowconfigure(0, weight=1)
        self.label_stock_complet.grid_columnconfigure(0, weight=1)

        self.charger_stock_dans_liste()

        # --- Zone d'informations du médicament sélectionné ---
        self.label_info = ttk.LabelFrame(master, text="Informations du médicament sélectionné")
        self.label_info.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")

        self.label_nom_info = ttk.Label(self.label_info, text="Nom :")
        self.label_nom_info.grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.nom_var = tk.StringVar()
        self.label_nom_valeur = ttk.Label(self.label_info, textvariable=self.nom_var)
        self.label_nom_valeur.grid(row=0, column=1, padx=5, pady=2, sticky="w")

        self.label_prix_info = ttk.Label(self.label_info, text="Prix :")
        self.label_prix_info.grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.prix_var = tk.StringVar()
        self.label_prix_valeur = ttk.Label(self.label_info, textvariable=self.prix_var)
        self.label_prix_valeur.grid(row=1, column=1, padx=5, pady=2, sticky="w")

        self.label_stock_info = ttk.Label(self.label_info, text="Stock :")
        self.label_stock_info.grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.stock_var = tk.StringVar()
        self.label_stock_valeur = ttk.Label(self.label_info, textvariable=self.stock_var)
        self.label_stock_valeur.grid(row=2, column=1, padx=5, pady=2, sticky="w")

        # --- Zone de vente (modifiée) ---
        self.label_vente = ttk.LabelFrame(master, text="Vente")
        self.label_vente.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")

        self.label_quantite_vente = ttk.Label(self.label_vente, text="Quantité à vendre :")
        self.label_quantite_vente.grid(row=0, column=0, padx=5, pady=2, sticky="w")

        self.entry_quantite_vente = ttk.Entry(self.label_vente)
        self.entry_quantite_vente.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        self.bouton_vendre = ttk.Button(self.label_vente, text="Vendre et Imprimer Ticket", command=self.vendre_et_imprimer)
        self.bouton_vendre.grid(row=0, column=2, padx=5, pady=2, sticky="ew")

        self.bouton_exporter = ttk.Button(self.label_vente, text="Exporter", command=self.exporter_rapport)
        self.bouton_exporter.grid(row=0, column=3, padx=5, pady=2, sticky="ew")

        # --- Zone d'ajout de médicament ---
        self.label_ajout = ttk.LabelFrame(master, text="Ajouter un médicament")
        self.label_ajout.grid(row=4, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")

        self.label_nouveau_nom = ttk.Label(self.label_ajout, text="Nom :")
        self.label_nouveau_nom.grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.entry_nouveau_nom = ttk.Entry(self.label_ajout)
        self.entry_nouveau_nom.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        self.label_nouveau_prix = ttk.Label(self.label_ajout, text="Prix :")
        self.label_nouveau_prix.grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.entry_nouveau_prix = ttk.Entry(self.label_ajout)
        self.entry_nouveau_prix.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        self.label_nouveau_stock = ttk.Label(self.label_ajout, text="Stock :")
        self.label_nouveau_stock.grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.entry_nouveau_stock = ttk.Entry(self.label_ajout)
        self.entry_nouveau_stock.grid(row=2, column=1, padx=5, pady=2, sticky="ew")

        self.label_nouveau_expiration = ttk.Label(self.label_ajout, text="Expiration (AAAA-MM-JJ) :")
        self.label_nouveau_expiration.grid(row=3, column=0, padx=5, pady=2, sticky="w")
        self.entry_nouveau_expiration = ttk.Entry(self.label_ajout)
        self.entry_nouveau_expiration.grid(row=3, column=1, padx=5, pady=2, sticky="ew")

        self.label_nouveau_lot = ttk.Label(self.label_ajout, text="Numéro de lot :")
        self.label_nouveau_lot.grid(row=4, column=0, padx=5, pady=2, sticky="w")
        self.entry_nouveau_lot = ttk.Entry(self.label_ajout)
        self.entry_nouveau_lot.grid(row=4, column=1, padx=5, pady=2, sticky="ew")

        self.bouton_ajouter = ttk.Button(self.label_ajout, text="Ajouter", command=self.ajouter_nouveau_medicament)
        self.bouton_ajouter.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="ew")


        
        # --- Bouton d'exportation ---
        self.bouton_exporter = ttk.Button(master, text="Exporter les ventes du jour", command=self.exporter_rapport)

        # Configuration de la grille pour que la fenêtre soit redimensionnable
        for i in range(4):
            master.grid_columnconfigure(i, weight=1)
        for i in range(5):
            master.grid_rowconfigure(i, weight=1)

        self.medicament_selectionne = None # Pour stocker le médicament actuellement sélectionné
        self.treeview_stock.bind("<Double-1>", self.selectionner_medicament_dans_liste)

    def charger_stock_dans_liste(self):
        """Charge tous les médicaments dans le Treeview."""
        for item in self.treeview_stock.get_children():
            self.treeview_stock.delete(item)
        for medicament in self.gestionnaire_stock.medicaments:
            self.treeview_stock.insert("", tk.END, values=(
                medicament.get('nom', ''),
                medicament.get('prix', ''),
                medicament.get('stock', ''),
                medicament.get('date_expiration', ''),
                medicament.get('numero_lot', '')
            ))

    def rechercher_medicament(self):
        nom_recherche = self.entry_recherche.get()
        if nom_recherche:
            medicament = self.gestionnaire_stock.get_medicament(nom_recherche)
            if medicament:
                self.medicament_selectionne = medicament
                self.afficher_informations_medicament(medicament)
            else:
                self.afficher_informations_medicament(None)
                messagebox.showinfo("Recherche", f"Le médicament '{nom_recherche}' n'a pas été trouvé.")
        else:
            self.afficher_informations_medicament(None)

    def afficher_informations_medicament(self, medicament):
        if medicament:
            self.nom_var.set(medicament.get('nom', ''))
            self.prix_var.set(medicament.get('prix', ''))
            self.stock_var.set(medicament.get('stock', ''))
        else:
            self.nom_var.set("")
            self.prix_var.set("")
            self.stock_var.set("")
            self.medicament_selectionne = None

    def vendre_et_imprimer(self):
        if self.medicament_selectionne:
            try:
                quantite_a_vendre = int(self.entry_quantite_vente.get())
                nom_medicament = self.medicament_selectionne['nom']
                prix_unitaire = float(self.medicament_selectionne.get('prix', 0)) # Récupérer le prix

                if self.gestionnaire_stock.verifier_disponibilite(nom_medicament, quantite_a_vendre):
                    vente = self.gestionnaire_ventes.enregistrer_vente(
                        self.medicament_selectionne,
                        quantite_a_vendre,
                        prix_unitaire
                    )
                    if self.gestionnaire_stock.vendre_medicament(nom_medicament, quantite_a_vendre):
                        ticket_text = self.gestionnaire_ventes.generer_ticket(vente)
                        self.afficher_ticket(ticket_text) # Nouvelle méthode pour afficher le ticket
                        self.charger_stock_dans_liste()
                        self.rechercher_medicament()
                        self.entry_quantite_vente.delete(0, tk.END)
                    else:
                        messagebox.showerror("Erreur de vente", "Erreur lors de la mise à jour du stock.")
                else:
                    messagebox.showerror("Stock insuffisant", f"Stock insuffisant pour {nom_medicament}.")
            except ValueError:
                messagebox.showerror("Erreur de quantité", "Veuillez entrer une quantité valide.")
        else:
            messagebox.showerror("Aucun médicament sélectionné", "Veuillez d'abord sélectionner un médicament.")

    def afficher_ticket(self, ticket_text):
        """Affiche le ticket de vente dans une nouvelle fenêtre."""
        fenetre_ticket = tk.Toplevel(self.master)
        fenetre_ticket.title("Ticket de Vente")
        texte_ticket = tk.Text(fenetre_ticket, height=10, width=30)
        texte_ticket.insert(tk.END, ticket_text)
        texte_ticket.config(state=tk.DISABLED) # Empêcher la modification
        texte_ticket.pack(padx=10, pady=10)
        bouton_imprimer = ttk.Button(fenetre_ticket, text="Imprimer", command=self.imprimer_ticket) # Fonctionnalité d'impression à ajouter
        bouton_imprimer.pack(pady=5)

    
    def imprimer_ticket(self):
        """Fonctionnalité d'impression du ticket (à implémenter)."""
        messagebox.showinfo("Impression", "Fonctionnalité d'impression en cours de développement.")


    def ajouter_nouveau_medicament(self):
        nom = self.entry_nouveau_nom.get()
        prix = self.entry_nouveau_prix.get()
        stock = self.entry_nouveau_stock.get()
        expiration = self.entry_nouveau_expiration.get()
        lot = self.entry_nouveau_lot.get()

        if nom and prix and stock and expiration and lot:
            nouveau_medicament = {
                "nom": nom,
                "prix": prix,
                "stock": stock,
                "date_expiration": expiration,
                "numero_lot": lot
            }
            self.gestionnaire_stock.ajouter_medicament(nouveau_medicament)
            self.charger_stock_dans_liste() # Rafraîchir la liste après l'ajout
            # Effacer les champs d'ajout
            self.entry_nouveau_nom.delete(0, tk.END)
            self.entry_nouveau_prix.delete(0, tk.END)
            self.entry_nouveau_stock.delete(0, tk.END)
            self.entry_nouveau_expiration.delete(0, tk.END)
            self.entry_nouveau_lot.delete(0, tk.END)
            messagebox.showinfo("Ajout", f"Le médicament '{nom}' a été ajouté au stock.")
        else:
            messagebox.showerror("Champs manquants", "Veuillez remplir tous les champs pour ajouter un médicament.")

    def selectionner_medicament_dans_liste(self, event):
        item = self.treeview_stock.selection()[0]
        if item:
            values = self.treeview_stock.item(item, 'values')
            medicament = {
                "nom": values[0],
                "prix": values[1],
                "stock": values[2],
                "date_expiration": values[3],
                "numero_lot": values[4]
            }
            self.medicament_selectionne = medicament
            self.afficher_informations_medicament(medicament)

    def exporter_rapport(self):
        """Récupère les ventes du jour et les exporte vers Excel."""
        ventes_du_jour = self.gestionnaire_ventes.get_ventes_du_jour()
        if ventes_du_jour:
            nom_fichier = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Fichier Excel", "*.xlsx"), ("Tous les fichiers", "*.*")],
                title="Enregistrer les ventes sous..."
            )
            if nom_fichier:
                exporter_ventes_excel(ventes_du_jour, nom_fichier)
                messagebox.showinfo("Exportation", f"Les ventes ont été exportées vers '{nom_fichier}'.")
        else:
            messagebox.showinfo("Exportation", "Aucune vente à exporter pour le moment.")

def main():
    root = tk.Tk()
    app = FenetrePrincipale(root)
    root.mainloop()

if __name__ == '__main__':
    main()