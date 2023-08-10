from flask_login import current_user
from flask import Flask, render_template, url_for, request, redirect, flash, session, g, send_from_directory, jsonify
import secrets
import os
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
# from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from collections import Counter

from flask_admin import Admin,  AdminIndexView
from flask_admin.contrib import sqla


app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'static/files/cv'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/flaskapp'
app.config['SECRET_KEY'] = '1234'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flaskapp'
db = SQLAlchemy(app)


mysql = MySQL(app)


class listings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    companyname = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)


class Submit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
   
    companyname = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    
    cv = db.Column(db.String(1000), nullable=False)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Students(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)    


admin = Admin(app, name='Admin', template_mode='bootstrap3')


class ListingAdmin(sqla.ModelView):
    column_list = ('companyname', 'role', 'location', 'category')
    form_columns = ('companyname', 'role', 'location', 'category')


class SubmitAdmin(sqla.ModelView):
    column_list = ('companyname', 'category', 'role','cv')
    form_columns = ('companyname', 'category',
                    'role')


class UsersAdmin(sqla.ModelView):
    column_list = ('username', 'email')
    form_columns = ('username', 'email')

class StudentsAdmin(sqla.ModelView):
    column_list = ('username', 'email')
    form_columns = ('username', 'email')


# Connect Flask-Admin to app's MySQL database
admin.add_view(ListingAdmin(listings, db.session,
               name='Opportunities'))

admin.add_view(SubmitAdmin(Submit, db.session,
               name='CV submissions' ))

admin.add_view(UsersAdmin(Users, db.session,
               name='Companies'))

admin.add_view(StudentsAdmin(Students, db.session,
               name='Students'))

for rule in app.url_map.iter_rules():
    print(rule.endpoint)


login_manager = LoginManager(app)
login_manager.login_view = 'login'



class User(UserMixin):
   def__init__(self,user_id):
        self.id=user_id

    @staticmethod
    def get(user_id):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user_data = cur.fetchone()
        cur.close()

        if user_data:
            # Create a new User instance with the found user_id
            return User(user_data[0])
        else:
            return None
        
class User1(UserMixin):
    def__init__(self,user_id1):
     self.id1=user_id1
       

    @staticmethod
    def get(user_id1):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM students WHERE id = %s", (user_id1,))
        user_data1 = cur.fetchone()
        cur.close()

        if user_data1:
            # Create a new User instance with the found user_id
            return User1(user_data1[0])
        else:
            return None


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@login_manager.user_loader
def load_user1(user_id1):
    return User1.get(user_id1)


@app.before_request
def before_request():
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(16)
    g.csrf_token = session['csrf_token']


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        details = request.form
        companyUsername = details['username']
        Password = details['password']
        email = details['email']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s",
                    (companyUsername,))
        user_data = cur.fetchone()

        if user_data:
            # Username already exists, redirect to a page showing error or handle accordingly
            flash('Username already exists!', 'error')
            return redirect(url_for('signup'))

        # If username does not exist, insert the data
        cur.execute("INSERT INTO users(username, email, password) VALUES (%s, %s, %s)",
                    (companyUsername, email, Password))
        mysql.connection.commit()
        cur.close()
        flash('User successfully registered!', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/signup1', methods=['GET', 'POST'])
def signup1():
    if request.method == "POST":
        details = request.form
        Fullname = details['fullname']
        Username = details['username']
        Password = details['password']
        email = details['email']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM students WHERE username = %s",
                    (Username,))
        user_data = cur.fetchone()

        if user_data:
            # Username already exists, redirect to a page showing error or handle accordingly
            flash('Username already exists!', 'error')
            return redirect(url_for('signup1'))

        # If username does not exist, insert the data
        cur.execute("INSERT INTO students(fullname, username, email, password) VALUES (%s, %s, %s, %s)",
                    ( Fullname, Username, email, Password))
        mysql.connection.commit()
        cur.close()
        flash('User successfully registered!', 'success')
        return redirect(url_for('login1'))

    return render_template('signup1.html')


@app.route('/company', methods=['GET', 'POST'])

