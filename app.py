from flask import Flask, render_template, url_for, redirect,request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
import os
from datetime import datetime
from dotenv import load_dotenv
from flask_migrate import Migrate


load_dotenv()
app = Flask(__name__,)



#################### Database Setting ##############################################
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS")
app.config['SECRET_KEY'] = os.getenv("APP_SECRET_KEY")

app.config['UPLOAD_FOLDER'] = os.getenv("UPLOAD_FOLDER") #'static/uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db = SQLAlchemy(app)

migrade = Migrate(app, db)



# Configuration Flask-Mail
app.config['MAIL_SERVER'] = os.getenv("MAIL_SERVER")  # Utilisez votre serveur de messagerie
app.config['MAIL_PORT'] =os.getenv("MAIL_PORT")
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")  # Remplacez par votre adresse e-mail
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")  # Remplacez par votre mot de passe d'application

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
    username = db.Column(db.String(50), nullable=False, unique=True)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telephone = db.Column(db.String(20), unique=True, nullable=True)
    password = db.Column(db.String(350), nullable=False)
    profile_picture = db.Column(db.String(120), nullable=True)
    create_date = db.Column(db.DateTime, default=datetime.now)
    description = db.Column(db.String(200), nullable=True)

    # relationship
    argent_de_poche = db.relationship('ArgentDePoche', backref='user', lazy=True)
    depenses = db.relationship('Depenses', backref='user', lazy=True)
    epargnes = db.relationship('Epargne', backref='user', lazy=True)
    revenues = db.relationship('Revenues', backref='user', lazy=True)

    def get_id(self):
        return str(self.user_id)  # Assuming user_id is the primary key
    
    def __repr__(self) -> str:
        return f"user: {self.username}"

# -> Table Revenue
class Revenues(db.Model):
    __tablename__ = 'revenues'
    id = db.Column(db.Integer, primary_key=True)
    designation_id = db.Column(db.Integer, db.ForeignKey('designation.id'), nullable=False) # foreign key
    montant = db.Column(db.Float, nullable=False)
    provenance_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False) # Foreign Key
    date = db.Column(db.DateTime, default=datetime.now)
    description = db.Column(db.String(200), nullable=True)

class Designation(db.Model):
    __tablename__ = 'designation'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    create_date = db.Column(db.DateTime, default=datetime.now)
    description = db.Column(db.String(200), nullable=True)

    #Relationship
    depenses = db.relationship('Depenses', backref='designation', lazy=True)
    epargnes = db.relationship('Epargne', backref='designation', lazy=True)
    revenues = db.relationship('Revenues', backref='designation', lazy=True)


class ArgentDePoche(db.Model):
    __tablename__ = 'argent_de_poche'
    id = db.Column(db.Integer, primary_key=True)
    beneficiaire_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    montant = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.now)
    description = db.Column(db.String(100), nullable=True)
    
    

class DepensesCategorie(db.Model):
    __tablename__ = 'depenses_categorie'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    # Relationship
    depenses = db.relationship('Depenses', backref='depenses_categorie', lazy=True)

class Depenses(db.Model):
    __tablename__ = 'depenses'
    id = db.Column(db.Integer, primary_key=True)
    designation_id = db.Column(db.Integer, db.ForeignKey('designation.id'), nullable=False)
    depenses_categorie_id = db.Column(db.Integer, db.ForeignKey('depenses_categorie.id'), nullable=False)
    montant = db.Column(db.Float, nullable=False)
    responsable_depenses = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.now)
    description = db.Column(db.String(200), nullable=True)

class EpargneCategorie(db.Model):
    __tablename__ = 'epargne_categorie'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    create_date = db.Column(db.DateTime, default=datetime.now)
    description = db.Column(db.String(200), nullable=True)

    # Relationship
    epargnes = db.relationship('Epargne', backref='epargne_categorie', lazy=True)

