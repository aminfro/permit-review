# 🛠️ Permit Review App

A local Flask-based application for managing **permit requests** in engineering and construction projects. Designed for use by **contractors**, **supervisors**, **inspectors**, and **employer supervisors** — with multi-level review, file attachments, and secure authentication.

---

## 🚀 Features

- 📄 **Permit submission** with multi-discipline support
- 📎 Upload multiple **drawings and files** per request
- 👤 Role-based login (Contractor, Inspector, Supervisor)
- 🔁 Multi-step approval flow:
  - Contractor ➜ Contractor Supervisor ➜ All Inspectors ➜ Lead Inspector ➜ Employer Supervisor
- 🗨️ Inspectors can view comments & reviews from other disciplines (read-only)
- 🔐 Secure login with **username + password**
- 📊 Dashboard views for tracking permit status
- 📁 Local file storage (uploads not pushed to GitHub)
- 📬 Notification system (planned)

---

## 📁 Project Structure

 models.py # Database models │ ├── forms.py # Flask-WTF forms │ └── templates/ # HTML files (Jinja2) │ ├── static/ # CSS, JS, images ├── uploads/ # Uploaded permit files (gitignored) ├── instance/ # Config file (local secrets) ├── run.py # App runner ├── requirements.txt # Python dependencies └── README.md

yaml
Copy
Edit


---

## ⚙️ Technologies

- Python + Flask
- SQLite (or switchable to MySQL/PostgreSQL)
- Jinja2 (templating)
- Bootstrap / custom CSS
- Git for version control

---

## 🛠️ Installation (Local)

```bash
# Clone the repo
git clone https://github.com/aminfro/permit-review.git
cd permit-review

# (Optional) Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python run.py
✅ To Do (Next Steps)
 Set up Git version control

 Basic app structure

 User login and roles

 Inspector review interface

 Notification system

 FIN (Field Inspection Notice) module

 Printable PDF export for permits

👨‍💼 Author
Amin Fro
Civil Manager - Jask Oil Tank Project
Fan of clean structure, solar desalination, and Shiraz hikes 🏞️
Contact: [amin.shakib@gmail.com ]

📜 License
MIT License – feel free to use, modify, and build upon this project.

yaml
Copy
Edit
