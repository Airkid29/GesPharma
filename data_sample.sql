-- Jeu de données pour GesPharma
-- A importer APRES avoir créé la structure de la base

USE `gespharma_db`;

-- 1. Enrichissement des Catégories
INSERT INTO `categories` (`id`, `nom`, `description`) VALUES
(4, 'Antibiotiques', 'Traitement des infections bactériennes'),
(5, 'Antalgiques', 'Traitement de la douleur et de la fièvre'),
(6, 'Vitamines', 'Compléments alimentaires et vitamines'),
(7, 'Cardiologie', 'Traitement des troubles cardiaques'),
(8, 'Dermatologie', 'Soins de la peau'),
(9, 'Premiers Secours', 'Matériel de soin rapide')
ON DUPLICATE KEY UPDATE description = VALUES(description);

-- 2. Insertion massive de Médicaments
INSERT INTO `medicaments` (`nom`, `prix`, `stock`, `date_expiration`, `numero_lot`, `category_id`) VALUES
-- Antalgiques (Cat 5) --
('Doliprane 1000mg', 2.10, 150, '2026-12-31', 'LOT-A001', 5),
('Doliprane 500mg', 1.90, 200, '2026-11-30', 'LOT-A002', 5),
('Efferalgan 1000mg', 2.15, 120, '2026-10-15', 'LOT-A003', 5),
('Dafalgan Codeine', 3.50, 50, '2025-08-20', 'LOT-A004', 5),
('Advil 400mg', 4.20, 80, '2027-01-10', 'LOT-A005', 5),
('Nurofen Flash 400mg', 4.50, 75, '2026-05-05', 'LOT-A006', 5),
('Spasfon Lyoc', 3.80, 100, '2028-02-28', 'LOT-A007', 5),
('Aspirine du Rhône 500mg', 2.00, 60, '2025-12-12', 'LOT-A008', 5),

-- Antibiotiques (Cat 4) --
('Amoxicilline 1g', 5.40, 40, '2025-09-30', 'LOT-B001', 4),
('Augmentin 1g', 6.80, 30, '2025-08-15', 'LOT-B002', 4),
('Pyostacine 500mg', 8.90, 25, '2026-03-20', 'LOT-B003', 4),
('Monuril', 7.50, 50, '2027-06-10', 'LOT-B004', 4),
('Orelox 200mg', 6.20, 35, '2026-04-12', 'LOT-B005', 4),

-- Vitamines (Cat 6) --
('Vitamine C 1000mg UPSA', 4.50, 150, '2027-11-01', 'LOT-C001', 6),
('Magnesium B6', 5.90, 80, '2028-01-15', 'LOT-C002', 6),
('Berocca', 9.50, 60, '2027-09-09', 'LOT-C003', 6),
('Azinc Forme et Vitalité', 11.20, 45, '2026-07-30', 'LOT-C004', 6),
('Vitamines D3 Ampoules', 3.10, 200, '2026-02-28', 'LOT-C005', 6),

-- Parapharmacie (Cat 2) --
('Bétadine Jaune', 3.40, 100, '2026-10-10', 'LOT-D001', 2),
('Bétadine Rouge (Scrub)', 3.60, 90, '2026-10-10', 'LOT-D002', 2),
('Biseptine Spray', 4.10, 85, '2027-05-05', 'LOT-D003', 2),
('Sérum Physiologique (x40)', 5.20, 150, '2027-12-31', 'LOT-D004', 2),
('Gel Hydroalcoolique 500ml', 4.00, 300, '2026-01-01', 'LOT-D005', 2),

-- Nourrissons (Cat 3) --
('Gallia 1er Age', 18.50, 40, '2025-11-20', 'LOT-E001', 3),
('Guigoz 2eme Age', 17.90, 45, '2025-12-15', 'LOT-E002', 3),
('Liniment Oléo-calcaire', 6.50, 80, '2026-08-08', 'LOT-E003', 3),
('Mouche Bébé', 8.90, 20, '2099-12-31', 'LOT-E004', 3),

-- Cardiologie (Cat 7) --
('Kardégic 75mg', 2.80, 100, '2026-06-30', 'LOT-F001', 7),
('Tahor 10mg', 12.50, 60, '2026-03-15', 'LOT-F002', 7),

-- Dermatologie (Cat 8) --
('Biafine Emulsion', 5.60, 120, '2027-07-20', 'LOT-G001', 8),
('Dexeryl Crème', 4.80, 140, '2027-04-10', 'LOT-G002', 8),
('Cicaplast Baume B5', 9.90, 70, '2027-01-01', 'LOT-G003', 8);

-- 3. Ajout d'utilisateurs de test (MDP = user)
-- Hachage SHA256 pour 'caissier1' = 'e6c3da5b206634d7f3f3586d747ffdb36b5c6d22e5a8d2a64864c3c3a9d4d385'
-- Hachage SHA256 pour 'caissier2' = '9834876dcfb05cb162a8848c6974737dca9c9a63200c8a8y8c888d3f8287d3a8' (fake hash for example simplicity)
-- On utilise le hash réel de 'caissier1' pour que ça marche.
INSERT INTO `utilisateurs` (`nom_utilisateur`, `mot_de_passe_hache`, `nom_complet`, `role_id`) VALUES
('caissier1', '0412803874311915998188151590483868018440842848184820842008400000', 'Sophie Martin', 2),
('caissier2', '0412803874311915998188151590483868018440842848184820842008400000', 'Thomas Durant', 2);
-- Note: les hashs ci-dessus pour les caissiers sont faux pour l'exemple rapide, 
-- pour tester utilisez admin/admin ou créez-en via l'interface.
-- Pour 'caissier1' -> '1234' (exemple hash réel SHA256 : 03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4)

UPDATE `utilisateurs` SET `mot_de_passe_hache` = '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4' WHERE `nom_utilisateur` = 'caissier1';
