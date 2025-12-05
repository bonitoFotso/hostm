# HostMail - SaaS Backend

Backend Django REST pour HostMail, un SaaS qui propose deux services principaux :
1. **Service de Contact** : Backend pour formulaires de contact personnalisables
2. **Service de Projets** : Gestion et affichage de portfolios de projets

## 📋 Fonctionnalités

### ✅ Système d'Abonnement
- **Free** : 1 site web, 50 contacts/mois, 5 projets, 100 MB storage
- **Pro** : 3 sites web, 500 contacts/mois, projets illimités, 1 GB storage, analytics
- **Agency** : Sites illimités, 5000 contacts/mois, projets illimités, 10 GB storage, analytics, white label

### 🌐 Gestion Multi-Sites
- Chaque utilisateur peut créer plusieurs sites web (selon son plan)
- API Key unique par site web
- Configuration CORS personnalisée par site

### 📧 Service de Contact
- Formulaires personnalisables (types de champs : text, email, textarea, select, etc.)
- Stockage des messages avec métadonnées (IP, User Agent)
- Statuts : nouveau, lu, répondu, archivé, spam
- Notifications par email
- Rate limiting anti-spam

### 🚀 Service de Projets
- Gestion de projets avec catégories et tags
- Upload d'images (thumbnails, featured images, gallery)
- Champs standards et personnalisables (JSON)
- Technologies utilisées
- Statistiques de vues
- Statuts : brouillon, publié, archivé

### 📊 Analytics
- Tracking des événements (contacts reçus, projets vus, etc.)
- Statistiques journalières agrégées
- Disponible pour les plans Pro et Agency

### 🔗 Webhooks
- Configuration de webhooks par événement
- Retry automatique en cas d'échec
- Logs détaillés des appels webhook
- Signature HMAC pour sécurité

### 💳 Paiements
- Intégration PayPal (Sandbox et Live)
- Génération automatique de factures
- Historique des paiements

## 🛠️ Stack Technique

- **Framework** : Django 5.2.6 + Django REST Framework
- **Base de données** : PostgreSQL (Neon)
- **Authentification** : JWT (djangorestframework_simplejwt)
- **Stockage Media** : MinIO (S3-compatible) - `https://minio.f2mb.xyz`
- **Paiements** : PayPal REST API
- **Email** : Gmail SMTP (`bonitofotso55@gmail.com`)
- **Cache** : Redis (optionnel)
- **Rate Limiting** : django-ratelimit

## 📦 Installation

### 1. Cloner le repository

```bash
git clone <repo-url>
cd hostm
```

### 2. Créer l'environnement virtuel

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configuration de l'environnement

Copier `.env.example` vers `.env` et configurer les variables :

```bash
cp .env.example .env
```

**Variables importantes à configurer :**

```env
# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (Neon PostgreSQL)
DB_NAME=hostmail
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_HOST=your-neon-host.neon.tech
DB_PORT=5432
DB_SSLMODE=require

# Email (Gmail)
EMAIL_HOST_USER=bonitofotso55@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password

# MinIO Storage
USE_MINIO=True
MINIO_ENDPOINT=https://minio.f2mb.xyz
MINIO_ACCESS_KEY=your-access-key
MINIO_SECRET_KEY=your-secret-key
MINIO_BUCKET_NAME=hostmail

# PayPal
PAYPAL_MODE=sandbox
PAYPAL_CLIENT_ID=your-paypal-client-id
PAYPAL_CLIENT_SECRET=your-paypal-secret
```

### 5. Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Créer un superutilisateur

```bash
python manage.py createsuperuser
```

### 7. Lancer le serveur

```bash
python manage.py runserver
```

## 📁 Structure du Projet

```
hostm/
├── auths/              # Authentification (User model personnalisé)
├── subscriptions/      # Gestion des abonnements et plans
├── websites/           # Sites web et API keys
├── contacts/           # Formulaires de contact et messages
├── projects/           # Gestion de projets/portfolio
├── analytics/          # Événements et statistiques
├── webhooks/           # Configuration et logs de webhooks
├── payments/           # Paiements PayPal et factures
├── core/               # Configuration Django
│   ├── settings.py     # Settings principal
│   ├── urls.py         # URLs principales
│   └── wsgi.py
├── manage.py
├── requirements.txt
└── .env.example
```

## 🗄️ Modèles de Données

### Subscriptions
- `Subscription` : Abonnement utilisateur avec limites et fonctionnalités

### Websites
- `Website` : Site web avec API key unique

