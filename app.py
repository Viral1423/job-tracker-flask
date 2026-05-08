from flask import Flask, request , redirect , render_template , url_for ,flash ,session
import bcrypt
from flask_sqlalchemy import SQLAlchemy
import os



app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:Veer4220H@localhost:5432/jobtracker'
app.config['SQLALCHEMY_DATABASE_URI']=os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.secret_key = os.environ.get("Veer4220H")


db = SQLAlchemy(app)
class User(db.Model):
    id = db.Column(db.Integer , primary_key =True)
    username = db.Column(db.String(100) ,unique = True , nullable = False )
    password = db.Column(db.LargeBinary , nullable = False)


class Job(db.Model):
    id = db.Column(db.Integer , primary_key = True) 
    company = db.Column(db.String(100), nullable= False)
    role = db.Column(db.String(100), nullable = False)
    status = db.Column(db.String(50), nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    created_at = db.Column(db.DateTime, server_default = db.func.current_timestamp())


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods =["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    user  = User.query.filter_by(username = username).first()
    if user:
        if bcrypt.checkpw(password.encode("utf-8"),user.password):
            session["username"] = username
            return redirect (url_for("dashboard"))
        else:
            flash("Wrong Password")
            return render_template("index.html")
        
    else:
        flash("Username Not Found")
        return render_template("index.html")
    
        


@app.route("/signup-pg")
def signup_pg():
    return render_template("signup.html")


@app.route("/signup", methods=["POST"])
def signup():
    sname = request.form["sname"]
    spass = request.form["spass"]
    hashed = bcrypt.hashpw(spass.encode(),bcrypt.gensalt())
    new_user =  User(username = sname , password = hashed)
    
    check_user = User.query.filter_by(username = sname).first()
    if check_user:
        flash ("username already exits")
        return redirect(url_for("home"))
    else:
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("home"))


@app.route("/add-job" , methods = ["POST"])
def add_job():
    if "username" not in session:
        return redirect(url_for("home"))
    username =session["username"]
    user = User.query.filter_by(username= username).first()
    company = request.form["company"]
    role = request.form["role"]
    status = request.form["status"]
    new_job = Job(company = company , role = role, status = status , user_id=user.id)
    db.session.add(new_job)
    db.session.commit()
    return redirect(url_for("dashboard"))


@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("home"))

    username = session["username"]
    user = User.query.filter_by(username = username).first()
    jobs = Job.query.filter_by(user_id = user.id)\
        .order_by(Job.created_at.desc()).all()
    return render_template("dashboard.html" , jobs = jobs , username = username ,total_jobs = len(jobs))

@app.route("/delete-job/<int:id>" , methods=["POST"])
def delete_job(id):
    if "username" not in session:
            return redirect(url_for("home"))
    username = session["username"]
    user = User.query.filter_by(username = username).first()
    job = db.session.get(Job,id)
    if job and job.user_id == user.id:
    # job = Job.query.get(id)
        db.session.delete(job)
        db.session.commit()
    return redirect(url_for("dashboard"))


@app.route("/update-job/<int:id>" , methods=["POST"])
def update_job(id):
    if "username" not in session:
        return redirect(url_for("home"))
    username = session["username"]
    user = User.query.filter_by(username =  username).first()
    job = db.session.get(Job,id)
    if job and job.user_id == user.id: 
        new_status = request.form["new_status"]
        job.status = new_status
        db.session.commit()
    return redirect(url_for("dashboard"))

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("home"))




if __name__ == "__main__":
    app.run(debug=True)