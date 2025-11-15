# Smart-Learn-Hub

> Une plateforme d'apprentissage en ligne (SaaS) conçue pour offrir des cours interactifs avec des quiz et un suivi de la progression personnalisé.

---

## 📝 Description

**Smart-Learn-Hub** est une application web développée comme un "Software as a Service" (SaaS). Elle permet aux utilisateurs de s'inscrire, de se connecter et d'accéder à un catalogue de cours. Chaque cours est accompagné de matériel pédagogique au format PDF et d'un quiz interactif pour évaluer les connaissances. La plateforme enregistre les scores des utilisateurs pour leur permettre de suivre leur progression sur leur profil personnel.

L'application est construite comme une **Single Page Application (SPA)**, où le backend (Flask) fournit une API RESTful et le frontend (HTML/CSS/JavaScript) gère l'interface utilisateur de manière dynamique sans recharger la page.

---

## ✨ Fonctionnalités clés

* **Gestion des utilisateurs :** Inscription, connexion et déconnexion sécurisées avec mots de passe hachés.
* **Catalogue de cours :** Affichage dynamique des cours disponibles à partir d'un fichier de configuration central (`quizzes.json`).
* **Quiz interactifs :** Chaque cours dispose d'un quiz pour tester les connaissances de l'utilisateur.
* **Suivi de la progression :** Le score de chaque quiz est enregistré dans la base de données et affiché sur le profil de l'utilisateur.
* **Consultation de documents :** Accès direct aux supports de cours au format PDF.
* **Profil utilisateur :** Une page de profil personnalisée affichant les informations de l'utilisateur et sa progression globale.
* **API RESTful :** Un backend robuste qui gère la logique métier et expose les données de manière sécurisée.

---

## 🛠️ Technologies utilisées

* **Backend :**
    * **Langage :** Python
    * **Framework :** Flask
    * **Base de données :** SQLite
    * **Sécurité :** Werkzeug pour le hachage des mots de passe.
* **Frontend :**
    * **Structure :** HTML5
    * **Style :** Tailwind CSS (via CDN), CSS personnalisé.
    * **Logique :** Vanilla JavaScript (pour la gestion de la SPA, les appels API et l'interactivité).
    * **Icônes :** Font Awesome.

---

## 🚀 Installation

Suivez ces étapes pour obtenir une copie locale du projet et la faire fonctionner.

### Prérequis

* [Python 3](https://www.python.org/)
* [Git](https://git-scm.com/)

### Étapes

1.  **Clonez le dépôt**
    ```bash
    git clone [https://github.com/](https://github.com/)[VOTRE_NOM_UTILISATEUR]/smart-learn-hub.git
    cd smart-learn-hub
    ```

2.  **Créez un environnement virtuel et activez-le**
    ```bash
    # Pour Windows
    python -m venv venv
    .\venv\Scripts\activate

    # Pour macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Installez les dépendances Python**
    Créez un fichier `requirements.txt` avec le contenu suivant :
    ```txt
    Flask
    Werkzeug
    ```
    Puis installez-le :
    ```bash
    pip install -r requirements.txt
    ```

4.  **Créez les fichiers de données nécessaires** à la racine du projet :
    * Un fichier `schema.sql` pour la structure de la base de données :
        ```sql
        DROP TABLE IF EXISTS user;
        DROP TABLE IF EXISTS progress;

        CREATE TABLE user (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          full_name TEXT NOT NULL,
          email TEXT UNIQUE NOT NULL,
          nickname TEXT UNIQUE NOT NULL,
          password TEXT NOT NULL
        );

        CREATE TABLE progress (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id INTEGER NOT NULL,
          subject TEXT NOT NULL,
          score INTEGER NOT NULL,
          FOREIGN KEY (user_id) REFERENCES user (id)
        );
        ```
    * Un fichier `quizzes.json` pour le contenu des cours :
        ```json
        {
          "math": {
            "title": "Mathématiques de Base",
            "description": "Apprenez les fondamentaux de l'algèbre et de l'arithmétique.",
            "emoji": "🧮",
            "professor": "Dr. Alan Turing",
            "pdf_link": "math_cours.pdf",
            "questions": [
              {
                "question": "Que vaut 2 + 2 ?",
                "options": ["3", "4", "5", "6"],
                "answer": "4"
              }
            ]
          }
        }
        ```

5.  **Créez le dossier pour les cours** et placez-y un PDF de test (par exemple `math_cours.pdf`).
    ```bash
    mkdir courses_pdf
    ```

6.  **Initialisez la base de données** (cette commande exécute `schema.sql`) :
    ```bash
    flask --app app init-db
    ```
    *Vous devriez voir le message "Base de données initialisée."*

7.  **Lancez le serveur Flask**
    ```bash
    flask --app app run
    ```

Votre application **Smart-Learn-Hub** est maintenant accessible à l'adresse `http://127.0.  0.1:5000`.

---

## 🤝 Contribution

Les contributions sont les bienvenues. Pour contribuer, veuillez forker le dépôt, créer une branche pour votre fonctionnalité et soumettre une Pull Request.

## 📜 Licence

Ce projet est distribué sous la licence MIT.