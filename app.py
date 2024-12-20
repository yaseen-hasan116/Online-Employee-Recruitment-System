import smtplib
import sqlite3

import pandas as pd
from flask import Flask, render_template, request

username=None
admin=False
login_user=False
req=False
email=None
def connect_db():
    conn = sqlite3.connect('Database.db', check_same_thread=False)
    return conn 
def mail(to):
    global username
    ob=smtplib.SMTP("smtp.gmail.com",587)
    ob.starttls()
    ob.login("psoul7716@gmail.com","Puresoul@1")   # please mention you email and password here
    subject="Thank you for Applying to Our Company!"
    body=f"Dear Applicant,\n\nI hope this email finds you well. I am writing to express our gratitude for your recent application. We appreciate the time and effort you have invested in considering us as a potential employer.\n\nWishing you the best of luck in your job search, and we hope to be in touch soon!\n\nBest regards,\njob Seekers Team"
    mes="subject:{}\n\n{}".format(subject,body)
    print(mes)
    listofadd=[to]
    ob.sendmail("psoul7716@gmail.com",listofadd,mes)
    ob.quit()
app = Flask(__name__)
@app.route("/")
def base():
    global username,login_user,admin,req
    if admin:
        return render_template("admin.html",username=username)
    elif login_user:
        return render_template("base.html",username=username)
    elif req:
        return render_template("req.html",username=username)
    else:
        return render_template("discover.html")
@app.route("/discover")
def discover():
    global username,login_user,admin,req
    return render_template ("discover.html",username=username,profile=login_user,admin=admin,req=req)    
@app.route("/logout")
def logout():
    global login_user,admin,req,email
    login_user=False
    admin=False
    req=False
    email=None
    return render_template("discover.html")
@app.route("/profile")
def profile():
    global username,login_user,admin,req
    name = username.replace(" ", "")
    conn=connect_db()
    cursor=conn.cursor()
    cursor.execute("SELECT education_1, education_2, Experience_1, Experience_2, Bio,Job_Applications FROM user_details WHERE Username = ?", (name,))
    result=cursor.fetchone()
    print(username)
    print(result)
    if result:
        education1, education2, experience1, experience2, bio,Job_Applications = result
        return render_template("profile.html",username=username,admin=admin,profile=login_user,req=req,education1=education1,education2=education2,experience1=experience1,experience2=experience2,bio=bio,job=Job_Applications)
    else:
        return render_template("profile.html",username= username,admin=admin,req=req,profile=login_user,job="Not Applied Yet")
@app.route("/save-profile",methods=["GET","POST"])
def save_profile():
    global username,login_user,admin,req
    conn=connect_db()
    cursor=conn.cursor()
    username = request.form.get('username')
    education1 = request.form.get('education-1')
    education2 = request.form.get('education-2')
    experience1 = request.form.get('experience-1')
    experience2 = request.form.get('experience-2')
    bio = request.form.get('bio')
    profile_photo = request.files.get('profile-photo-upload')
    profile_photo_path = ''
    if profile_photo:
        # Save the profile photo to a desired location
        # For example, you can save it in the "static" folder
        profile_photo_path = f"static/profiles/{profile_photo.filename}"
        profile_photo.save(profile_photo_path)
    cursor.execute("INSERT INTO user_details(Username,profile_photo,education_1,education_2,Experience_1,Experience_2,Bio)VALUES(?,?,?,?,?,?,?)",(username,profile_photo_path,education1,education2,experience1,experience2,bio))
    conn.commit()
    return render_template("profile.html",username=username,admin=admin,req=req,education1=education1,education2=education2,experience1=experience1,experience2=experience2,bio=bio,profile_photo=profile_photo_path)
@app.route("/login",methods=["GET","POST"])
def login():
    global username,login_user,admin,req,email
    if request.method=="POST":
        email=request.form['email']
        passw=request.form['password']
        conn=connect_db()
        cursor=conn.cursor()
        cursor.execute("SELECT Ac_type,Username,email FROM login WHERE email = ? AND Password = ?", (email, passw))
        record = cursor.fetchone() 
        if record:
            if record[0] =="Admin":
                admin=True
                login_user=False
                req=False
                username=record[1]
                email=record[2]
                return render_template('dashboard.html',admin=admin,username=username,profile=login_user,req=req)
            elif record[0]=="Recruiter account":
                admin=False
                login_user=False
                req=True
                username=record[1]
                email=record[2]
                return render_template('req.html',admin=admin,username=username,profile=login_user,req=req)
                
            else:
                login_user=True
                admin=False
                username=record[1]
                email=record[2]
                return render_template("discover.html",username=username,profile=login_user,admin=admin,req=req)
        else :
            return render_template('login_page.html',msg="Invalid Credentials",profile=login_user)
    return render_template("login_page.html",username=username,profile=login_user,req=req,admin=admin)