### Contacts
- `ContactFormField` : Champs personnalisables du formulaire
- `ContactMessage` : Messages de contact reçus

### Projects
- `Category` : Catégories de projets
- `Tag` : Tags pour projets
- `Project` : Projets avec images et métadonnées
- `ProjectImage` : Images additionnelles des projets

### Analytics
- `AnalyticsEvent` : Événements trackés
- `DailyStats` : Statistiques journalières agrégées

### Webhooks
- `Webhook` : Configuration des webhooks
- `WebhookLog` : Logs des appels webhook

### Payments
- `Payment` : Paiements PayPal
- `Invoice` : Factures générées

## 🔐 API Endpoints (À implémenter)

### Authentification
- `POST /api/auth/register/` - Inscription
- `POST /api/auth/login/` - Connexion (JWT)
- `POST /api/auth/refresh/` - Refresh token

### Subscriptions
- `GET /api/subscriptions/me/` - Mon abonnement
- `POST /api/subscriptions/upgrade/` - Upgrade de plan

### Websites
- `GET /api/websites/` - Liste des sites
- `POST /api/websites/` - Créer un site
- `POST /api/websites/{id}/regenerate-key/` - Régénérer l'API key

### Contacts (Protected - nécessite authentification)
- `GET /api/contacts/messages/` - Messages reçus
- `GET /api/contacts/fields/` - Configuration des champs

### Contacts (Public - nécessite API key)
- `POST /api/public/contact/submit/` - Soumettre un message

### Projects (Protected)
- `GET/POST /api/projects/` - CRUD projets
- `GET/POST /api/projects/categories/` - CRUD catégories
- `GET/POST /api/projects/tags/` - CRUD tags

### Projects (Public - avec API key)
- `GET /api/public/projects/` - Liste des projets publiés
- `GET /api/public/projects/{slug}/` - Détail d'un projet

### Analytics
- `GET /api/analytics/stats/` - Statistiques globales
- `GET /api/analytics/events/` - Liste des événements

### Webhooks
- `GET/POST /api/webhooks/` - CRUD webhooks
- `GET /api/webhooks/{id}/logs/` - Logs d'un webhook

### Payments
- `POST /api/payments/create-order/` - Créer une commande PayPal
- `POST /api/payments/capture-order/` - Capturer un paiement
- `GET /api/payments/invoices/` - Liste des factures

## 🔒 Sécurité

- **Authentication** : JWT tokens pour les utilisateurs
- **API Keys** : Clés uniques par site web (format: `hm_xxx`)
- **Rate Limiting** : Protection anti-spam sur les endpoints publics
- **CORS** : Configuration personnalisable par site web
- **HTTPS** : SSL/TLS pour toutes les communications
- **Webhooks** : Signature HMAC pour vérification

## 📝 Configuration Gmail

Pour utiliser Gmail SMTP, vous devez :
1. Activer la validation en 2 étapes sur votre compte Google
2. Générer un "mot de passe d'application" : https://myaccount.google.com/apppasswords
3. Utiliser ce mot de passe dans `EMAIL_HOST_PASSWORD`

## ☁️ Configuration MinIO

Le storage MinIO est configuré sur `https://minio.f2mb.xyz`
- Les fichiers uploadés sont stockés dans le bucket `hostmail`
- Configuration S3-compatible via `django-storages` et `boto3`

## 💻 Développement

### Lancer les tests
```bash
python manage.py test
```

### Créer une migration
```bash
python manage.py makemigrations
```

### Shell Django
```bash
python manage.py shell
```

### Collecter les fichiers statiques
```bash
python manage.py collectstatic
```

## 📚 Documentation API

Une fois le serveur lancé, la documentation OpenAPI/Swagger sera disponible à :
- Swagger UI : `http://localhost:8000/api/schema/swagger-ui/`
- ReDoc : `http://localhost:8000/api/schema/redoc/`
- Schema JSON : `http://localhost:8000/api/schema/`

## 🚀 Prochaines Étapes

1. **Implémenter les Serializers** pour tous les modèles
2. **Créer les ViewSets** et endpoints API
3. **Configurer les URLs** pour tous les endpoints
4. **Implémenter les Middlewares** (API key validation, rate limiting)
5. **Créer les utilitaires** (envoi webhooks, emails)
6. **Tests unitaires** pour tous les endpoints
7. **Développement du Frontend** (React/Vue)

## 📄 License

MIT

## 👤 Auteur

Bonito Fotso - bonitofotso55@gmail.com
