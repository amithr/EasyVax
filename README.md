# EasyVax
EasyVax is a proof-of-concept vaccine passport system made for healthcare professionals to keep track of and provide patients with QR-code based proof of vaccination.

### Features
- Store patient information
- Store information on vaccine doses given for each patient
- Email .pdfs with patient data and a QR Code that links back to the application to verify whether the user is vaccinated or not

### Future
- Migrate to SASS
- Install webpack to compile SASS to CSS
- CORS (Secure API Routes)

### Installation
- Make sure you have Python 3.8 or greater installed
- If you want to modify the application, initiate and activate a virtual environment
- Run `pip install -r requirements.txt` (to install pip packages)
- Install Postgresql (https://www.postgresql.org/download/)
- Create a database called "easyvax" with a username and password of your choice.
- Set the following environmental variables
    - `DB_USER`
    - `DB_PASSWORD`
    - `EMAIL_ADDRESS` (For the email address your application will use to send emails)
    - `EMAIL_PASSWORD`
- Run `flask db init`, `flask db migrate`, `flask db upgrade` to set up your database
- You may have to adjust settings in your email account to allow your application to user it to send emails. ![This video](https://www.youtube.com/watch?v=oFUbdfX854s&t=163s) could be useful.
- Run the command `flask run` to start the application.

### Tech Stack
This application is written primarily in Python and uses the Flask framework. PostgreSQL is used for the database and the application is hosted on Heroku.