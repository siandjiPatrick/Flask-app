from flask import Flask, render_template, url_for, redirect,request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
import os
from datetime import datetime


app = Flask(__name__,)


#################### Database Setting ##############################################
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secretkey'

db = SQLAlchemy(app)



# Configuration Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Utilisez votre serveur de messagerie
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'gcptestpatrick@gmail.com'  # Remplacez par votre adresse e-mail
app.config['MAIL_PASSWORD'] = 'xsng dest xvdv myvl'  # Remplacez par votre mot de passe d'application

mail = Mail(app)


#######################  Model(Table creation)  #########################################################
"""
class User(db.Model, UserMixin):
    __tables__ = "user"
   
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)

    password = db.Column(db.String(80), nullable=False)
"""

# -> Table User
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=True)
    lastname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telephone = db.Column(db.String(20), unique=True, nullable=True)
    description = db.Column(db.String(200), nullable=True)
    password = db.Column(db.String(80), nullable=False)
    create_date = db.Column(db.DateTime, default=datetime.utcnow)
    argent_de_poche = db.relationship('ArgentDePoche', backref='beneficiaire', lazy=True)
    depenses = db.relationship('Depenses', backref='responsible', lazy=True)
    epargnes = db.relationship('Epargne', backref='provenance', lazy=True)
    revenues = db.relationship('Revenues', backref='provenance', lazy=True)

    def get_id(self):
        return str(self.user_id)  # Assuming user_id is the primary key

# -> Table Revenue
class Revenues(db.Model):
    __tablename__ = 'revenues'
    revenue_id = db.Column(db.Integer, primary_key=True)
    montant = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    provenance_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    designation_id = db.Column(db.Integer, db.ForeignKey('designation.designation_id'), nullable=False)
    description = db.Column(db.String(200), nullable=True)

class Designation(db.Model):
    __tablename__ = 'designation'
    designation_id = db.Column(db.Integer, primary_key=True)
    designation_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    create_date = db.Column(db.DateTime, default=datetime.utcnow)
    depenses = db.relationship('Depenses', backref='designation', lazy=True)
    epargnes = db.relationship('Epargne', backref='designation', lazy=True)
    revenues = db.relationship('Revenues', backref='designation', lazy=True)


class ArgentDePoche(db.Model):
    __tablename__ = 'argent_de_poche'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(100), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    beneficiaire_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)


class Depenses(db.Model):
    __tablename__ = 'depenses'
    depenses_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    montant = db.Column(db.Float, nullable=False)
    depenses_categorie_id = db.Column(db.Integer, db.ForeignKey('depenses_categorie.depenses_categorie_id'), nullable=False)
    responsable_depenses = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    designation_id = db.Column(db.Integer, db.ForeignKey('designation.designation_id'), nullable=False)

class DepensesCategorie(db.Model):
    __tablename__ = 'depenses_categorie'
    depenses_categorie_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    depenses = db.relationship('Depenses', backref='categorie', lazy=True)



class EpargneCategorie(db.Model):
    __tablename__ = 'epargne_categorie'
    epargne_categorie_id = db.Column(db.Integer, primary_key=True)
    epargne_categorie_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    create_date = db.Column(db.DateTime, default=datetime.utcnow)
    epargnes = db.relationship('Epargne', backref='epargne_categorie', lazy=True)

class Epargne(db.Model):
    __tablename__ = 'epargne'
    epargne_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(7), nullable=False)  # Format: MM.YYYY
    epargne_categorie_id = db.Column(db.Integer, db.ForeignKey('epargne_categorie.epargne_categorie_id'), nullable=False)
    montant = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=True)
    provenance_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    designation_id = db.Column(db.Integer, db.ForeignKey('designation.designation_id'), nullable=False)

class BudgetCategorie(db.Model):
    __tablename__ = 'budget_categorie'
    budget_categorie_id = db.Column(db.Integer, primary_key=True)
    budget_categorie_name = db.Column(db.String(100), nullable=False)#, unique=True)
    description = db.Column(db.String(200), nullable=True)
    create_date = db.Column(db.DateTime, default=datetime.utcnow)
    budgets = db.relationship('Budget', backref='budget_categorie', lazy=True)

class Budget(db.Model):
    __tablename__ = 'budget'
    budget_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    budget_categorie_id = db.Column(db.Integer, db.ForeignKey('budget_categorie.budget_categorie_id'), nullable=False)
    montant = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=True)



#------------------------------------------------------------------------------------------------------------->
############# login system route ################

