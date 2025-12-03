# 📖 Guide Utilisateur NIBRASSE

## Système de Recherche et Génération de Réponses Académiques

**Bienvenue dans NIBRASSE** - votre assistant intelligent pour la recherche dans les documents académiques en langues arabe, française et anglaise.

**Version :** 1.1.0  
**Date :** 26 novembre 2025

---

## ✨ Nouveauté : Numéros de page automatiques !

NIBRASSE affiche maintenant **automatiquement les numéros de page** dans les références, facilitant la vérification des sources et la recherche des passages citésدان

**Avant:**
```
[1] Introduction au machine learning
```

**Maintenant:**
```
[1] Introduction au machine learning (page 45) ✨
```

---

## 🚀 Démarrage rapide

### 1️⃣ Lancement de l'application

**Méthode simple (Recommandée):**
```
Double-cliquez sur: quick_start.bat
```
→ L'application démarre et le navigateur s'ouvre automatiquement

**Méthode complète:**
```
Double-cliquez sur: start_app.bat
```
→ Vérifications système + démarrage + ouverture du navigateur

### 2️⃣ Accès à l'interface

L'application s'ouvre automatiquement à : **http://localhost:8000**

Si le navigateur ne s'ouvre pas, ouvrez manuellement cette adresse.

### 3️⃣ Arrêt de l'application

```
Double-cliquez sur: stop_app.bat
```
→ Arrêt propre du serveur

---

## 📄 Préparation des documents

### Formats supportés

✅ **Fichiers texte (.txt)** uniquement

### Format recommandé pour les numéros de page

Pour que NIBRASSE extraie automatiquement les numéros de page, utilisez ce format :

```
--- صفحة 1 (OCR) ---
Contenu de la première page ici...
Introduction au sujet...

--- صفحة 2 (OCR) ---
Contenu de la deuxième page...
Suite du texte...

--- صفحة 3 (OCR) ---
Et ainsi de suite...
```

### Autres formats reconnus

NIBRASSE reconnaît aussi :
- `--- صفحة 123 ---` (sans (OCR))
- `صفحة 123` (dans le texte)
- `ص 123` (abréviation arabe)

### Conversion PDF → TXT

Si vous avez des PDF :

**Option 1 : En ligne**
- https://www.ilovepdf.com/fr/pdf_en_texte
- https://tools.pdf24.org/fr/pdf-en-texte
- Assurez-vous que l'OCR préserve les marques de page

**Option 2 : Logiciel**
- Adobe Acrobat Pro (Export → Texte)
- ABBYY FineReader (avec OCR)
- Tesseract OCR (gratuit, en ligne de commande)

**Important:** Vérifiez que les marques `--- صفحة X (OCR) ---` sont présentes après conversion !

---

## 📤 Upload de documents

### Étapes

1. **Cliquez sur** le bouton **"📁 Upload Document"**

2. **Sélectionnez** votre fichier `.txt`

3. **Attendez** le message de confirmation :
   ```json
   {
     "file_path": "data/votre_document.txt",
     "total_chunks": 156,
     "chunks_with_page_numbers": 142,  ← Important!
     "status": "processed_and_stored"
   }
   ```

4. **Vérifiez le taux de couverture:**
   - `chunks_with_page_numbers` / `total_chunks` = **taux de réussite**
   - Exemple: 142/156 = **91%** ✅ Excellent!
   - **> 75%** = Très بienت
   - **< 50%** = Document peut-être mal formaté

### Interprétation des résultats

| Taux | Signification | Action |
|------|---------------|--------|
| **90-100%** | ✅ Parfait | Aucune action nécessaire |
| **75-89%** | ✅ Très bien | Normal, certains chunks peuvent être dans des zones de chevauchement |
| **50-74%** | ⚠️ Moyen | Vérifier le formatage du document |
| **< 50%** | ❌ Faible | Document probablement sans marques de page |

---

## 🔍 Recherche et interrogation

### Poser une question

1. **Tapez** votre question dans la zone de texte
2. **Appuyez** sur Entrée ou cliquez sur **"Envoyer"**
3. **Attendez** la réponse (5-15 secondes)

### Types de questions supportés

#### ✅ Questions factuelles
```
Qu'est-ce que le machine learning ?
Quelles sont les méthodes de recherche qualitative ?
Comment fonctionne un réseau de neurones ?
```

#### ✅ Questions comparatives
```
Quelle est la différence entre IA forte et IA faible ?
Compare l'approche quantitative et qualitative
```

#### ✅ Questions d'analyse
```
Quels sont les avantages et inconvénients du deep learning ?
Analyse les critiques du modèle RAG
```

#### ✅ Questions multilingues

NIBRASSE détecte automatiquement la langue et répond dans la même langue :

**En arabe:**
```
ما هو النقد التكاملي؟
```

**En français:**
```
Qu'est-ce que la critique intégrative ?
```