class Epargne(db.Model):
    __tablename__ = 'epargne'
    id = db.Column(db.Integer, primary_key=True)
    designation_id = db.Column(db.Integer, db.ForeignKey('designation.id'), nullable=False)
    provenance_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    epargne_categorie_id = db.Column(db.Integer, db.ForeignKey('epargne_categorie.id'), nullable=False)
    montant = db.Column(db.Float, nullable=False)
    date = db.Column(db.String(7), nullable=False)  # Format: MM.YYYY
    description = db.Column(db.String(200), nullable=True)
    
    

class BudgetCategorie(db.Model):
    __tablename__ = 'budget_categorie'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    create_date = db.Column(db.DateTime, default=datetime.now)
    description = db.Column(db.String(200), nullable=True)

    # relationship
    budgets = db.relationship('Budget', backref='budget_categorie', lazy=True)

class Budget(db.Model):
    __tablename__ = 'budget'
    id = db.Column(db.Integer, primary_key=True)
    budget_categorie_id = db.Column(db.Integer, db.ForeignKey('budget_categorie.id'), nullable=False)
    montant = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.now)
    description = db.Column(db.String(200), nullable=True)



#------------------------------------------------------------------------------------------------------------->
############# login system route ################
"""
users = [
    {

    }
]
with app.app_context():
    db.create_all()
    
    d = Budget.query.all()
    print(d)
    #users = ["astrid","patrick", "admin"]
    if not User.query.filter_by(username='patrick').first() :
            user1 = User( username = "patrick",
                        lastname = "siandji",
                        email = "siandjipatrick@yahoo.fr",
                        telephone = "0176-16-37-08-76",
                        description = "",
                        profile_picture="login_img.jpeg",
                        password = generate_password_hash(os.getenv("PATRICK_USER_PASSWORD"), method='pbkdf2:sha256'))
            db.session.add(user1)
            #db.session.commit()
    if not User.query.filter_by(username='astrid').first() :
            user2 = User( username = "astrid",
                        lastname = "medom",
                        email = "astridmedom@yahoo.fr",
                        telephone = "0176-21-43-15-48",
                        profile_picture="as_bild.png",
                        description = "",
                        password = generate_password_hash(os.getenv("ASTRID_USER_PASSWORD"), method='pbkdf2:sha256'))
            db.session.add(user2)
            #db.session.commit()
    if not User.query.filter_by(username='admin').first() :      
            user3 = User( username = "admin",
                        lastname = "admin",
                        email = os.getenv("MAIL_USERNAME"),
                        telephone = "0176-25-45-36-78",
                        profile_picture="",
                        description = "",
                        password = generate_password_hash(os.getenv("ADMIN_USER_PASSWORD"), method='pbkdf2:sha256'))
            db.session.add(user3)

    if not BudgetCategorie.query.filter_by(name='creer une nouvelle Categorie de Buget').first() :      
            new_categorie = BudgetCategorie(
                            name = 'creer une nouvelle Categorie de Buget',
                            description = "",
                           )
            db.session.add(new_categorie)

            designation = Designation(name="loyer")
            db.session.add(designation)

            depense_categorie = DepensesCategorie(name="depenses_fixes")
            depense_categorie2 = DepensesCategorie(name="depenses_nourriture")
            depense_categorie3 = DepensesCategorie(name="dettes")
            depense_categorie4 = DepensesCategorie(name="imprevues")
            db.session.add(depense_categorie)   
            db.session.add(depense_categorie2)
            db.session.add(depense_categorie3)
            db.session.add(depense_categorie4)

            depense = Depenses(           
            montant = 25,
            categorie = depense_categorie2,
            responsable = user1,
            description = "mes depenses",
            designation = designation
                                ) 
            db.session.add(depense)

            

            # epargne init

            epargne_categorie1 = EpargneCategorie(name = "FAH", description ="tontine fah")
            epargne_categorie2 = EpargneCategorie(name = "FI", description ="tontine allemagne patrick")
            db.session.add(epargne_categorie1)
            db.session.add(epargne_categorie2)

           
    db.session.commit()
    #user1 = User(username='astrid', password=generate_password_hash('1234', method='pbkdf2:sha256'))
            
    

    if not User.query.filter_by(username='patrick').first() :
        user1 = User(username='patrick', password=generate_password_hash('1234', method='pbkdf2:sha256'))
        db.session.add(user1)
        db.session.commit()
    
    users = User.query.all()
    print(users)
"""
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
        email = User.query.filter_by(email=username).first()
        print(f"meine email: {email}")
        
        if user and check_password_hash(user.password, password): 
          
            login_user(user)
            return redirect(url_for('home'))
        
        elif email and check_password_hash(email.password, password):
            
            login_user(email)
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
        profil_bild = request.files['profil_bild']
        #profil_bild_path = os.path.join('/tmp', str(profil_bild))
        #profil_bild.save(profil_bild_path)
      

        #new_user = User(username=usr, password=password)
        #if profil_bild:
        filename = secure_filename(profil_bild.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        profil_bild.save(file_path)
        
        new_user = User( username = usr,
                    lastname = lastname,
                    email = email,
                    telephone = telephone,
                    description = description,
                    password = password,
                    profile_picture=filename
                    )
       

        if not User.query.filter_by(email=new_user.email).first() :
            db.session.add(new_user)
            db.session.commit()

           
            return redirect(url_for('home'))
        else:
       
           msg = Message('Bienvenue sur notre plateforme!', recipients=[new_user.email])
           msg.html = render_template('send_email.html', user=current_user)
           msg.sender=os.getenv("MAIL_USERNAME")
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

@app.route('/show_categorie_depenses')
@login_required
def show_categorie_depenses():

    depenses_categories = DepensesCategorie.query.all()
    return render_template('show_categorie_depenses.html', user=current_user, depenses_categories=depenses_categories)

@app.route('/show_categorie_epargnes')
@login_required
def show_categorie_epargnes():

    epargnes_categories = EpargneCategorie.query.all()
    return render_template('show_categorie_epargnes.html', user=current_user, epargnes_categories=epargnes_categories)

@app.route('/show_list_users')
@login_required
def show_list_users():

    all_users = User.query.all()
    return render_template('show_list_users.html', user=current_user, all_users=all_users)

@app.route('/show_designations')
@login_required
def show_designations():

    designations = Designation.query.all()
    return render_template('show_designations.html', user=current_user, designations=designations)

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
        if request.form.get('categorie_budget') == "creer une nouvelle Categorie de Buget":
            # create new budget categorie
            return redirect(url_for('manage_budget_categorie'))
        else:
            a = BudgetCategorie.query.filter_by(name = categorie).first().budget_categorie_id
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
    designation_id = db.Column(db.Integer, db.ForeignKey('designation.id'), nullable=False)

    if request.method == 'POST':
        date = request.form.get('date')
        date = datetime.strptime(date, "%Y-%m-%d")
        montant = request.form.get('montant')
        depenses_categorie = request.form.get('depense_categorie')
        montant = request.form.get('montant')
        responsable_depenses = request.form.get('provenance')
        designation = request.form.get('designation')
        description = request.form.get('description')
    

        print(depenses_categorie)
        print(montant)

        print(montant)
        print(responsable_depenses)
        print(designation)
        print(description)
                
        # if request.form.get('categorie_budget') == "new":
        #     # create new budget categorie
        #     return redirect(url_for('manage_budget_categorie'))
        # else:
        #a= Depenses.query.filter_by(budget_categorie_name = categorie).first().budget_categorie_id
        #     print(a)
        new_depenses = Depenses(       
                    date = date,
                    montant = montant,
                    categorie = DepensesCategorie.query.filter_by(name=depenses_categorie).first(),
                    responsable = User.query.filter_by(lastname=responsable_depenses).first(),
                    designation = Designation.query.filter_by(name=designation).first(),
                    description = description
             )
        
   
        db.session.add(new_depenses)
        db.session.commit()
        return redirect(url_for('manage_depenses'))
    return render_template('manage_depenses.html', user=current_user, 
                           depenses_categories = depenses_categories, all_users= all_users,
                           designations=designations)

@app.route('/manage_budget_categorie', methods=['GET', 'POST'])
@login_required
def manage_budget_categorie():
    
    if request.method == 'POST':

        categorie = request.form.get('new_categorie')
        description = request.form.get('description')
        print(categorie)
 
        new_categorie = BudgetCategorie(
                            name = categorie,
                            description = description,                      
                        )
    
        db.session.add(new_categorie)
        db.session.commit()
        return redirect(url_for('manage_budget_categorie'))
 
    return render_template('manage_budget_categorie.html', user=current_user)


@app.route('/manage_revenues', methods=['GET', 'POST'])
@login_required
def manage_revenues():

    all_users = User.query.all()
    designations = Designation.query.all()
    print(designations)
    
    if request.method == 'POST':
        
        designation = request.form.get('designation')
        description = request.form.get('description')
        date = request.form.get('date')
        date = datetime.strptime(date, "%Y-%m-%d")
        montant = request.form.get('montant')
        provenance = request.form.get('provenance')
        
        
        new_revenues = Revenues(
                            designation = Designation.query.filter_by(name=designation).first(),
                            description = description,
                            date = date,
                            montant = montant,
                            provenance = User.query.filter_by(lastname=provenance).first()                    
                        )
    
        db.session.add(new_revenues)
        db.session.commit()
        return redirect(url_for('manage_revenues'))
 
    return render_template('manage_revenues.html', user=current_user, all_users=all_users, designations=designations)


@app.route('/manage_designations', methods=['GET', 'POST'])
@login_required
def manage_designations():
    
    if request.method == 'POST':

        designation_name = request.form.get('designation')
        description = request.form.get('description')
        
 
        new_designation = Designation(
                            name = designation_name,
                            description = description,                      
                        )
    
        db.session.add(new_designation)
        db.session.commit()
        return redirect(url_for('manage_designations'))
 
    return render_template('manage_designations.html', user=current_user)


@app.route('/manage_epargne', methods=['GET', 'POST'])
@login_required
def manage_epargnes():
    depenses = Depenses.query.all()
    all_users = User.query.all()
    epargne_categories = EpargneCategorie.query.all()
    designations = Designation.query.all()
    if request.method == 'POST':

        date = request.form.get('date')
        date = datetime.strptime(date, "%Y-%m-%d")
        epargne_categorie_id = request.form.get('epargne_categorie')
        montant = request.form.get('montant')
        provenance_id = request.form.get('provenance')
        designation_id = request.form.get('designation')
        description = request.form.get('description')
    
 
        new_epargne = Epargne(
                            date = date,
                            epargne_categorie_id = epargne_categorie_id,
                            montant = montant,
                            provenance_id = provenance_id,
                            designation_id = designation_id,
                            description = description                   
                        )
    
        db.session.add(new_epargne)
        db.session.commit()
        return redirect(url_for('manage_epargnes'))
 
    return render_template('manage_epargnes.html', user=current_user,
                            epargne_categories = epargne_categories, all_users= all_users,
                           designations=designations)

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

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == "POST":
        new_pass = request.form.get('new_password')
        confirm_pass = request.form.get('confirm_password')
        email = request.form.get('email')
        print(email)
        print(confirm_pass)
        print(new_pass)
        
        if new_pass == confirm_pass:
            print("passport correct")
            for usr in User.query.all():
                #print(usr.email)
                if usr.email == email:
                    reset_user = User.query.filter_by(email=email).first()   
                    print("email correct")
                    
                    reset_user.password = generate_password_hash(new_pass, method='pbkdf2:sha256')
                    print(reset_user.telephone)
                    #current_user.password = confirm_pass
                    db.session.commit()

        return redirect(url_for('login'))
    return render_template('reset_password.html', user=current_user)

@app.route('/reset_password_email', methods=['GET', 'POST'])
def reset_password_email():
    if request.method == "POST":
        email = request.form.get('email')
        print(email)
        msg = Message('Reset Password!', recipients=[email])
        msg.html = render_template('send_email.html')
        msg.sender=os.getenv("MAIL_USERNAME")
        mail.send(msg)
        return redirect(url_for('login'))
    return render_template('reset_password_email.html', user=current_user)

if __name__ == '__main__':
   
   
    app.run(debug=True, port=5555)