with app.app_context():
    db.create_all()
    #users = ["astrid","patrick", "admin"]
    if not User.query.filter_by(username='patrick').first() :
            user1 = User( username = "patrick",
                        lastname = "siandji",
                        email = "siandjipatrick@yahoo.fr",
                        telephone = "0176-16-37-08-76",
                        description = "",
                        password = generate_password_hash('1234', method='pbkdf2:sha256'))
            db.session.add(user1)
            #db.session.commit()
    if not User.query.filter_by(username='astrid').first() :
            user2 = User( username = "astrid",
                        lastname = "medom",
                        email = "astridmedom@yahoo.fr",
                        telephone = "0176-21-43-15-48",
                        description = "",
                        password = generate_password_hash('1234', method='pbkdf2:sha256'))
            db.session.add(user2)
            #db.session.commit()
    if not User.query.filter_by(username='admin').first() :      
            user3 = User( username = "admin",
                        lastname = "admin",
                        email = "gcptestpatrick@gmail.com",
                        telephone = "0176-25-45-36-78",
                        description = "",
                        password = generate_password_hash('admin', method='pbkdf2:sha256'))
            db.session.add(user3)

    if not BudgetCategorie.query.filter_by(budget_categorie_name='new').first() :      
            new_categorie = BudgetCategorie(
                            budget_categorie_name = 'new',
                            description = "",
                           )
            db.session.add(new_categorie)

    depense = Depenses(
                            
    montant = 25,
    depenses_categorie_id = 2,
    responsable_depenses = 3,
    description = "mes depenses",
    designation_id="loyer"
                           ) 
    db.session.add(depense)  
    db.session.commit()
    #user1 = User(username='astrid', password=generate_password_hash('1234', method='pbkdf2:sha256'))
            
    

    if not User.query.filter_by(username='patrick').first() :
        user1 = User(username='patrick', password=generate_password_hash('1234', method='pbkdf2:sha256'))
        db.session.add(user1)
        db.session.commit()
    
    users = User.query.all()
    print(users)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    #print(User.query.get(int(user_id)))
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('home.html', user=current_user)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        
        
        if user and check_password_hash(user.password, password):
          
            login_user(user)
            return redirect(url_for('home'))
        else:
            message = 'Invalid username or password'
            return render_template('login.html', user=current_user, msg=message)
    return render_template('login.html', user=current_user)

@app.route('/logout', )
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))



@app.route('/manage_users', methods=['GET', 'POST'])     
def manage_users():

    users = User.query.all()
    print(users[0].username)

    if request.method == 'POST':
        usr = request.form.get('username')
        password = generate_password_hash(request.form.get('password'), method='pbkdf2:sha256')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        telephone = request.form.get('Numero_telephone')
        description = request.form.get('description')
        

        #new_user = User(username=usr, password=password)

        new_user = User( username = usr,
                    lastname = lastname,
                    email = email,
                    telephone = telephone,
                    description = description,
                    password = password)
       

        if not User.query.filter_by(email=new_user.email).first() :
            db.session.add(new_user)
            db.session.commit()

           
            return redirect(url_for('home'))
        else:
       
           msg = Message('Bienvenue sur notre plateforme!', recipients=[new_user.username])
           msg.html = render_template('send_email.html', user=current_user)
           msg.sender='gcptestpatrick@gmail.com'
           #image_file = request.files['image_file']
          
           # Enregistrement du fichier temporaire sur le serveur
           #temp_image_path = f"/tmp/{image_file.filename}"
           
           #image_file.save(temp_image_path)

           #with app.open_resource(temp_image_path) as img:
           #     msg.attach("image.jpg", "image/jpeg", img.read())
           mail.send(msg)
           # Suppression du fichier temporaire
           #os.remove(temp_image_path)

           return redirect(url_for('send_email'))
    return render_template('manage_users.html', user=current_user)


########## Depenses Route #################
@app.route('/show_categorie_budget')
@login_required
def show_categorie_budget():

    categories = BudgetCategorie.query.all()

    return render_template('show_categorie_budget.html', user=current_user, categories = categories)

@app.route('/show_list_users')
@login_required
def show_list_users():

    all_users = User.query.all()
    return render_template('show_list_users.html', user=current_user, all_users=all_users)

@app.route('/show_budgets')
@login_required
def show_budgets():

    budgets = Budget.query.all()
    return render_template('show_budgets.html', user=current_user, budgets=budgets)

@app.route('/show_depenses')
@login_required
def show_depenses():

    depenses = Depenses.query.all()
    return render_template('show_depenses.html', user=current_user, depenses=depenses)

@app.route('/show_epargnes')
@login_required
def show_epargnes():

    epargnes = Epargne.query.all()
    return render_template('show_epargnes.html', user=current_user, epargnes=epargnes)

@app.route('/show_revenues')
@login_required
def show_revenues():

    revenues = Revenues.query.all()
    return render_template('show_revenues.html', user=current_user, revenues=revenues)


@app.route('/depenses_imprevues')
@login_required
def depenses_imprevues():
    return render_template('depenses_imprevues.html', user=current_user)

@app.route('/depenses_nourriture', methods=['GET', 'POST'])
@login_required
def depenses_nourriture():

    return render_template('depenses_nourriture.html', user=current_user)

@app.route('/dettes')
@login_required
def dettes():
    return render_template('dettes.html', user=current_user)

##########  Budgets Routes ##################

