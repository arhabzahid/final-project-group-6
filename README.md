# final project group 6
# Backend Setup: python, pip, django commands
cd backend
python -m venv venv
Mac: source venv/bin/activate
--WITH THE VIRTUAL ENV INSIDE BACKEND DIRECTORY--
--env must be activated for any python commands--
pip install -r requirements.txt
create database hospital;
create user 'hospitalUser'@'localhost' identified by 'yourpwhere';
grant all privileges on hospital.* to 'hospitalUser'@'localhost';
flush privileges;

python manage.py migrate
python manage.py runserver

#Frontend Setup: npm, vue commands
cd frontend
npm install
npm run dev