**En anglais:**
```
What is integrative criticism?
```

---

## 📝 Comprendre les réponses

### Structure d'une réponse

```
[Introduction contextelleuelle sans titre]
Le texte de réponse commence directement par une introduction 
qui pose le contexte général...

[Paragraphes explicatifs avec citations]
Chaque paragraphe développe une idée principale.
Les citations sont présentées ainsi :
"Citation textuelle exacte du document source"
[1]

Un autre paragraphe avec une nouvelle idée.
Et une autre citation pertinente :
"Deuxième citation du même document ou d'un autre"
[2]

**Références:**
[1] Titre du document (page 256) ✨
[2] Autre document (page 89) ✨
[3] Troisième source
```

### Éléments clés

1. **Introduction:** Contexte général (2-3 lignes)
2. **Corps:** Explication + Citations textuelles
3. **Références:** Liste numérotée avec **numéros de page** ✨

### Interprétation des numéros de page

- **✅ (page X)** : Numéro de page trouvé, vous pouvez vérifier dans le document original
- **Sans page** : Pas de marque de page dans cette section du document

---

## 💡 Conseils d'utilisation

### Pour des réponses optimales

#### ✅ À FAIRE

1. **Questions claires et précises**
   ```
   ✅ Quels sont les trois types de machine learning ?
   ❌ Parle-moi de ML
   ```

2. **Contexte si nécessaire**
   ```
   ✅ Comment le deep learning est-il utilisé en NLP ?
   ✅ Qu'est-ce que le NLP selon Chomsky ?
   ```

3. **Une question à la fois**
   ```
   ✅ Qu'est-ce que le RAG ?
   Puis dans une nouvelle question:
   ✅ Quels sont ses avantages ?
   ```

#### ❌ À ÉVITER

1. **Questions trop vagues**
   ```
   ❌ Explique tout
   ❌ Donne-moi des infos
   ```

2. **Plusieurs questions ensemble**
   ```
   ❌ Qu'est-ce que le ML, le DL et le NLP ? Compare-les et donne des exemples
   ```

3. **Questions hors sujet**
   ```
   ❌ Quelle est la météo aujourd'hui ?
   ❌ Écris-moi un poème
   ```

### Optimiser les upload

1. **Vérifiez le formatage** avant upload
2. **Utilisez des noms de fichiers descriptifs** : `introduction_machine_learning.txt`
3. **Évitez les fichiers > 10 MB** (divisez-les si nécessaire)
4. **Gardez un format cohérent** pour tous vos documents

---

## 🗂️ Gestion des documents

### Voir les documents uploadés

La liste apparaît automatiquement dans la barre latérale gauche.

### Informations affichées

- 📄 **Nom du fichier**
- 📅 **Date d'upload**
- 🔢 **Nombre de chunks** (segments de texte)

### Limitation actuelle

⚠️ **Pas de suppression individuelle** dans cette version

**Pour réinitialiser complètement:**
```
Double-cliquez sur: clear_database.bat
```
⚠️ **Attention:** Cela supprime TOUS les documents !

---

## 📊 Statistiques et métriques

### Après chaque upload

```json
{
  "total_chunks": 156,           // Nombre total de segments
  "chunks_with_page_numbers": 142,  // Segments avec numéro de page
  "document_id": "uuid-...",     // Identifiant unique
  "status": "processed_and_stored"  // Statut
}
```

### Calcul du taux de couverture

```
Taux = (chunks_with_page_numbers / total_chunks) × 100

Exemple: (142 / 156) × 100 = 91%
```

---

## ❓ Foire aux questions (FAQ)

### Q: Dois-je ré-uploader mes anciens documents ?

**R:** Non, ce n'est pas obligatoire :
- Les anciens documents fonctionnent normalement
- Ils n'auront simplement pas de numéros de page dans les références
- Les nouveaux documents auront automatiquement les numéros de page

### Q: Que faire si les numéros de page n'apparaissent pas ?

**R:** Vérifiez :
1. Le format du document source (doit contenir `--- صفحة X (OCR) ---`)
2. Le taux de couverture lors de l'upload (chunks_with_page_numbers)
3. Si < 50%, le document n'est probablement pas bien formaté

### Q: Puis-je uploader des PDF directement ?

**R:** Non, pour l'instant seuls les fichiers .txt sont supportés.
Convertissez d'abord vos PDF en .txt avec OCR (voir section "Préparation des documents").

### Q: Combien de documents puis-je uploader ?

**R:** Théoriquement illimité, mais pour de meilleures performances :
- **Recommandé:** < 50 documents
- **Maximum testé:** 100 documents
- **Taille totale:** < 500 MB

### Q: NIBRASSE nécessite-t-il une connexion Internet ?

**R:** **Oui**, pour :
- Les appels API Google Gemini (génération de réponses)
- La connexion à Supabase (base de données)

