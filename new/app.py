from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import datetime

with open('config.json', 'r') as c:
    params = json.load(c)["params"]

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'my-thisissecret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://postgres:7659939242@localhost/loan_management"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class tb_customer_detail(db.Model):
    __tablename__ = 'tb_customer_detail'
    customer_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    employer = db.Column(db.String(50), nullable=False)
    birthdate = db.Column(db.DateTime, nullable=False)
    email = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(50), nullable=False)

    def __init__(self, first_name, last_name, employer, birthdate, email, phone
                 ):
        self.first_name = first_name
        self.last_name = last_name
        self.employer = employer
        self.birthdate = birthdate
        self.email = email
        self.phone = phone


class tb_loan_application(db.Model):
    __tablename__ = 'tb_loan_application'
    application_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('tb_customer_detail.customer_id', ondelete="CASCADE"),
                            nullable=False)
    product_id = db.Column(db.Integer, nullable=True)
    amount_applied = db.Column(db.Integer, nullable=False)
    duration_applied = db.Column(db.Integer, nullable=False)
    submitted_on = db.Column(db.String(50), nullable=True)
    reviewed_by = db.Column(db.String(50), nullable=True)
    reviewed_on = db.Column(db.String(50), nullable=True)
    application_status = db.Column(db.String(10), nullable=True)
    interest_rate = db.Column(db.String(50), nullable=True)
    amount_approved = db.Column(db.String(50), nullable=True)
    duration_approved = db.Column(db.String(50), nullable=True)
    total_num_pymnt = db.Column(db.String(50), nullable=True)
    loan_status = db.Column(db.String(10), nullable=True)

    def __init__(self, customer_id, product_id, amount_applied, duration_applied, submitted_on,
                 reviewed_by, reviewed_on, application_status, interest_rate, amount_approved,
                 duration_approved, total_num_pymnt, loan_status
                 ):
        self.customer_id = customer_id
        self.product_id = product_id
        self.amount_applied = amount_applied
        self.duration_applied = duration_applied
        self.submitted_on = submitted_on
        self.reviewed_by = reviewed_by
        self.reviewed_on = reviewed_on
        self.application_status = application_status
        self.interest_rate = interest_rate
        self.amount_approved = amount_approved
        self.duration_approved = duration_approved
        self.total_num_pymnt = total_num_pymnt
        self.loan_status = loan_status


class tb_emergency_contact(db.Model):
    __tablename__ = 'tb_emergency_contact'
    emergency_contact_id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('tb_loan_application.application_id', ondelete="CASCADE"),
                               nullable=False)
    first_name = db.Column(db.String(10), nullable=False)
    last_name = db.Column(db.String(10), nullable=False)
    birthdate = db.Column(db.DateTime, nullable=False)
    phone = db.Column(db.String(12), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    address = db.Column(db.String(50), unique=True, nullable=False)


class tb_loan_pymt(db.Model):
    __tablename__ = 'tb_loan_pymt'
    payment_id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('tb_loan_application.application_id', ondelete="CASCADE"),
                               nullable=False)
    amount_due = db.Column(db.Integer, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    amount_paid = db.Column(db.Integer, nullable=True)
    date_paid = db.Column(db.DateTime, nullable=True)


db.create_all()
db.session.commit()


@app.route("/", methods=('GET', 'POST'))
def home():
    if request.method == 'POST':
        f_name = request.form['first_name']
        l_name = request.form['last_name']
        employer = request.form['employer']
        birthdate = request.form['birthdate']
        email = request.form['email']
        phone = request.form['phone']

        """
            These are lines below that allow us to add customers details
        """
        entry = tb_customer_detail(first_name=f_name, last_name=l_name, employer=employer,
                                   birthdate=birthdate, email=email, phone=phone)
        db.session.add(entry)
        db.session.commit()

        """
            These are the lines below that allow to add tb_loan_application
        """

        get_record = tb_customer_detail.query.all()
        customer_id_forign_key = get_record[-1].customer_id

        amount_applied = int(request.form['amount_applied'])
        duration_applied = int(request.form['duration_applied'])
        date = datetime.now()

        entry = tb_loan_application(customer_id=customer_id_forign_key, product_id=0, amount_applied=amount_applied,
                                    duration_applied=duration_applied, submitted_on=date,
                                    reviewed_by='None', reviewed_on='None', application_status='None',
                                    interest_rate='None', amount_approved='None', duration_approved='None',
                                    total_num_pymnt='None', loan_status='None')
        db.session.add(entry)
        db.session.commit()

        flash('Your application number is..')
        return redirect(url_for('home'))

    return render_template("home.html")


@app.route("/status", methods=['POST', 'GET'])
def status():
    answer = 'No Record'
    if request.method == 'POST':
        application_status = request.form.get('appstatus')
        app_status = tb_loan_application.query.filter_by(customer_id=int(application_status)).first()
        answer = app_status.application_status
    return render_template("status.html", answer=answer)


@app.route("/admin_login", methods=('GET', 'POST'))
def admin_login():
    if "user" in session and session["user"] == params['admin_username']:
        applications = tb_loan_application.query.all()
        customers = tb_customer_detail.query.all()
        return render_template("admin_panel.html", applications=applications, customers=customers)
    elif request.method == 'POST':
        admin_user = request.form['username']
        admin_pass = request.form['password']

        if admin_user == params['admin_username'] and admin_pass == params['admin_password']:
            flash('Login successfull !!')
            session["user"] = admin_user

            applications = tb_loan_application.query.all()
            customers = tb_customer_detail.query.all()
            return render_template('admin_panel.html', applications=applications, customers=customers)
        else:
            flash('Login failed !!')

    return render_template('admin_login.html')


@app.route("/logout")
def logout():
    session.pop("user")
    return redirect(url_for("admin_login"))


@app.route("/approve/<int:id>")
def approve(id):
    print("Approve", id)
    update_status = tb_loan_application.query.filter_by(customer_id=id).first()
    update_status.application_status = 'Approveed'
    db.session.commit()
    return redirect(url_for("admin_login"))


@app.route("/reject/<int:id>")
def reject(id):
    print("reject", id)
    update_status = tb_loan_application.query.filter_by(customer_id=id).first()
    update_status.application_status = 'Reject'
    db.session.commit()
    return redirect(url_for("admin_login"))


@app.route("/repayment/<int:id>")
def repayment(id):
    print("repayment", id)
    update_status = tb_loan_application.query.filter_by(customer_id=id).first()
    update_status.application_status = 'Repayment'
    db.session.commit()
    return redirect(url_for("admin_login"))


if __name__ == '__main__':
    app.run(debug=True)
