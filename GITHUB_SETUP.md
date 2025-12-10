# 📤 Guide de Publication sur GitHub

## 🎯 Étapes pour Publier le Projet

### 1️⃣ Initialiser le Dépôt Git Local

Ouvrez un terminal dans le dossier `RO/` et exécutez :

```bash
# Initialiser le dépôt git
git init

# Ajouter tous les fichiers
git add .

# Créer le premier commit
git commit -m "Initial commit: 5 projets de Recherche Opérationnelle"
```

---

### 2️⃣ Créer un Dépôt sur GitHub

1. Allez sur [github.com](https://github.com)
2. Cliquez sur **"New repository"** (bouton vert)
3. Remplissez les informations :
   - **Repository name** : `RO-Projects-GL3` (ou un autre nom)
   - **Description** : `5 projets de Recherche Opérationnelle - GL3 INSAT`
   - **Visibility** : Public ou Private
   - **⚠️ NE PAS** cocher "Initialize with README" (on a déjà un README)
4. Cliquez sur **"Create repository"**

---

### 3️⃣ Lier le Dépôt Local à GitHub

GitHub vous donnera des commandes. Utilisez celles-ci :

```bash
# Ajouter le remote (remplacez USERNAME et REPO-NAME)
git remote add origin https://github.com/USERNAME/REPO-NAME.git

# Renommer la branche en main (si nécessaire)
git branch -M main

# Pousser le code
git push -u origin main
```

**Exemple concret :**
```bash
git remote add origin https://github.com/elyesmlawah/RO-Projects-GL3.git
git branch -M main
git push -u origin main
```

---

### 4️⃣ Vérifier la Publication

1. Allez sur votre dépôt GitHub
2. Vérifiez que tous les fichiers sont présents
3. Le README.md devrait s'afficher automatiquement

---

## 🔐 Authentification GitHub

### Option 1 : Token Personnel (Recommandé)

1. Allez dans **Settings** > **Developer settings** > **Personal access tokens** > **Tokens (classic)**
2. Cliquez sur **"Generate new token (classic)"**
3. Donnez un nom : `RO-Projects-Upload`
4. Cochez : `repo` (Full control of private repositories)
5. Cliquez sur **"Generate token"**
6. **⚠️ COPIEZ LE TOKEN** (vous ne le reverrez plus !)

Lors du `git push`, utilisez :
- **Username** : votre username GitHub
- **Password** : le token (pas votre mot de passe)

### Option 2 : SSH (Plus Avancé)

Suivez le guide GitHub : [docs.github.com/en/authentication/connecting-to-github-with-ssh](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)

---

## 📝 Commandes Git Utiles

### Vérifier le Statut
```bash
git status
```

### Ajouter des Modifications
```bash
# Ajouter tous les fichiers modifiés
git add .

# Ajouter un fichier spécifique
git add fichier.py
```

### Créer un Commit
```bash
git commit -m "Description des modifications"
```

### Pousser les Modifications
```bash
git push
```

### Voir l'Historique
```bash
git log --oneline
```

---

## 🌿 Créer des Branches (Optionnel)

```bash
# Créer une nouvelle branche
git checkout -b feature/nouvelle-fonctionnalite

# Pousser la branche
git push -u origin feature/nouvelle-fonctionnalite

# Revenir à main
git checkout main

# Fusionner une branche
git merge feature/nouvelle-fonctionnalite
```

---

## 📋 Checklist Avant de Pousser

- [ ] `.gitignore` est présent et configuré
- [ ] `README.md` est complet et à jour
- [ ] `requirements.txt` contient toutes les dépendances
- [ ] Pas de fichiers sensibles (mots de passe, clés API)
- [ ] Pas de fichiers volumineux inutiles
- [ ] Le code fonctionne localement
- [ ] La documentation est claire

---

## 🎨 Personnaliser le README

N'oubliez pas de mettre à jour dans `README.md` :

1. **Ligne 8** : Remplacez `VOTRE-USERNAME` par votre username GitHub
2. **Section Équipe** : Vérifiez les noms et projets
3. **Badges** : Personnalisez si nécessaire

---

## 🚀 Après la Publication

### Ajouter des Topics

Sur GitHub, dans votre dépôt :
1. Cliquez sur ⚙️ à côté de "About"
2. Ajoutez des topics : `python`, `optimization`, `gurobi`, `pyqt5`, `operations-research`

### Créer une Release

```bash
# Créer un tag
git tag -a v1.0.0 -m "Version 1.0.0 - 5 projets complets"

# Pousser le tag
git push origin v1.0.0
```

Puis sur GitHub : **Releases** > **Create a new release**

---

## 🐛 Problèmes Courants

### Erreur : "remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/USERNAME/REPO-NAME.git
```

### Erreur : "failed to push some refs"
```bash
# Récupérer les changements distants
git pull origin main --rebase

# Puis pousser
git push origin main
```

### Fichiers Trop Volumineux
```bash
# Supprimer du cache
git rm --cached fichier-volumineux

# Ajouter au .gitignore
echo "fichier-volumineux" >> .gitignore

# Commit et push
git commit -m "Remove large file"
git push
```

---

## 📚 Ressources

- [Git Documentation](https://git-scm.com/doc)
- [GitHub Guides](https://guides.github.com/)
- [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)

---

**Bon courage pour la publication ! 🚀**