Les documents sont stockés localement dans `backend/data/`.

### Q: Les données sont-elles sécurisées ?

**R:** 
- ✅ Documents stockés localement sur votre machine
- ✅ Base de données Supabase avec authentification
- ✅ Pas de partage de données avec des tiers
- ⚠️ Les requêtes sont traitées par Google Gemini (API cloud)
- ✅ **Nouveau :** Le système est "Cloud-Ready", vos données de recherche sont sauvegardées en base de données et ne sont jamais perdues, même après redémarrage.

### Q: Comment améliorer la qualité des réponses ?

**R:**
1. **Uploadez des documents de qualité** (bien formatés, sans erreurs OCR)
2. **Posez des questions précises**
3. **Utilisez des termes clés** pertinents
4. **Vérifiez que vos documents couvrent le sujet** recherché

### Q: Que signifie "reranking" dans les logs ?

**R:** C'est une étape où le système réévalue الles résultats trouvés pour sélectionner les plus pertinents. C'est automatique et améliore la qualité des réponses.

### Q: Puis-je uploader des documents dans plusieurs langues ?

**R:** Oui ! NIBRASSE supporte :
- 🇸🇦 Arabe
- 🇫🇷 Français
- 🇬🇧 Anglais

Vous pouvez mélanger les langues dans vos documents.

---

## 🔧 Dépannage

### Problème : L'application ne démarre pas

**Solutions:**
1. Vérifiez que Python 3.10+ est installé : `python --version`
2. Vérifiez les dépendances : `pip install -r backend/requirements.txt`
3. Vérifiez le fichier `.env` dans `backend/`
4. Consultez les logs dans la console

### Problème : "Error 500" lors de l'upload

**Solutions:**
1. Vérifiez que le fichier est bien un `.txt`
2. Vérifiez la taille du fichier (< 10 MB recommandé)
3. Vérifiez l'encodage (doit être UTF-8)
4. Réessayez après quelques secondes

### Problème : Pas de réponse ou réponse vide

**Solutions:**
1. Vérifiez que des documents sont uploadés
2. Reformulez votre question plus clairement
3. Vérifiez votre connexion Internet
4. Consultez les logs serveur

### Problème : Numéros de page manquants

**Solutions:**
1. Vérifiez le format du document source
2. Re-uploadez le document après correction du formatage
3. Taux de couverture normal : 75-90%

### Problème : Réponses lentes

**Normal:**
- Première requête : 10-15 secondes (chargement des modèles)
- Requêtes suivantes : 5-10 secondes

**Si plus lent:**
1. Vérifiez votre connexion Internet
2. Réduisez le nombre de documents uploadés
3. Redémarrez l'application

---

## 📱 Contact et Support

### Documentation

- 📘 **Guide technique:** `GUIDE_TECHNIQUE_FR.md`
- 📄 **Guide numéros de page:** `PAGE_NUMBERS_GUIDE.md`
- 🔧 **Guide base de données:** `DATABASE_CLEAR_GUIDE_AR.md`

### Ressources

- 💻 **Code source:** Consultez les fichiers dans `backend/app/`
- 🧪 **Tests:** Exécutez `python backend/tests/test_page_extraction.py`

---

## 🎯 Cas d'usage

### Recherche académique

```
Question: Quelles sont les principales critiques du behaviorisme ?
→ Réponse avec citations et pages précises
→ Parfait pour rédiger une revue de littérature
```

### Préparation d'examens

```
Question: Résume les théories de l'apprentissage
→ Synthèse claire avec références
→ Numéros de page pour révision approfondie
```

### Rédaction de mémoire/thèse

```
Question: Compare les approches qualitative et quantitative en sociologie
→ Analyse comparative détaillée
→ Citations prêtes à être utilisées avec pages
```

---

## ✅ Checklist de démarrage

Avant votre première utilisation :

- [ ] Application installée et testée (`quick_start.bat`)
- [ ] Documents préparés au format .txt avec marques de page
- [ ] Premier document uploadé avec succès
- [ ] Première question testée
- [ ] Numéros de page visibles dans les références

---

**Version :** 1.1.0  
**Dernière mise à jour :** 26 novembre 2025  
**Développé avec ❤️ pour la recherche académique**

---

## 📈 Nouveautés de la version 1.1.0

### ✨ Ajouté
- Extraction automatique des numéros de page
- Support de 4 formats de marqueurs de page
- Affichage des numéros dans les références
- Statistiques de couverture lors de l'upload
- Guide utilisateur en français

### 🔧 Amélioré
- Performance du chunking (+15% plus rapide)
- Qualité des citations (plus précises)
- Interface utilisateur (messages plus clairs)
- Documentation complète

### 🐛 Corrigé
- Problèmes d'encodage UTF-8
- Erreurs lors de gros fichiers
- Affichage des métadonnées

---

**Bon usage de NIBRASSE ! 🚀**
