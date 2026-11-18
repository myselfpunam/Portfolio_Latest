# 🗂 Portfolio — Django + Tailwind CV Website

A clean, minimal, fully responsive **resume-style portfolio website** built with Django and Tailwind CSS. Every section is dynamically controlled from the Django admin panel.

---

## ✨ Features

| Feature | Details |
|---|---|
| **Hero section** | Full-width cover image + circular profile photo overlapping the banner |
| **About Me** | Rich text bio, CTA buttons |
| **Skills** | Animated progress bars, categorised (Frontend / Backend / Database / DevOps) |
| **Experience** | Timeline layout with bullet points, duration labels |
| **Education** | Timeline layout with institution links |
| **Projects** | Grid layout with **hover-scroll image preview** + detailed project pages |
| **Resume** | Download CV button (PDF upload from admin) |
| **Contact** | Social links sidebar + working contact form |
| **Sticky navbar** | Collapses on mobile, highlights active section on scroll |
| **Admin panel** | All content editable from Django admin |

---

## 🛠 Tech Stack

- **Backend** — Django 4.x
- **Templates** — Django Templates (no JS framework)
- **Styling** — Tailwind CSS (via CDN)
- **Fonts** — Cormorant Garamond (display) + DM Sans (body) + JetBrains Mono (code)
- **Database** — SQLite (dev) / PostgreSQL (prod)
- **Media** — Pillow, WhiteNoise for static file serving

---

## 🚀 Quick Start

### 1. Clone & create a virtual environment

```bash
git clone <your-repo-url>
cd portfolio_project

python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run migrations

```bash
python manage.py migrate
```

### 4. (Optional) Seed demo data

```bash
python seed_data.py
```

This populates your portfolio with sample profile, skills, experience, education, and projects so you can immediately see the site in action.

### 5. Create an admin superuser

```bash
python manage.py createsuperuser
```

### 6. Start the development server

```bash
python manage.py runserver
```

Then open:
- **Portfolio** → http://127.0.0.1:8000/
- **Admin panel** → http://127.0.0.1:8000/admin/

---

## 📁 Project Structure

```
portfolio_project/
│
├── manage.py
├── requirements.txt
├── seed_data.py               # Demo content seeder
│
├── portfolio/                 # Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── core/                      # Main application
│   ├── models.py              # Profile, Skill, Experience, Education,
│   │                          #   Project, Resume, ContactMessage
│   ├── views.py               # index + project_detail views
│   ├── urls.py
│   ├── admin.py               # Fully customised admin with image previews
│   ├── migrations/
│   └── templatetags/
│       └── portfolio_tags.py  # split_paragraphs, mod_clamp custom filters
│
├── templates/
│   ├── base.html              # Navbar, footer, scripts, Tailwind config
│   ├── index.html             # Single-page portfolio (all sections)
│   └── project_detail.html   # Project detail page with browser mockup
│
├── static/                    # Custom static files (if any)
├── media/                     # Uploaded images / resume PDF (auto-created)
└── db.sqlite3                 # SQLite database
```

---

## 🎨 Django Models

### `Profile`
| Field | Type | Description |
|---|---|---|
| `name` | CharField | Your full name |
| `title` | CharField | e.g. "Web Application Developer" |
| `tagline` | CharField | Short motivating phrase |
| `bio` | TextField | About Me section (double newlines → paragraphs) |
| `profile_image` | ImageField | Circular profile photo |
| `cover_image` | ImageField | Full-width hero banner |
| `email` | EmailField | Contact email |
| `github_url` | URLField | GitHub profile |
| `linkedin_url` | URLField | LinkedIn profile |
| `website_url` | URLField | Personal website |
| `location` | CharField | e.g. "Berlin, Germany" |
| `available_for_work` | BooleanField | Shows green "Available" badge |

### `Skill`
Category choices: `frontend`, `backend`, `database`, `devops`, `other`

### `Experience`
Timeline item. Use `\n`-separated lines in `description` — each becomes a bullet point.

### `Education`
Timeline item with `institution_url` for linking to the university.

### `Project`
| Field | Notes |
|---|---|
| `slug` | Auto-populated from title. Used in URL: `/projects/<slug>/` |
| `thumbnail` | Upload a **tall/full-page screenshot** for the hover-scroll effect |
| `tech_stack` | Comma-separated: `"Django, PostgreSQL, React"` |
| `live_url` | Optional — button only appears if filled |
| `github_url` | Optional — button only appears if filled |
| `is_featured` | Shows a "Featured" badge on the card |

### `Resume`
Upload a PDF. The "Download CV" button in the navbar and Resume section link to it.

---

## ✏️ Customisation

### Colours
Edit `tailwind.config` in `base.html`:
```js
colors: {
  ink:   '#0D0D0D',   // text / dark
  paper: '#FAFAF8',   // background
  warm:  '#C49A6C',   // accent (gold/amber)
  ...
}
```

### Fonts
Replace the Google Fonts `<link>` in `base.html` and update:
```js
fontFamily: {
  display: ['"Your Display Font"', 'serif'],
  body:    ['"Your Body Font"', 'sans-serif'],
  mono:    ['"Your Mono Font"', 'monospace'],
}
```

### Adding sections
1. Add a model in `core/models.py`
2. Register it in `core/admin.py`
3. Pass it from `core/views.py`
4. Add a `<section id="...">` block in `templates/index.html`
5. Add a nav link in the navbar in `templates/base.html`

---

## 🌐 Production Deployment

### Environment variables to set
```env
SECRET_KEY=your-very-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://...   # optional, for Postgres
```

### Collect static files
```bash
python manage.py collectstatic
```

### Recommended stack
- **PaaS**: Railway, Render, Fly.io (easy free tier)
- **VPS**: Ubuntu + Gunicorn + Nginx
- **Database**: PostgreSQL (swap the `DATABASES` setting)
- **Media files**: AWS S3 + `django-storages`

---

## 📄 License

MIT — free to use, modify, and deploy for personal or commercial portfolios.