def company():
    if request.method == "POST":
        details = request.form
        companyName = details['companyname']
        Role = details['role']
        Location = details['location']
        Category = details['category']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO listings(companyname, role, location, category ) VALUES (%s, %s, %s, %s)",
                    (companyName, Role, Location, Category))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('company'))

    # Fetch all CV submissions from the 'Submit' table for the current user's companyname
    cur = mysql.connection.cursor()
    # Retrieve the logged-in user's username from the session
    username = session.get('username')
    cur.execute("SELECT * FROM submit WHERE companyname = %s", (username,))
    cv_submissions = cur.fetchall()

    # Query to fetch data from the listings table for the current user's companyname
    cur.execute("SELECT * FROM listings WHERE companyname = %s", (username,))
    listings_data = cur.fetchall()

    cur.close()
   
    return render_template('company.html', cv_submissions=cv_submissions, listings_data=listings_data)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # If login is successful, store the username in the session
        session['username'] = username

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user_data = cur.fetchone()
        cur.close()

        if user_data and username == 'admin' and password == 'admin':
            user = User(user_data[0])
            login_user(user)
            flash('Logged in successfully as admin!', 'success')
            return redirect(url_for('admin1'))
        elif user_data:
            user = User(user_data[0])
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('company'))
        else:
            flash('Invalid username or password', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')




@app.route('/login1', methods=['GET', 'POST'])
def login1():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # If login is successful, store the username in the session
        session['username'] = username

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM students WHERE username = %s", (username,))
        user_data1 = cur.fetchone()
        cur.close()
        
        if user_data1 and user_data1[4] == password:
            user = User1(user_data1[0])
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('job_list'))
        
        else:
            flash('Invalid username or password', 'error')
            return redirect(url_for('login1'))

    return render_template('login1.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('username', None)  # Clear the 'username' from the session
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

@app.route('/logout1')
@login_required
def logout1():
    logout_user()
    session.pop('username', None)  # Clear the 'username' from the session
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login1'))

@app.route('/admin1', methods=['GET', 'POST'])
@login_required
def admin1():
    # if request.method == "POST":
    #     details = request.form
    #     companyName = details['companyname']
    #     Role = details['role']
    #     Location = details['location']
    #     Category = details['category']
    #     cur = mysql.connection.cursor()
    #     cur.execute("INSERT INTO listings(companyname, role, location, category ) VALUES (%s, %s, %s, %s)",
    #                 (companyName, Role, Location, Category))
    #     mysql.connection.commit()
    #     cur.close()
    #     return 'success'

    # Fetch data from the 'listings' and 'submit' tables to get the counts
    cur = mysql.connection.cursor()

    # Get the count of internships and jobs
    cur.execute("SELECT COUNT(*) FROM listings WHERE category = 'internship'")
    num_internships = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM listings WHERE category = 'job'")
    num_jobs = cur.fetchone()[0]

    # Get the count of CV submissions
    cur.execute("SELECT COUNT(*) FROM submit")
    num_cv_submissions = cur.fetchone()[0]

    # Get the count of users
    cur.execute("SELECT COUNT(*) FROM users")
    num_users = cur.fetchone()[0]

    cur.close()

    # Fetch all CV submissions from the 'submit' table
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM submit")
    all_cv_submissions = cur.fetchall()
    cur.close()

    # Count the number of submissions for each company using Counter
    company_counts = Counter(submission[1] for submission in all_cv_submissions)

    # Get the top 5 companies with the most CV submissions
    num_companies = 5
    recommended_companies = company_counts.most_common(num_companies)

    return render_template('admin1.html', num_internships=num_internships, num_jobs=num_jobs, num_cv_submissions=num_cv_submissions, num_users=num_users, recommended_companies=recommended_companies)


@app.route('/delete/listing<int:id>', methods=['POST'])
def delete_listing(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM listings WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('company'))


@app.route('/delete/submission<int:id>', methods=['POST'])
def delete_submission(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM submit WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('company'))


@app.route('/jobs', methods=['GET', 'POST'])
@login_required
def job_list():
    if request.method == "POST":
        # Get form data
        
        companyName = request.form['companyname']
        Category = request.form['category']
        Role = request.form['role']
        

        # Get the uploaded file data
        cv = request.files['cv']  # Get the FileStorage object

        # Save the file to the specified folder
        filename = secure_filename(cv.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        cv.save(file_path)

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO submit (companyname, category, role, cv) VALUES (%s, %s, %s, %s)",
                    (companyName, Category, Role, filename))
        mysql.connection.commit()
        cur.close()

        flash('Resume submitted successfully!', 'success')

        return redirect(url_for('job_list'))

    # Fetch all data related to job listings, internship listings, and all listings
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM listings WHERE category = 'job'")
    job_listings = cur.fetchall()
    cur.execute("SELECT * FROM listings WHERE category = 'internship'")
    internship_listings = cur.fetchall()
    cur.execute("SELECT * FROM listings")
    listings = cur.fetchall()
    cur.close()

    return render_template('job.html', job_listings=job_listings, internship_listings=internship_listings, listings=listings)


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route('/search', methods=['POST'])
def search():
    search_input = request.form['search_input']

    # Query the database for job listings that match the search input
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM listings WHERE companyname LIKE %s OR role LIKE %s OR category LIKE %s OR location LIKE %s",
                (f"%{search_input}%", f"%{search_input}%", f"%{search_input}%", f"%{search_input}%"))
    job_listings = cur.fetchall()
    cur.close()

    # Convert the job listings data into a list of dictionaries
    job_listings_data = []
    for job in job_listings:
        job_data = {
            'id': job[0],
            'companyname': job[1],
            'role': job[2],
            'location': job[3],
            'category': job[4]
        }
        job_listings_data.append(job_data)

    # Return the job listings data as JSON
    return jsonify(job_listings_data)



if __name__ == "__main__":
   

