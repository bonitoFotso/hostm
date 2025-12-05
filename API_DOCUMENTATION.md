# 📚 Documentation API HostMail SaaS

## Table des Matières

- [Introduction](#introduction)
- [Authentication](#authentication)
- [Subscriptions](#subscriptions)
- [Websites](#websites)
- [Contacts](#contacts)
- [Projects](#projects)
- [Analytics](#analytics)
- [Webhooks](#webhooks)
- [Payments](#payments)

---

## Introduction

### Base URLs

- **API Authentifiée** : `https://api.hostmail.com/api/v1/`
- **API Publique** : `https://api.hostmail.com/api/public/`

### Authentication Types

1. **JWT Authentication** (Endpoints authentifiés)
   - Header : `Authorization: Bearer <access_token>`

2. **API Key** (Endpoints publics)
   - Header : `X-API-Key: hm_xxxxxxxxxxxxx`

### Codes de Statut

- `200` : Succès
- `201` : Créé avec succès
- `204` : Succès sans contenu
- `400` : Requête invalide
- `401` : Non authentifié
- `403` : Accès interdit
- `404` : Non trouvé
- `429` : Limite atteinte
- `500` : Erreur serveur

---

## Authentication

### 1. Inscription

**Endpoint** : `POST /api/v1/auth/register/`

**Headers**
```
Content-Type: application/json
```

**Body**
```json
{
  "email": "user@example.com",
  "username": "john_doe",
  "password": "SecurePass123!",
  "password2": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Réponse** : `201 Created`
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "john_doe",
    "first_name": "John",
    "last_name": "Doe"
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  },
  "subscription": {
    "id": 1,
    "plan": "free",
    "status": "active",
    "websites_limit": 1,
    "contacts_per_month": 50,
    "projects_limit": 5
  }
}
```

**Erreurs**
```json
{
  "email": ["Un utilisateur avec cet email existe déjà."],
  "password": ["Les mots de passe ne correspondent pas."]
}
```

---

### 2. Connexion

**Endpoint** : `POST /api/v1/auth/login/`

**Body**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Réponse** : `200 OK`
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "john_doe",
    "first_name": "John",
    "last_name": "Doe"
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

---

### 3. Rafraîchir le Token

**Endpoint** : `POST /api/v1/auth/token/refresh/`

**Body**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Réponse** : `200 OK`
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### 4. Profil Utilisateur

**Endpoint** : `GET /api/v1/auth/profile/`

**Headers**
```
Authorization: Bearer <access_token>
```

**Réponse** : `200 OK`
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "john_doe",
  "first_name": "John",
  "last_name": "Doe",
  "date_joined": "2025-01-15T10:30:00Z"
}
```

---

### 5. Mettre à Jour le Profil

**Endpoint** : `PATCH /api/v1/auth/profile/`

**Headers**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Body**
```json
{
  "first_name": "Jean",
  "last_name": "Dupont"
}
```

**Réponse** : `200 OK`
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "john_doe",
  "first_name": "Jean",
  "last_name": "Dupont",
  "date_joined": "2025-01-15T10:30:00Z"
}
```

---

## Subscriptions

### 1. Mon Abonnement

**Endpoint** : `GET /api/v1/subscriptions/me/`

**Headers**
```
Authorization: Bearer <access_token>
```

**Réponse** : `200 OK`
```json
{
  "id": 1,
  "user": 1,
  "plan": "free",
  "billing_period": "monthly",
  "status": "active",
  "websites_limit": 1,
  "websites_count": 0,
  "contacts_per_month": 50,
  "contacts_this_month": 0,
  "projects_limit": 5,
  "projects_count": 0,
  "storage_limit_mb": 100,
  "storage_used_mb": 0,
  "custom_domain": false,
  "remove_branding": false,
  "analytics": false,
  "webhooks": false,
  "priority_support": false,
  "started_at": "2025-01-15T10:30:00Z",
  "expires_at": null,
  "next_billing_date": null
}
```

---

### 2. Plans Disponibles

**Endpoint** : `GET /api/v1/subscriptions/plans/`

**Headers**
```
Authorization: Bearer <access_token>
```

**Réponse** : `200 OK`
```json
{
  "plans": {
    "free": {
      "name": "Free",
      "price": 0,
      "websites_limit": 1,
      "contacts_per_month": 50,
      "projects_limit": 5,
      "storage_limit_mb": 100,
      "custom_domain": false,
      "remove_branding": false,
      "analytics": false,
      "webhooks": false,
      "priority_support": false
    },
    "pro": {
      "name": "Pro",
      "price_monthly": 19,
      "price_yearly": 190,
      "websites_limit": 3,
      "contacts_per_month": 500,
      "projects_limit": -1,
      "storage_limit_mb": 5120,
      "custom_domain": true,
      "remove_branding": true,
      "analytics": true,
      "webhooks": true,
      "priority_support": false
    },
    "agency": {
      "name": "Agency",
      "price_monthly": 49,
      "price_yearly": 490,
      "websites_limit": -1,
      "contacts_per_month": 5000,
      "projects_limit": -1,
      "storage_limit_mb": 20480,
      "custom_domain": true,
      "remove_branding": true,
      "analytics": true,
      "webhooks": true,
      "priority_support": true
    }
  }
}
```

---

### 3. Upgrade de Plan

**Endpoint** : `POST /api/v1/subscriptions/upgrade/`

**Headers**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Body**
```json
{
  "plan": "pro",
  "billing_period": "monthly"
}
```

**Réponse** : `200 OK`
```json
{
  "message": "Veuillez procéder au paiement pour activer votre abonnement",
  "payment_required": true,
  "amount": 19,
  "currency": "EUR",
  "plan": "pro",
  "billing_period": "monthly"
}
```

**Pour Free** : `200 OK`
```json
{
  "message": "Plan modifié avec succès",
  "subscription": {
    "id": 1,
    "plan": "free",
    "status": "active"
  }
}
```

---

### 4. Annuler l'Abonnement

**Endpoint** : `POST /api/v1/subscriptions/cancel/`

**Headers**
```
Authorization: Bearer <access_token>
```

**Réponse** : `200 OK`
```json
{
  "message": "Abonnement annulé avec succès",
  "subscription": {
    "id": 1,
    "plan": "free",
    "status": "active"
  }
}
```

---

## Websites

### 1. Lister Mes Websites

**Endpoint** : `GET /api/v1/websites/`

**Headers**
```
Authorization: Bearer <access_token>
```

**Réponse** : `200 OK`
```json
[
  {
    "id": 1,
    "name": "Mon Portfolio",
    "domain": "https://johndoe.com",
    "description": "Portfolio personnel de John Doe",
    "api_key": "hm_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "is_active": true,
    "allowed_origins": ["https://johndoe.com", "http://localhost:3000"],
    "notification_email": "john@example.com",
    "created_at": "2025-01-15T11:00:00Z",
    "updated_at": "2025-01-15T11:00:00Z"
  }
]
```

---

### 2. Créer un Website

**Endpoint** : `POST /api/v1/websites/`

**Headers**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Body**
```json
{
  "name": "Mon Portfolio",
  "domain": "https://johndoe.com",
  "description": "Portfolio personnel de John Doe",
  "allowed_origins": ["https://johndoe.com", "http://localhost:3000"],
  "notification_email": "john@example.com"
}
```

**Réponse** : `201 Created`
```json
{
  "id": 1,
  "name": "Mon Portfolio",
  "domain": "https://johndoe.com",
  "description": "Portfolio personnel de John Doe",
  "api_key": "hm_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "is_active": true,
  "allowed_origins": ["https://johndoe.com", "http://localhost:3000"],
  "notification_email": "john@example.com",
  "created_at": "2025-01-15T11:00:00Z",
  "updated_at": "2025-01-15T11:00:00Z"
}
```

**Erreur - Limite atteinte** : `400 Bad Request`
```json
{
  "non_field_errors": ["Vous avez atteint la limite de websites pour votre plan"]
}
```

---

### 3. Détails d'un Website

**Endpoint** : `GET /api/v1/websites/{id}/`

**Headers**
```
Authorization: Bearer <access_token>
```

**Réponse** : `200 OK`
```json
{
  "id": 1,
  "name": "Mon Portfolio",
  "domain": "https://johndoe.com",
  "description": "Portfolio personnel de John Doe",
  "api_key": "hm_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "is_active": true,
  "allowed_origins": ["https://johndoe.com", "http://localhost:3000"],
  "notification_email": "john@example.com",
  "created_at": "2025-01-15T11:00:00Z",
  "updated_at": "2025-01-15T11:00:00Z"
}
```

---

### 4. Mettre à Jour un Website

**Endpoint** : `PATCH /api/v1/websites/{id}/`

**Headers**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Body**
```json
{
  "name": "Portfolio Pro",
  "notification_email": "newemail@example.com"
}
```

**Réponse** : `200 OK`
```json
{
  "id": 1,
  "name": "Portfolio Pro",
  "domain": "https://johndoe.com",
  "description": "Portfolio personnel de John Doe",
  "api_key": "hm_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "is_active": true,
  "allowed_origins": ["https://johndoe.com", "http://localhost:3000"],
  "notification_email": "newemail@example.com",
  "created_at": "2025-01-15T11:00:00Z",
  "updated_at": "2025-01-15T12:00:00Z"
}
```

---

### 5. Regénérer l'API Key

**Endpoint** : `POST /api/v1/websites/{id}/regenerate_key/`

**Headers**
```
Authorization: Bearer <access_token>
```

**Réponse** : `200 OK`
```json
{
  "message": "API key régénérée avec succès",
  "api_key": "hm_yyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"
}
```

---

### 6. Supprimer un Website

**Endpoint** : `DELETE /api/v1/websites/{id}/`

**Headers**
```
Authorization: Bearer <access_token>
```

**Réponse** : `204 No Content`

---

## Contacts

### 1. Configuration du Formulaire

#### Lister les Champs

**Endpoint** : `GET /api/v1/contacts/fields/`

**Headers**
```
Authorization: Bearer <access_token>
```

**Query Parameters**
```
?website={website_id}
```

**Réponse** : `200 OK`
```json
[
  {
    "id": 1,
    "website": 1,
    "field_name": "email",
    "field_type": "email",
    "label": "Email",
    "placeholder": "votre@email.com",
    "is_required": true,
    "order": 1,
    "validation_rules": {
      "max_length": 255
    }
  },
  {
    "id": 2,
    "website": 1,
    "field_name": "name",
    "field_type": "text",
    "label": "Nom complet",
    "placeholder": "John Doe",
    "is_required": true,
    "order": 2,
    "validation_rules": {}
  }
]
```

---

#### Créer un Champ

**Endpoint** : `POST /api/v1/contacts/fields/`

**Headers**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Body**
```json
{
  "website": 1,
  "field_name": "company",
  "field_type": "text",
  "label": "Entreprise",
  "placeholder": "Nom de votre entreprise",
  "is_required": false,
  "order": 5,
  "validation_rules": {
    "max_length": 200
  }
}
```

**Types de champs disponibles** : `text`, `email`, `textarea`, `tel`, `url`, `select`, `checkbox`, `radio`, `number`, `date`

**Réponse** : `201 Created`
```json
{
  "id": 5,
  "website": 1,
  "field_name": "company",
  "field_type": "text",
  "label": "Entreprise",
  "placeholder": "Nom de votre entreprise",
  "is_required": false,
  "order": 5,
  "validation_rules": {
    "max_length": 200
  }
}
```

---

### 2. Gestion des Messages (Authentifié)

#### Lister les Messages

**Endpoint** : `GET /api/v1/contacts/messages/`

**Headers**
```
Authorization: Bearer <access_token>
```

**Query Parameters**
```
?website={website_id}
&status=unread
&search=john
```

**Statuts disponibles** : `unread`, `read`, `archived`, `spam`

**Réponse** : `200 OK`
```json
[
  {
    "id": 1,
    "website": 1,
    "form_data": {
      "name": "John Doe",
      "email": "john@example.com",
      "subject": "Demande de devis",
      "message": "Bonjour, je souhaiterais un devis pour...",
      "company": "ABC Corp"
    },
    "email": "john@example.com",
    "name": "John Doe",
    "subject": "Demande de devis",
    "message": "Bonjour, je souhaiterais un devis pour...",
    "status": "unread",
    "ip_address": "192.168.1.1",
    "user_agent": "Mozilla/5.0...",
    "created_at": "2025-01-15T14:30:00Z",
    "updated_at": "2025-01-15T14:30:00Z"
  }
]
```

---

#### Détails d'un Message

**Endpoint** : `GET /api/v1/contacts/messages/{id}/`

**Headers**
```
Authorization: Bearer <access_token>
```

**Réponse** : `200 OK`
```json
{
  "id": 1,
  "website": 1,
  "form_data": {
    "name": "John Doe",
    "email": "john@example.com",
    "subject": "Demande de devis",
    "message": "Bonjour, je souhaiterais un devis pour...",
    "company": "ABC Corp"
  },
  "email": "john@example.com",
  "name": "John Doe",
  "subject": "Demande de devis",
  "message": "Bonjour, je souhaiterais un devis pour...",
  "status": "read",
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "created_at": "2025-01-15T14:30:00Z",
  "updated_at": "2025-01-15T15:00:00Z"
}
```

---

#### Changer le Statut

**Endpoint** : `POST /api/v1/contacts/messages/{id}/mark_as_read/`

**Autres actions** : `/mark_as_unread/`, `/mark_as_archived/`, `/mark_as_spam/`

**Headers**
```
Authorization: Bearer <access_token>
```

**Réponse** : `200 OK`
```json
{
  "message": "Message marqué comme lu",
  "status": "read"
}
```

---

### 3. Soumission Publique (API Key)

**Endpoint** : `POST /api/public/contact/submit/`

**Headers**
```
X-API-Key: hm_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Content-Type: application/json
```

**Body**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "subject": "Demande d'information",
  "message": "Bonjour, je souhaiterais des informations sur...",
  "company": "ABC Corp",
  "phone": "+33612345678"
}
```

**Réponse** : `201 Created`
```json
{
  "message": "Message envoyé avec succès",
  "id": 1
}
```

**Erreur - Limite atteinte** : `429 Too Many Requests`
```json
{
  "error": "Limite de contacts mensuelle atteinte"
}
```

**Erreur - API Key manquante** : `401 Unauthorized`
```json
{
  "error": "API key manquante",
  "detail": "Veuillez fournir une API key valide dans le header X-API-Key"
}
```

**Erreur - API Key invalide** : `401 Unauthorized`
```json
{
  "error": "API key invalide",
  "detail": "L'API key fournie est invalide ou le site est désactivé"
}
```

**Erreur - Rate limit** : `429 Too Many Requests`
```json
{
  "error": "Trop de requêtes",
  "detail": "Veuillez patienter avant de soumettre un nouveau message"
}
```

---

## Projects

### 1. Gestion des Catégories

#### Lister les Catégories

**Endpoint** : `GET /api/v1/projects/categories/`

**Headers**
```
Authorization: Bearer <access_token>
```

**Query Parameters**
```
?website={website_id}
```

**Réponse** : `200 OK`
```json
[
  {
    "id": 1,
    "website": 1,
    "name": "Web Development",
    "slug": "web-development",
    "description": "Projets de développement web",
    "order": 1,
    "created_at": "2025-01-15T10:00:00Z"
  }
]
```

---

#### Créer une Catégorie

**Endpoint** : `POST /api/v1/projects/categories/`

**Headers**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Body**
```json
{
  "website": 1,
  "name": "Web Development",
  "description": "Projets de développement web",
  "order": 1
}
```

**Réponse** : `201 Created`
```json
{
  "id": 1,
  "website": 1,
  "name": "Web Development",
  "slug": "web-development",
  "description": "Projets de développement web",
  "order": 1,
  "created_at": "2025-01-15T10:00:00Z"
}
```

---

### 2. Gestion des Tags

#### Lister les Tags

**Endpoint** : `GET /api/v1/projects/tags/`

**Headers**
```
Authorization: Bearer <access_token>
```

**Query Parameters**
```
?website={website_id}
```

**Réponse** : `200 OK`
```json
[
  {
    "id": 1,
    "website": 1,
    "name": "React",
    "slug": "react",
    "color": "#61DAFB"
  }
]
```

---

#### Créer un Tag

**Endpoint** : `POST /api/v1/projects/tags/`

**Headers**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Body**
```json
{
  "website": 1,
  "name": "React",
  "color": "#61DAFB"
}
```

**Réponse** : `201 Created`
```json
{
  "id": 1,
  "website": 1,
  "name": "React",
  "slug": "react",
  "color": "#61DAFB"
}
```

---

### 3. Gestion des Projets (Authentifié)

#### Lister les Projets

**Endpoint** : `GET /api/v1/projects/projects/`

**Headers**
```
Authorization: Bearer <access_token>
```

**Query Parameters**
```
?website={website_id}
&status=published
&category=1
&tags=1,2
&search=ecommerce
```

**Réponse** : `200 OK`
```json
[
  {
    "id": 1,
    "website": 1,
    "title": "Site E-commerce",
    "slug": "site-ecommerce",
    "description": "Plateforme e-commerce complète avec panier et paiement",
    "content": "Détails complets du projet...",
    "category": {
      "id": 1,
      "name": "Web Development",
      "slug": "web-development"
    },
    "tags": [
      {
        "id": 1,
        "name": "React",
        "slug": "react",
        "color": "#61DAFB"
      },
      {
        "id": 2,
        "name": "Node.js",
        "slug": "nodejs",
        "color": "#339933"
      }
    ],
    "client_name": "ABC Corp",
    "project_url": "https://example-shop.com",
    "github_url": null,
    "start_date": "2024-01-01",
    "end_date": "2024-03-15",
    "technologies": ["React", "Node.js", "MongoDB", "Stripe"],
    "featured_image": "https://minio.f2mb.xyz/hostmail/projects/project-1.jpg",
    "status": "published",
    "is_featured": true,
    "views_count": 245,
    "custom_fields": {
      "budget": "10000 EUR",
      "team_size": "3"
    },
    "published_at": "2024-03-20T10:00:00Z",
    "created_at": "2024-03-15T09:00:00Z",
    "updated_at": "2024-03-20T10:00:00Z"
  }
]
```

---

#### Créer un Projet

**Endpoint** : `POST /api/v1/projects/projects/`

**Headers**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Body**
```json
{
  "website": 1,
  "title": "Site E-commerce",
  "description": "Plateforme e-commerce complète",
  "content": "Détails complets du projet...",
  "category": 1,
  "tags": [1, 2],
  "client_name": "ABC Corp",
  "project_url": "https://example-shop.com",
  "start_date": "2024-01-01",
  "end_date": "2024-03-15",
  "technologies": ["React", "Node.js", "MongoDB", "Stripe"],
  "status": "draft",
  "is_featured": false,
  "custom_fields": {
    "budget": "10000 EUR",
    "team_size": "3"
  }
}
```

**Réponse** : `201 Created`
```json
{
  "id": 1,
  "website": 1,
  "title": "Site E-commerce",
  "slug": "site-ecommerce",
  "description": "Plateforme e-commerce complète",
  "content": "Détails complets du projet...",
  "category": {
    "id": 1,
    "name": "Web Development",
    "slug": "web-development"
  },
  "tags": [
    {
      "id": 1,
      "name": "React",
      "slug": "react",
      "color": "#61DAFB"
    }
  ],
  "client_name": "ABC Corp",
  "project_url": "https://example-shop.com",
  "github_url": null,
  "start_date": "2024-01-01",
  "end_date": "2024-03-15",
  "technologies": ["React", "Node.js", "MongoDB", "Stripe"],
  "featured_image": null,
  "status": "draft",
  "is_featured": false,
  "views_count": 0,
  "custom_fields": {
    "budget": "10000 EUR",
    "team_size": "3"
  },
  "published_at": null,
  "created_at": "2024-03-15T09:00:00Z",
  "updated_at": "2024-03-15T09:00:00Z"
}
```

**Erreur - Limite atteinte** : `400 Bad Request`
```json
{
  "non_field_errors": ["Vous avez atteint la limite de projets pour votre plan"]
}
```

---

#### Mettre à Jour un Projet

**Endpoint** : `PATCH /api/v1/projects/projects/{id}/`

**Headers**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Body**
```json
{
  "title": "Site E-commerce Premium",
  "is_featured": true
}
```

**Réponse** : `200 OK`

---

#### Publier un Projet

**Endpoint** : `POST /api/v1/projects/projects/{id}/publish/`

**Headers**
```
Authorization: Bearer <access_token>
```

**Réponse** : `200 OK`
```json
{
  "message": "Projet publié avec succès",
  "status": "published",
  "published_at": "2024-03-20T10:00:00Z"
}
```

---

#### Mettre en Vedette

**Endpoint** : `POST /api/v1/projects/projects/{id}/toggle_featured/`

**Headers**
```
Authorization: Bearer <access_token>
```

**Réponse** : `200 OK`
```json
{
  "message": "Projet mis en vedette",
  "is_featured": true
}
```

---

### 4. Images de Projet

#### Ajouter une Image

**Endpoint** : `POST /api/v1/projects/images/`

**Headers**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Body** (Form Data)
```
project: 1
image: [fichier image]
caption: "Interface principale"
order: 1
is_featured: false
```

**Réponse** : `201 Created`
```json
{
  "id": 1,
  "project": 1,
  "image": "https://minio.f2mb.xyz/hostmail/projects/images/image-1.jpg",
  "caption": "Interface principale",
  "order": 1,
  "is_featured": false
}
```

---

#### Lister les Images

**Endpoint** : `GET /api/v1/projects/images/?project={project_id}`

**Headers**
```
Authorization: Bearer <access_token>
```

**Réponse** : `200 OK`
```json
[
  {
    "id": 1,
    "project": 1,
    "image": "https://minio.f2mb.xyz/hostmail/projects/images/image-1.jpg",
    "caption": "Interface principale",
    "order": 1,
    "is_featured": true
  }
]
```

---

### 5. API Publique des Projets (API Key)

#### Lister les Projets Publics

**Endpoint** : `GET /api/public/projects/`

**Headers**
```
X-API-Key: hm_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Query Parameters**
```
?category=web-development
&tags=react,nodejs
&featured=true
&limit=10
&offset=0
```

**Réponse** : `200 OK`
```json
{
  "count": 25,
  "next": "https://api.hostmail.com/api/public/projects/?offset=10",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Site E-commerce",
      "slug": "site-ecommerce",
      "description": "Plateforme e-commerce complète",
      "content": "Détails complets du projet...",
      "category": {
        "id": 1,
        "name": "Web Development",
        "slug": "web-development"
      },
      "tags": [
        {
          "id": 1,
          "name": "React",
          "slug": "react",
          "color": "#61DAFB"
        }
      ],
      "client_name": "ABC Corp",
      "project_url": "https://example-shop.com",
      "github_url": null,
      "start_date": "2024-01-01",
      "end_date": "2024-03-15",
      "technologies": ["React", "Node.js", "MongoDB", "Stripe"],
      "featured_image": "https://minio.f2mb.xyz/hostmail/projects/project-1.jpg",
      "images": [
        {
          "id": 1,
          "image": "https://minio.f2mb.xyz/hostmail/projects/images/image-1.jpg",
          "caption": "Interface principale",
          "order": 1
        }
      ],
      "is_featured": true,
      "views_count": 245,
      "published_at": "2024-03-20T10:00:00Z"
    }
  ]
}
```

---

#### Détails d'un Projet Public

**Endpoint** : `GET /api/public/projects/{slug}/`

**Headers**
```
X-API-Key: hm_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Réponse** : `200 OK`
```json
{
  "id": 1,
  "title": "Site E-commerce",
  "slug": "site-ecommerce",
  "description": "Plateforme e-commerce complète",
  "content": "Détails complets du projet...",
  "category": {
    "id": 1,
    "name": "Web Development",
    "slug": "web-development"
  },
  "tags": [
    {
      "id": 1,
      "name": "React",
      "slug": "react",
      "color": "#61DAFB"
    }
  ],
  "client_name": "ABC Corp",
  "project_url": "https://example-shop.com",
  "github_url": null,
  "start_date": "2024-01-01",
  "end_date": "2024-03-15",
  "technologies": ["React", "Node.js", "MongoDB", "Stripe"],
  "featured_image": "https://minio.f2mb.xyz/hostmail/projects/project-1.jpg",
  "images": [
    {
      "id": 1,
      "image": "https://minio.f2mb.xyz/hostmail/projects/images/image-1.jpg",
      "caption": "Interface principale",
      "order": 1
    }
  ],
  "is_featured": true,
  "views_count": 246,
  "custom_fields": {
    "budget": "10000 EUR",
    "team_size": "3"
  },
  "published_at": "2024-03-20T10:00:00Z"
}
```

---

## Analytics

**Requis** : Plan Pro ou Agency avec analytics activé

### 1. Enregistrer un Événement

**Endpoint** : `POST /api/v1/analytics/events/`

**Headers**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Body**
```json
{
  "website": 1,
  "event_type": "page_view",
  "event_data": {
    "page": "/projects/site-ecommerce",
    "referrer": "https://google.com",
    "user_agent": "Mozilla/5.0..."
  },
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0..."
}
```

**Types d'événements** : `page_view`, `contact_submit`, `project_view`, `custom`

**Réponse** : `201 Created`
```json
{
  "id": 1,
  "website": 1,
  "event_type": "page_view",
  "event_data": {
    "page": "/projects/site-ecommerce",
    "referrer": "https://google.com"
  },
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "created_at": "2025-01-15T14:30:00Z"
}
```

---

### 2. Statistiques Globales

**Endpoint** : `GET /api/v1/analytics/stats/`

**Headers**
```
Authorization: Bearer <access_token>
```

**Query Parameters**
```
?website={website_id}
&start_date=2025-01-01
&end_date=2025-01-31
```

**Réponse** : `200 OK`
```json
{
  "website": 1,
  "period": {
    "start": "2025-01-01",
    "end": "2025-01-31"
  },
  "total_page_views": 1250,
  "total_contacts": 45,
  "total_project_views": 320,
  "unique_visitors": 890,
  "top_pages": [
    {
      "page": "/projects/site-ecommerce",
      "views": 245
    },
    {
      "page": "/",
      "views": 180
    }
  ],
  "top_referrers": [
    {
      "referrer": "google.com",
      "count": 450
    },
    {
      "referrer": "direct",
      "count": 340
    }
  ],
  "daily_stats": [
    {
      "date": "2025-01-01",
      "page_views": 42,
      "contacts": 2,
      "project_views": 12
    }
  ]
}
```

---

### 3. Statistiques Journalières

**Endpoint** : `GET /api/v1/analytics/daily/`

**Headers**
```
Authorization: Bearer <access_token>
```

**Query Parameters**
```
?website={website_id}
&start_date=2025-01-01
&end_date=2025-01-31
```

**Réponse** : `200 OK`
```json
[
  {
    "id": 1,
    "website": 1,
    "date": "2025-01-15",
    "page_views": 42,
    "unique_visitors": 35,
    "contacts_received": 2,
    "project_views": 12,
    "avg_session_duration": 180.5
  }
]
```

---

## Webhooks

**Requis** : Plan Pro ou Agency avec webhooks activé

### 1. Lister les Webhooks

**Endpoint** : `GET /api/v1/webhooks/webhooks/`

**Headers**
```
Authorization: Bearer <access_token>
```

**Query Parameters**
```
?website={website_id}
```

**Réponse** : `200 OK`
```json
[
  {
    "id": 1,
    "website": 1,
    "name": "Notification Slack",
    "url": "https://hooks.slack.com/services/xxx",
    "events": ["contact.received", "project.published"],
    "is_active": true,
    "secret": "whsec_xxxxxxxxxxxxx",
    "headers": {
      "Authorization": "Bearer xxx"
    },
    "created_at": "2025-01-15T10:00:00Z"
  }
]
```

**Événements disponibles** :
- `contact.received`
- `contact.read`
- `contact.archived`
- `project.published`
- `project.updated`
- `subscription.upgraded`
- `subscription.cancelled`

---

### 2. Créer un Webhook

**Endpoint** : `POST /api/v1/webhooks/webhooks/`

**Headers**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Body**
```json
{
  "website": 1,
  "name": "Notification Slack",
  "url": "https://hooks.slack.com/services/xxx",
  "events": ["contact.received", "project.published"],
  "is_active": true,
  "headers": {
    "Authorization": "Bearer xxx"
  }
}
```

**Réponse** : `201 Created`
```json
{
  "id": 1,
  "website": 1,
  "name": "Notification Slack",
  "url": "https://hooks.slack.com/services/xxx",
  "events": ["contact.received", "project.published"],
  "is_active": true,
  "secret": "whsec_xxxxxxxxxxxxx",
  "headers": {
    "Authorization": "Bearer xxx"
  },
  "created_at": "2025-01-15T10:00:00Z"
}
```

**Erreur - Feature non disponible** : `403 Forbidden`
```json
{
  "detail": "Cette fonctionnalité nécessite un abonnement Pro ou Agency"
}
```

---

### 3. Logs des Webhooks

**Endpoint** : `GET /api/v1/webhooks/logs/`

**Headers**
```
Authorization: Bearer <access_token>
```

**Query Parameters**
```
?webhook={webhook_id}
&success=true
```

**Réponse** : `200 OK`
```json
[
  {
    "id": 1,
    "webhook": 1,
    "event_type": "contact.received",
    "payload": {
      "event": "contact.received",
      "data": {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com"
      }
    },
    "response_status": 200,
    "response_body": "ok",
    "success": true,
    "error_message": null,
    "sent_at": "2025-01-15T14:30:00Z"
  }
]
```

---

### 4. Tester un Webhook

**Endpoint** : `POST /api/v1/webhooks/webhooks/{id}/test/`

**Headers**
```
Authorization: Bearer <access_token>
```

**Réponse** : `200 OK`
```json
{
  "message": "Webhook testé avec succès",
  "success": true,
  "status_code": 200
}
```

---

## Payments

### 1. Créer une Commande PayPal

**Endpoint** : `POST /api/v1/payments/paypal/create-order/`

**Headers**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Body**
```json
{
  "plan": "pro",
  "billing_period": "monthly"
}
```

**Réponse** : `200 OK`
```json
{
  "order_id": "7XP12345ABC67890",
  "approval_url": "https://www.paypal.com/checkoutnow?token=7XP12345ABC67890",
  "amount": 19,
  "currency": "EUR"
}
```

---

### 2. Capturer le Paiement PayPal

**Endpoint** : `POST /api/v1/payments/paypal/capture-order/`

**Headers**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Body**
```json
{
  "order_id": "7XP12345ABC67890"
}
```

**Réponse** : `200 OK`
```json
{
  "message": "Paiement effectué avec succès",
  "payment_id": 1,
  "subscription": {
    "id": 1,
    "plan": "pro",
    "status": "active",
    "expires_at": "2025-02-15T10:00:00Z"
  }
}
```

---

### 3. Historique des Paiements

**Endpoint** : `GET /api/v1/payments/payments/`

**Headers**
```
Authorization: Bearer <access_token>
```

**Réponse** : `200 OK`
```json
[
  {
    "id": 1,
    "user": 1,
    "subscription": 1,
    "amount": 19.00,
    "currency": "EUR",
    "status": "completed",
    "payment_method": "paypal",
    "transaction_id": "7XP12345ABC67890",
    "metadata": {
      "plan": "pro",
      "billing_period": "monthly"
    },
    "created_at": "2025-01-15T10:00:00Z",
    "updated_at": "2025-01-15T10:05:00Z"
  }
]
```

**Statuts** : `pending`, `completed`, `failed`, `refunded`

---

### 4. Factures

**Endpoint** : `GET /api/v1/payments/invoices/`

**Headers**
```
Authorization: Bearer <access_token>
```

**Réponse** : `200 OK`
```json
[
  {
    "id": 1,
    "payment": 1,
    "invoice_number": "INV-2025-001",
    "invoice_date": "2025-01-15",
    "due_date": "2025-02-15",
    "subtotal": 19.00,
    "tax": 3.80,
    "total": 22.80,
    "currency": "EUR",
    "status": "paid",
    "notes": "Abonnement Pro - Mensuel",
    "pdf_url": null
  }
]
```

---

### 5. Télécharger une Facture

**Endpoint** : `GET /api/v1/payments/invoices/{id}/download/`

**Headers**
```
Authorization: Bearer <access_token>
```

**Réponse** : `200 OK`
```json
{
  "url": "https://minio.f2mb.xyz/hostmail/invoices/INV-2025-001.pdf"
}
```

---

## Exemples d'Intégration

### Frontend React - Formulaire de Contact

```javascript
const submitContact = async (formData) => {
  try {
    const response = await fetch('https://api.hostmail.com/api/public/contact/submit/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': 'hm_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
      },
      body: JSON.stringify(formData)
    });

    if (!response.ok) {
      throw new Error('Erreur lors de l\'envoi');
    }

    const data = await response.json();
    console.log('Message envoyé:', data);
  } catch (error) {
    console.error('Erreur:', error);
  }
};
```

---

### Frontend React - Afficher les Projets

```javascript
const fetchProjects = async () => {
  try {
    const response = await fetch('https://api.hostmail.com/api/public/projects/', {
      headers: {
        'X-API-Key': 'hm_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
      }
    });

    const data = await response.json();
    setProjects(data.results);
  } catch (error) {
    console.error('Erreur:', error);
  }
};
```

---

### Backend - Webhook Payload

Lorsqu'un événement se produit, HostMail envoie une requête POST à votre URL de webhook :

```json
{
  "event": "contact.received",
  "timestamp": "2025-01-15T14:30:00Z",
  "website": {
    "id": 1,
    "name": "Mon Portfolio",
    "domain": "https://johndoe.com"
  },
  "data": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "subject": "Demande d'information",
    "message": "Bonjour...",
    "created_at": "2025-01-15T14:30:00Z"
  }
}
```

**Vérification de signature** :

```javascript
const crypto = require('crypto');

function verifyWebhookSignature(payload, signature, secret) {
  const hash = crypto
    .createHmac('sha256', secret)
    .update(JSON.stringify(payload))
    .digest('hex');

  return hash === signature;
}

// Dans votre endpoint webhook
app.post('/webhook', (req, res) => {
  const signature = req.headers['x-hostmail-signature'];
  const isValid = verifyWebhookSignature(req.body, signature, 'whsec_xxxxx');

  if (!isValid) {
    return res.status(401).json({ error: 'Invalid signature' });
  }

  // Traiter l'événement
  console.log('Event:', req.body.event);
  res.json({ success: true });
});
```

---

## Limites et Quotas

### Plan Free
- 1 website
- 50 contacts/mois
- 5 projets
- 100 MB stockage
- Pas d'analytics
- Pas de webhooks

### Plan Pro
- 3 websites
- 500 contacts/mois
- Projets illimités
- 5 GB stockage
- Analytics inclus
- Webhooks inclus

### Plan Agency
- Websites illimités
- 5000 contacts/mois
- Projets illimités
- 20 GB stockage
- Analytics inclus
- Webhooks inclus
- Support prioritaire

---

## Support et Contact

- **Documentation** : https://docs.hostmail.com
- **Support** : support@hostmail.com
- **Status** : https://status.hostmail.com

---

**Version** : 1.0.0
**Dernière mise à jour** : 2025-01-15
