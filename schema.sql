-- Supprimer les tables si elles existent déjà pour repartir sur une base propre
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS progress;

-- Création de la table pour stocker les informations des utilisateurs
CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT, -- Identifiant unique pour chaque utilisateur
  full_name TEXT NOT NULL,              -- Nom complet de l'utilisateur
  email TEXT UNIQUE NOT NULL,           -- Email de l'utilisateur, doit être unique
  nickname TEXT UNIQUE NOT NULL,        -- Pseudo de l'utilisateur, doit être unique
  password TEXT NOT NULL,               -- Mot de passe haché de l'utilisateur
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP -- Date de création du compte
);

-- Création de la table pour suivre la progression des utilisateurs dans les quiz
CREATE TABLE progress (
  id INTEGER PRIMARY KEY AUTOINCREMENT, -- Identifiant unique pour chaque enregistrement de progression
  user_id INTEGER NOT NULL,             -- Lie cette progression à un utilisateur
  subject TEXT NOT NULL,                -- Le nom de la matière (ex: "python", "big_data")
  score INTEGER NOT NULL,               -- Le meilleur score obtenu par l'utilisateur pour cette matière
  last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, -- Date de la dernière mise à jour du score
  FOREIGN KEY (user_id) REFERENCES user (id) -- Crée un lien vers la table 'user'
);
