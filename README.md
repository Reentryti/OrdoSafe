  <pre>           ██████╗ ██████╗ ██████╗  ██████╗ ███████╗ █████╗ ███████╗███████╗
          ██╔═══██╗██╔══██╗██╔══██╗██╔═══██╗██╔════╝██╔══██╗██╔════╝██╔════╝
          ██║   ██║██████╔╝██║  ██║██║   ██║███████╗███████║█████╗  █████╗  
          ██║   ██║██╔══██╗██║  ██║██║   ██║╚════██║██╔══██║██╔══╝  ██╔══╝ 
          ╚██████╔╝██║  ██║██████╔╝╚██████╔╝███████║██║  ██║██║     ███████╗
           ╚═════╝ ╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝     ╚══════╝  </pre>


                                                                  
                                                                  

# Plateforme de Prescription Médicale Sécurisé

**OrdoSafe** est une application web sécurisée conçue pour faciliter la création, la validation et la consultation d’ordonnances médicales numériques. Ce système centralise les interactions entre les professionnels de santé (médecins, pharmaciens) et les patients tout en garantissant un haut niveau de sécurité, de traçabilité et de confidentialité.

Ce projet s’inscrit dans une démarche **DevSecOps**, intégrant la sécurité dès les premières étapes du développement jusqu’au déploiement.

---

## Objectifs

- Numériser et sécuriser le processus de prescription médicale.
- Protéger les données sensibles des patients via des mécanismes de chiffrement, d’intégrité et de contrôle d'accès.
- Fournir une traçabilité complète de chaque action liée aux prescriptions.
- Faciliter une possible intégration avec d’autres services de santé via une API sécurisée.
- Mettre en œuvre des pratiques DevSecOps modernes pour garantir la sécurité continue du système.

---

## Principaux Piliers de Sécurité

- **Authentification forte** avec support de la double authentification.
- **Autorisation basée sur les rôles** (médecin, pharmacien, patient, administrateur).
- **Audit et traçabilité** des actions sensibles (consultations, modifications, validations).
- **Confidentialité** des données médicales via le chiffrement.
- **Intégrité** assurée des prescriptions médicales avec vérification cryptographique.

---

## Technologies prévues

- **Backend** : Python (Django)
- **Frontend** : Vue.js
- **Base de données** : MySQL
- **Tests unitaires et d'intégration** : GitHub Actions
- **Conteneurisation** : Docker
- **Sécurité DevOps** : HTTPS, AES, OTP, JWT

---

---

##  Instructions d’installation et d’exécution

## 1. Cloner le projet

```bash
git clone https://github.com/Reentryti/OrdoSafe
cd OrdoSafe
```

## 2. Créer un environnement virtuel (optionnel)

```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

> ou simplement :

```bash
pip install django djangorestframework
```

## 4. Appliquer les migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

## 5. Créer un superutilisateur

```bash
python manage.py createsuperuser
```

## 6. Lancer le serveur

```bash
python manage.py runserver
```

## 7. Tester l’API

- http://127.0.0.1:8000/admin/
- http://127.0.0.1:8000/api/ordonnances/
- http://127.0.0.1:8000/api/medicaments/
- http://127.0.0.1:8000/api/patient/signup/
- http://127.0.0.1:8000/api/patient/login/

---

##  Exemple JSON à tester (POST /api/ordonnances/)

```json
{
  "patient": 2,
  "medecin": 3,
  "medicaments": [
    {
      "nom": "Doliprane",
      "dosage": "500mg",
      "frequence": "3 fois par jour"
    },
    {
      "nom": "Amoxicilline",
      "dosage": "250mg",
      "frequence": "2 fois par jour"
    }
  ],
  "statut": "validee"
}
```

