from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

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
    trash_logs = db.relationship("TrashLog", backref="user", lazy=True)

class TrashLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    material = db.Column(db.String(150))
    status = db.Column(db.String(20), default="Pendente")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

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
    return render_template("index.html")

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

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("trash_logs"))
        
        else:
            flash("E-mail ou senha incorretos", "danger")

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user
    return redirect(url_for("index"))

#-----------------------------------
# Listar Tarefas --- READ
#-----------------------------------

@app.route("/trash_logs", methods=["POST", "GET"])
@login_required
def trash_logs():
    trah_logs = TrashLog.query.filter_by(user_id=current_user.id).all()
    return render_template("trash_logs.html", trah_logs=trah_logs)

#-----------------------------------
# Adicionar Tarefas --- CREATE
#-----------------------------------

@app.route("/trash_register", methods=["GET", "POST"])
@login_required
def trash_register():
    if request.method == "POST":
        material = request.form.get("material")
        
        new_register = TrashLog(material=material, user_id=current_user.id)

        db.session.add(new_register)
        db.session.commit()

        flash("Tarefa adicionada com sucesso!", "success")
        return redirect(url_for("trash_logs"))
    return render_template("add_tasks.html")

#-----------------------------------
# Atualizar Status da Tarefa --- UPDATE
#-----------------------------------
@app.route("/update_log/<int:id>")
@login_required
def update_log(id):
    trash_log = TrashLog.query.get_or_404(id)

    if trash_log.user_id != current_user.id:
        flash("Acesso não autorizado - Esta não é a conta logada!", "danger")
        return redirect(url_for("trash_logs"))
    
    trash_log.status = "Concluída" if trash_log.status == "Pendente" else "Pendente"
    db.session.commit()
    return redirect(url_for("tasks"))

#-----------------------------------
# Deletar Tarefa --- DELETE
#-----------------------------------
@app.route("/delete_log/<int:id>")
@login_required
def delete_log(id):
    trash_log = TrashLog.query.get_or_404(id)

    if trash_log.user_id != current_user.id:
        flash("Acesso não autorizado - Esta não é a conta logada!", "danger")
        return redirect(url_for("tasks"))
    
    db.session.delete(trash_log)
    db.session.commit()
    flash("Tarefa excluída com sucesso!", "info")
    return redirect(url_for("tasks"))

#-----------------------------------
# CRIAR BANCO NA PRIMEIRA EXECUÇÃO
#-----------------------------------

if __name__ == "__main__":
    if not os.path.exists("database.db"):
        with app.app_context():
            db.create_all()
    app.run(debug=True)