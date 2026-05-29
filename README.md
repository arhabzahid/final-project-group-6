# MedCare

## Application Overview

MedCare Scheduling System is a web application that allows patients, providers, and administrators to manage healthcare appointments.

Patients can view provider availability and schedule appointments. Providers can create and manage their availability, while administrators can oversee appointments, patients, and providers through an admin dashboard.

The application was developed using Vue.js, Django REST Framework, and a MySQL cloud database hosted on Aiven.

---

## Features

### Patient Features

* Register an account
* Login securely
* View provider availability
* Schedule appointments
* Cancel appointments
* View appointments
* Receive email notifications

### Provider Features

* Register an account
* Login securely
* Create availability slots
* Edit/Delete availability
* View appointments
* Manage appointments
* Receive email notifications

### Administrator Features

* Login securely
* View patient list
* View provider list
* View availability
* Schedule appointments
* Cancel appointments
* Manage appointments

---

## Tech Stack

### Frontend

* Vue.js
* TypeScript
* Vite

### Backend

* Django
* Django REST Framework

### Database

* MySQL (with Aiven Cloud Database integration)

### APIs & Services

* Gmail SMTP
* REST API Architecture

### Version Control

* Git
* GitHub

---

## Installation

### Environment Variables

Before running the application, create a `.env` file in the backend directory.

The `.env` file is needed for:

* Database connectivity
* Email notification functionality

Example:

```env
DB_NAME=database_name
DB_USER=database_user
DB_PASSWORD=database_pw
DB_HOST=database_host
DB_PORT=3306

EMAIL_HOST_USER=email@gmail.com
EMAIL_HOST_PASSWORD=app_pw
```

> Note: The `.env` file is not included in this repository and must be created manually.

---

### Clone Repository

```bash
git clone <repository-url>
cd final-project-group-6
```

### Backend Setup

```bash
cd backend

python -m venv venv
```

On Windows:

```bash
venv\Scripts\activate
```

On Mac:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run migrations:

```bash
python manage.py migrate
```

Start the backend server:

```bash
python manage.py runserver
```

### Frontend Setup

```bash
cd frontend

npm install
npm run dev
```

---

## Team Members

* Arhab Zahid
* Kiruthika Chan
* Mason Yuen
* Paul Basile

---

## Future Improvements

* SMS notifications
* Appointment reminders
* Calendar integration
* Provider search and filtering
* Billing and payment system

---