@app.route('/manage_budget', methods=['GET', 'POST'])
@login_required
def manage_budget():
    categories = BudgetCategorie.query.all()
    print(categories)
    
    if request.method == 'POST':
        date = request.form.get('date')
        montant = request.form.get('montant')
        date = datetime.strptime(date, "%Y-%m-%d")
        categorie = request.form.get('categorie_budget')
        
        description = ""
        #categorie='test'
        if request.form.get('categorie_budget') == "new":
            # create new budget categorie
            return redirect(url_for('manage_budget_categorie'))
        else:
            a = BudgetCategorie.query.filter_by(budget_categorie_name = categorie).first().budget_categorie_id
            print("hehooooooooooooooooooooo")
            print(a)
            new_budget = Budget( 
                                       
                                montant = montant,
                                description = description,
                                date=date,
                                budget_categorie_id=  a
            )
        

            db.session.add(new_budget)
            db.session.commit()
            return redirect(url_for('manage_budget'))
    return render_template('manage_budget.html', user=current_user, categories = categories)

###### Settig ####################

@app.route('/manage_depenses', methods=['GET', 'POST'])
@login_required
def manage_depenses():
    depenses = Depenses.query.all()
    all_users = User.query.all()
    depenses_categories = DepensesCategorie.query.all()
    designations = Designation.query.all()
    

    depenses_id = db.Column(db.Integer, primary_key=True)
   
  
    responsable_depenses = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    designation_id = db.Column(db.Integer, db.ForeignKey('designation.designation_id'), nullable=False)

    if request.method == 'POST':
        date = request.form.get('date')
        date = datetime.strptime(date, "%Y-%m-%d")
        montant = request.form.get('montant')
        depenses_categorie = request.form.get('depenses_categorie')
        montant = request.form.get('montant')
        responsable_depenses = request.form.get('responsable_depenses')
        designation = request.form.get('designation')
        description = request.form.get('description')
    

        print(depenses_categorie)
        print(montant)
        print(depenses_categorie)
        print(montant)
        print(responsable_depenses)
        print(designation)
        print(description)
                
        if request.form.get('categorie_budget') == "new":
            # create new budget categorie
            return redirect(url_for('manage_budget_categorie'))
        else:
            a = BudgetCategorie.query.filter_by(budget_categorie_name = categorie).first().budget_categorie_id
            print(a)
            new_budget = Budget( 
                                       
                                montant = montant,
                                description = description,
                                date=date,
                                budget_categorie_id=  a
            )
        

            db.session.add(new_budget)
            db.session.commit()
            return redirect(url_for('manage_budget'))
    return render_template('manage_budget.html', user=current_user, depenses = depenses)
ö
@app.route('/manage_budget_categorie', methods=['GET', 'POST'])
@login_required
def manage_budget_categorie():
    
    if request.method == 'POST':

        categorie = request.form.get('new_categorie')
        description = request.form.get('description')
        print(categorie)
 
        new_categorie = BudgetCategorie(
                            budget_categorie_name = categorie,
                            description = description,                      
                        )
    
        db.session.add(new_categorie)
        db.session.commit()
        return redirect(url_for('manage_budget_categorie'))
 
    return render_template('manage_budget_categorie.html', user=current_user)


@app.route('/manage_revenues', methods=['GET', 'POST'])
@login_required
def manage_revenues():
    
    if request.method == 'POST':

        categorie = request.form.get('new_categorie')
        description = request.form.get('description')
        print(categorie)
 
        new_categorie = BudgetCategorie(
                            budget_categorie_name = categorie,
                            description = description,                      
                        )
    
        db.session.add(new_categorie)
        db.session.commit()
        return redirect(url_for('manage_revenues'))
 
    return render_template('manage_revenues.html', user=current_user)


@app.route('/manage_designations', methods=['GET', 'POST'])
@login_required
def manage_designations():
    
    if request.method == 'POST':

        categorie = request.form.get('new_categorie')
        description = request.form.get('description')
        print(categorie)
 
        new_categorie = BudgetCategorie(
                            budget_categorie_name = categorie,
                            description = description,                      
                        )
    
        db.session.add(new_categorie)
        db.session.commit()
        return redirect(url_for('manage_designations'))
 
    return render_template('manage_designations.html', user=current_user)


@app.route('/manage_epargne', methods=['GET', 'POST'])
@login_required
def manage_epargne():
    
    if request.method == 'POST':

        categorie = request.form.get('new_categorie')
        description = request.form.get('description')
        print(categorie)
 
        new_categorie = BudgetCategorie(
                            budget_categorie_name = categorie,
                            description = description,                      
                        )
    
        db.session.add(new_categorie)
        db.session.commit()
        return redirect(url_for('manage_epargne'))
 
    return render_template('manage_epargne.html', user=current_user)

############################## Budget #########################################

@app.route('/budget_imprevues')
@login_required
def budget_imprevues():
    return render_template('budget_imprevues.html', user=current_user)

@app.route('/budget_nourriture', methods=['GET', 'POST'])
@login_required
def budget_nourriture():
    
    return render_template('budget_nourriture.html', user=current_user)

@app.route('/epargnes')
@login_required
def epargnes():
    return render_template('epargnes.html', user=current_user)

@app.route('/send_email', methods=['GET', 'POST'])
@login_required
def send_email():
    return render_template('send_email.html', user=current_user)


if __name__ == '__main__':
   

    app.run(debug=True, port=5555)