@app.route("/newuser",methods=["GET","POST"])
def newuser():
    global username,login_user,admin,req
    if request.method=="POST":
        print("reached")
        username=request.form['username'] 
        password=request.form['password']
        email=request.form['email']
        ac_type=request.form['account-type']
        conn=connect_db()
        cursor=conn.cursor()
        cursor.execute("SELECT Username From login WHERE Username=?",(username,))
        record=cursor.fetchone()
        if record:
            return render_template("newuser.html",msg1="Username Already Exists !",username=username,admin=admin,profile=login_user,req=req)
        else:
            # Inserting the values into the database
            cursor.execute("INSERT INTO login(Username, Password, email , Ac_type) VALUES (?, ?, ?, ?)",(username, password, email ,ac_type))
            conn.commit()
            return render_template("login_page.html",username=username,admin=admin,req=req,profile=login_user)
    return render_template("newuser.html",username=username,profile=login_user,admin=admin,req=req)
@app.route("/dashboard")
def dashboard():
    global username
    return render_template("dashboard.html",username=username)
@app.route("/new_job",methods=["GET","POST"])
def new_job():
    global username
    if request.method=="POST":
        conn=connect_db()
        cursor=conn.cursor()
        company_name = request.form['company_name']
        job_title = request.form['job-title']
        job_description = request.form['job-description']
        job_requirements = request.form['job-requirements']
        employment_type = request.form['employment-type']
        job_field=request.form['job-field']
        location = request.form['location']
        compensation = request.form['compensation']
        application_deadline = request.form['application-deadline']
        contact_info = request.form['contact-info']
        cursor.execute('''INSERT INTO job_postings
                    (CompanyName, job_title, job_description, job_requirements,
                    employment_type,job_field, location, compensation, application_deadline, contact_info)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?,?)''',
                   (company_name, job_title, job_description, job_requirements,
                    employment_type,job_field, location, compensation, application_deadline, contact_info))
        conn.commit()
        return render_template("job_posting_form.html",msg="New Job Posted successfully!",username=username)
    return render_template("job_posting_form.html",username=username)
@app.route("/job_postings")
def jobs():
    global username,login_user,admin,req
    conn=connect_db()
    cursor=conn.cursor()
    cursor.execute("SELECT CompanyName,job_title,job_description,job_requirements,employment_type,location,compensation,application_deadline,contact_info fROM job_postings")
    results = cursor.fetchall()
    df = pd.DataFrame(results, columns=['CompanyName','job_title','job_description', 'job_requirements','employment_type','location','compensation','application_deadline','contact_info'])
    company_name = df['CompanyName'].tolist()
    job_title = df['job_title'].tolist()
    job_description = df['job_description'].tolist()
    job_requirements = df['job_requirements'].tolist()
    employment_type = df['employment_type'].tolist()
    location = df['location'].tolist()
    compensation = df['compensation'].tolist()
    application_deadline = df['application_deadline'].tolist()
    contact_info = df['contact_info'].tolist()
    return render_template("job_postings.html",company_name=company_name,job_title=job_title,job_description=job_description,job_requirements=job_requirements,employment_type=employment_type,location=location,compensation=compensation,application_deadline=application_deadline,contact_info=contact_info,username=username,profile=login_user,admin=admin,req=req)
