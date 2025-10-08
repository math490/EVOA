from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import date

#-----------------------------------
# CONFIGURAÇÃO INICIAL
#-----------------------------------

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(24)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

#-----------------------------------
# MODELS
#-----------------------------------

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True, nullable=True)
    password = db.Column(db.String(20), nullable=False)
    cash = db.Column(db.Float, default=0.0)
    xp = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)

    trash_logs = db.relationship(
        "TrashLog",
        backref="user",
        lazy=True,
        cascade="all, delete"
    )

    def add_xp(self, amount):
        self.xp += amount
        self.update_level()

    def add_cash(self, amount):
        self.cash += amount

    def update_level(self):
        self.level = (self.xp // 100) + 1

class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    default_weight = db.Column(db.Float, nullable=False)     # Peso padrão (ex: 1kg)

    trash_logs = db.relationship(
        "TrashLog",
        backref="material_ref",
        lazy=True,
        cascade="all, delete"
    )

class TrashLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.Integer, db.ForeignKey("material.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    weight = db.Column(db.Float, default=1.0)
    date = db.Column(db.Date, default=date.today)
    cash_earned = db.Column(db.Float, default=0.0)
    xp_earned = db.Column(db.Integer, default=0)

#-----------------------------------
# LOGIN MANAGER
#-----------------------------------

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#-----------------------------------
# ROTAS
#-----------------------------------

@app.route("/")
def index():
    ano = get_ano_atual()
    return render_template("index.html", ano=ano)

def get_ano_atual():
    return date.today().year

#-----------------------------------
# Cadastro de Material --- CREATE
#-----------------------------------

@app.route("/material_register", methods=["GET", "POST"])
@login_required
def material_register():
    if request.method == "POST":
        name = request.form.get("name")
        default_weight = float(request.form.get("default_weight"))

        # Verifica se já existe material com esse nome
        if Material.query.filter_by(name=name).first():
            flash("Material já cadastrado!", "warning")
            return redirect(url_for("material_register"))

        new_material = Material(
            name=name,
            default_weight=default_weight
        )
        db.session.add(new_material)
        db.session.commit()
        flash("Material cadastrado com sucesso!", "success")
        return redirect(url_for("index"))

    ano = get_ano_atual()
    return render_template("material_register.html", ano=ano)

#-----------------------------------
# Cadastro de Usuário --- CREATE
#-----------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = generate_password_hash(request.form.get("password"))

        # Verificar se já existe
        user = User.query.filter_by(email=email).first()

        if user:
            flash("E-mail já cadastrado!", "warning")
            return redirect(url_for("register"))
        
        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        
        flash("Cadastro realizado com sucesso! (Faça Login)", "success")
        return redirect(url_for("login"))

    ano = get_ano_atual()
    return render_template("register.html", ano=ano)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("index"))
        
        else:
            flash("E-mail ou senha incorretos", "danger")

    ano = get_ano_atual()
    return render_template("login.html", ano=ano)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

#-----------------------------------
# Adicionar Reciclagem --- CREATE
#-----------------------------------

@app.route("/trash_register", methods=["GET", "POST"])
@login_required
def trash_register():
    if request.method == "POST":
        material_name = request.form.get("material")
        weight = float(request.form.get("weight"))

        material = Material.query.filter_by(name=material_name).first()
        if not material:
            flash("Material não encontrado!", "danger")
            return redirect(url_for("trash_register"))

        cash_per_kg = 10 / material.default_weight
        cash = cash_per_kg * weight

        today = date.today()
        logs_today = TrashLog.query.filter_by(user_id=current_user.id, date=today).count()
        xp = 30 + (logs_today * 20)

        new_register = TrashLog(
            material_id=material.id,
            user_id=current_user.id,
            weight=weight,
            date=today,
            cash_earned=cash,
            xp_earned=xp
        )
        db.session.add(new_register)
        current_user.add_xp(int(xp))
        current_user.add_cash(cash)
        db.session.commit()

        flash(f"Log adicionado! Você ganhou {int(xp)} XP e {cash:.2f} cash!", "success")
        return redirect(url_for("trash_logs"))

    materials = Material.query.all()
    default_weight = materials[0].default_weight if materials else 0.001
    ano = get_ano_atual()
    return render_template("trash_register.html", materials=materials, default_weight=default_weight, ano=ano)

#-----------------------------------
# Listar Reciclagem --- READ
#-----------------------------------

@app.route("/trash_logs")
@login_required
def trash_logs():
    logs = TrashLog.query.filter_by(user_id=current_user.id).order_by(TrashLog.date.desc()).all()
    ano = get_ano_atual()
    return render_template("trash_logs.html", trash_logs=logs, ano=ano)

#-----------------------------------
# Listar Materiais --- READ
#-----------------------------------

@app.route("/materials")
@login_required
def materials():
    materials = Material.query.all()
    ano = get_ano_atual()
    return render_template("materials.html", materials=materials, ano=ano)

#-----------------------------------
# Perfil do Usuário --- READ
#-----------------------------------

@app.route("/profile")
@login_required
def profile():
    ano = get_ano_atual()
    return render_template("profile.html", user=current_user, ano=ano)

#-----------------------------------
# Listar Usuários --- READ
#-----------------------------------

@app.route("/users")
@login_required
def users():
    users = User.query.all()
    ano = get_ano_atual()
    return render_template("users.html", users=users, ano=ano)

#-----------------------------------
# Atualizar Material --- UPDATE
#-----------------------------------

@app.route("/edit_material/<int:id>", methods=["GET", "POST"])
@login_required
def edit_material(id):
    material = Material.query.get_or_404(id)
    if request.method == "POST":
        material.name = request.form.get("name")
        material.default_weight = float(request.form.get("default_weight"))
        db.session.commit()
        flash("Material atualizado com sucesso!", "success")
        return redirect(url_for("materials"))
    ano = get_ano_atual()
    return render_template("edit_material.html", material=material, ano=ano)

#-----------------------------------
# Atualizar Usuário --- UPDATE
#-----------------------------------

@app.route("/edit_user/<int:id>", methods=["GET", "POST"])
@login_required
def edit_user(id):
    user = User.query.get_or_404(id)
    if request.method == "POST":
        user.name = request.form.get("name")
        user.email = request.form.get("email")
        # Atualização de senha apenas se fornecida
        password = request.form.get("password")
        if password:
            user.password = generate_password_hash(password)
        db.session.commit()
        flash("Usuário atualizado com sucesso!", "success")
        return redirect(url_for("users"))
    ano = get_ano_atual()
    return render_template("edit_user.html", user=user, ano=ano)

#-----------------------------------
# Deletar Reciclagem --- DELETE
#-----------------------------------

@app.route("/delete_log/<int:id>")
@login_required
def delete_log(id):
    trash_log = TrashLog.query.get_or_404(id)

    if trash_log.user_id != current_user.id:
        flash("Acesso não autorizado - Esta não é a conta logada!", "danger")
        return redirect(url_for("trash_logs"))
    
    db.session.delete(trash_log)
    db.session.commit()
    flash("Log excluído com sucesso!", "info")
    return redirect(url_for("trash_logs"))

#-----------------------------------
# Deletar Material --- DELETE
#-----------------------------------

@app.route("/delete_material/<int:id>")
@login_required
def delete_material(id):
    material = Material.query.get_or_404(id)
    db.session.delete(material)
    db.session.commit()
    flash("Material excluído com sucesso!", "info")
    return redirect(url_for("materials"))

#-----------------------------------
# Deletar Usuário --- DELETE
#-----------------------------------

@app.route("/delete_user/<int:id>", methods=["POST"])
@login_required
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash("Usuário deletado com sucesso!", "info")
    return redirect(url_for("users"))

#-----------------------------------
# CRIAR BANCO NA PRIMEIRA EXECUÇÃO
#-----------------------------------

if __name__ == "__main__":
    if not os.path.exists("database.db"):
        with app.app_context():
            db.create_all()
    app.run(debug=True)