@app.route("/apply",methods=["GET","POST"])
def apply():
    global username,login_user,admin,req,email
    conn=connect_db()
    cursor=conn.cursor()
    if request.method=="POST":
        name=request.form['username']
        full_name = request.form['full-name']
        email = request.form['email']
        phone = request.form['phone']
        resume = request.files['resume'].read()  # Read the binary data of the file
        cover_letter = request.form['cover-letter']
        references = request.form['references']
        portfolio = request.form['portfolio']
        certifications = request.form['certifications']
        cursor.execute('''INSERT INTO job_applications (username, full_name, email, phone, resume, cover_letter, references1, portfolio, certifications)VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', (name,full_name, email, phone, resume, cover_letter, references, portfolio, certifications))
        cursor.execute("UPDATE user_details SET Job_Applications = 'Pending' WHERE email = ?",(email,))
        conn.commit()
        #mail(email)
        return render_template("job_application_form.html",username=username,profile=login_user,req=req,admin=admin,msg="Job application submitted successfully!")
    return render_template("job_application_form.html",username=username,profile=login_user,req=req,admin=admin,email=email)

@app.route("/delete/<string:company_name>/<string:job_title>")
def delete(company_name,job_title):
    global username,login_user,admin,req
    conn=connect_db()
    cursor=conn.cursor()
    cursor.execute("DELETE FROM job_postings WHERE  CompanyName = ? AND job_title=? ",(company_name,job_title))
    conn.commit()
    return render_template ("job_postings.html",username=username,profile=login_user,admin=admin,req=req)
@app.route("/applications")
def applications():
    global username, login_user, admin ,req
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT full_name, email, phone,cover_letter, references1, portfolio, certifications FROM job_applications")
    results = cursor.fetchall()
    df = pd.DataFrame(results, columns=['full_name', 'email', 'phone', 'cover_letter', 'references1', 'portfolio', 'certifications'])
    Full_name = df['full_name'].tolist()
    Email = df["email"].tolist()
    Phone = df["phone"].tolist()
    cover_letter = df['cover_letter'].tolist()
    reference1 = df['references1'].tolist()
    portfolio = df['portfolio'].tolist()
    certifications = df['certifications'].tolist()
    # Convert resume from binary to text
     
    return render_template("applicants.html",name=Full_name,email=Email,phone=Phone,cover_letter=cover_letter,reference1=reference1,portfolio=portfolio,certifications=certifications,username=username,profile=login_user,admin=admin,req=req)
@app.route("/accept/<string:email>")
def accecpt(email):
    print(email)
    global username,admin,req,login_user
    pro="Selected"
    conn=connect_db()
    cursor=conn.cursor()
    cursor.execute("UPDATE user_details SET Job_Applications =? WHERE email =?",(pro,email))
    conn.commit()
    
    return render_template ("req.html",admin=admin,profile=login_user,req=req,username=username)
@app.route("/decline/<string:email>")
def decline(email):
    print(email)
    global username,admin,req
    pro="Decline ! Try For Another Job"
    conn=connect_db()
    cursor=conn.cursor()
    cursor.execute("UPDATE user_details SET Job_Applications =? WHERE email =?",(pro,email))  
    conn.commit()  
    return render_template ("req.html",admin=admin,req=req,username=username)
@app.route("/computer_science",methods=['GET','POST'])
def Computer():
    global username,login_user,admin,req
    conn=connect_db()
    cursor=conn.cursor()
    cursor.execute("SELECT CompanyName, job_title, job_description, job_requirements, employment_type, location, compensation, application_deadline, contact_info FROM job_postings WHERE job_field='Computer science'")
    results = cursor.fetchall()
    if results:
        df = pd.DataFrame(results, columns=['CompanyName','job_title','job_description', 'job_requirements','employment_type','location','compensation','application_deadline','contact_info'])
        company_name = df['CompanyName'].tolist()
        job_title=df['job_title'].tolist()
        job_description = df['job_description'].tolist()
        job_requirements = df['job_requirements'].tolist()
        employment_type = df['employment_type'].tolist()
        location = df['location'].tolist()
        compensation = df['compensation'].tolist()
        application_deadline = df['application_deadline'].tolist()
        contact_info = df['contact_info'].tolist()
        return render_template("search.html",req=req,company_name=company_name,job_title=job_title,job_description=job_description,job_requirements=job_requirements,employment_type=employment_type,location=location,compensation=compensation,application_deadline=application_deadline,contact_info=contact_info,username=username,profile=login_user,admin=admin)

@app.route("/Civil",methods=['GET','POST'])
def Civil():
    global username,login_user,admin,req
    conn=connect_db()
    cursor=conn.cursor()
    cursor.execute("SELECT CompanyName, job_title, job_description, job_requirements, employment_type, location, compensation, application_deadline, contact_info FROM job_postings WHERE job_field='Civil'")
    results = cursor.fetchall()
    if results:
        df = pd.DataFrame(results, columns=['CompanyName','job_title','job_description', 'job_requirements','employment_type','location','compensation','application_deadline','contact_info'])
        company_name = df['CompanyName'].tolist()
        job_title=df['job_title'].tolist()
        job_description = df['job_description'].tolist()
        job_requirements = df['job_requirements'].tolist()
        employment_type = df['employment_type'].tolist()
        location = df['location'].tolist()
        compensation = df['compensation'].tolist()
        application_deadline = df['application_deadline'].tolist()
        contact_info = df['contact_info'].tolist()
        return render_template("search.html",req=req,company_name=company_name,job_title=job_title,job_description=job_description,job_requirements=job_requirements,employment_type=employment_type,location=location,compensation=compensation,application_deadline=application_deadline,contact_info=contact_info,username=username,profile=login_user,admin=admin)

@app.route("/Electrical",methods=['GET','POST'])
def Electrical():
    global username,login_user,admin,req
    conn=connect_db()
    cursor=conn.cursor()
    cursor.execute("SELECT CompanyName, job_title, job_description, job_requirements, employment_type, location, compensation, application_deadline, contact_info FROM job_postings WHERE job_field='Electrical'")
    results = cursor.fetchall()
    if results:
        df = pd.DataFrame(results, columns=['CompanyName','job_title','job_description', 'job_requirements','employment_type','location','compensation','application_deadline','contact_info'])
        company_name = df['CompanyName'].tolist()
        job_title=df['job_title'].tolist()
        job_description = df['job_description'].tolist()
        job_requirements = df['job_requirements'].tolist()
        employment_type = df['employment_type'].tolist()
        location = df['location'].tolist()
        compensation = df['compensation'].tolist()
        application_deadline = df['application_deadline'].tolist()
        contact_info = df['contact_info'].tolist()
        return render_template("search.html",req=req,company_name=company_name,job_title=job_title,job_description=job_description,job_requirements=job_requirements,employment_type=employment_type,location=location,compensation=compensation,application_deadline=application_deadline,contact_info=contact_info,username=username,profile=login_user,admin=admin)
     
@app.route("/Mechanical",methods=['GET','POST'])
def Mechanical():
    global username,login_user,admin,req
    conn=connect_db()
    cursor=conn.cursor()
    cursor.execute("SELECT CompanyName, job_title, job_description, job_requirements, employment_type, location, compensation, application_deadline, contact_info FROM job_postings WHERE job_field='Mechanical'")
    results = cursor.fetchall()
    if results:
        df = pd.DataFrame(results, columns=['CompanyName','job_title','job_description', 'job_requirements','employment_type','location','compensation','application_deadline','contact_info'])
        company_name = df['CompanyName'].tolist()
        job_title=df['job_title'].tolist()
        job_description = df['job_description'].tolist()
        job_requirements = df['job_requirements'].tolist()
        employment_type = df['employment_type'].tolist()
        location = df['location'].tolist()
        compensation = df['compensation'].tolist()
        application_deadline = df['application_deadline'].tolist()
        contact_info = df['contact_info'].tolist()
        return render_template("search.html",req=req,company_name=company_name,job_title=job_title,job_description=job_description,job_requirements=job_requirements,employment_type=employment_type,location=location,compensation=compensation,application_deadline=application_deadline,contact_info=contact_info,username=username,profile=login_user,admin=admin)
@app.route("/accouts", methods=['GET', 'POST'])
def accounts():
    global username,login_user,admin,req
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT Username, Password, email FROM login")
    results = cursor.fetchall()
    df = pd.DataFrame(results, columns=['Username', 'Password', 'Email'])
    
    # Close the database connection
    conn.close()
    
    # Convert DataFrame columns into lists
    username_list = df['Username'].tolist()
    password_list = df['Password'].tolist()
    email_list = df['Email'].tolist() 
    return render_template("table.html", admin=admin, login_user=login_user, username=username, username_list=username_list, password_list=password_list, email_list=email_list)

@app.route("/dele/<string:user>")
def delete_ac(user):
    global username,login,admin,login_user,req
    conn=connect_db()
    cursor=conn.cursor()
    cursor.execute("DELETE FROM login WHERE Username=?",(user,)) 
    conn.commit()
    return render_template("dashboard.html",admin=admin,username=username,login_user=login_user,req=req)    

if __name__ == '__main__':
    app.run(debug=True)