# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.exceptions import BadRequest
from flask_login import (
    LoginManager, UserMixin, login_user, login_required, logout_user, current_user
)
from flask_bcrypt import Bcrypt

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from bson import ObjectId

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from config import Config
from utils.logic import (
    load_df, who_is_going_to_leave, medical_scores, who_needs_training,
    leadership_list, skill_grouping, select_best_team, what_if_simulation
)

import os, sys
from urllib.parse import urlparse, urljoin

# ---------------------------
# App & Config
# ---------------------------
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-change-in-production")
app.config.from_object(Config)

# Security settings
app.config.update(
    SESSION_COOKIE_SECURE=False,  # Set to True in production with HTTPS
    REMEMBER_COOKIE_SECURE=False,  # Set to True in production with HTTPS
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_HTTPONLY=True,
    PERMANENT_SESSION_LIFETIME=3600,  # 1 hour session timeout
)

# ---------------------------
# Auth / DB Setup
# ---------------------------
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'error'
login_manager.session_protection = "strong"

mongo_client = MongoClient(app.config.get('MONGODB_URI'))
try:
    db = mongo_client.get_default_database()
except Exception:
    db = mongo_client['iaf_app']  # fallback if no DB name in URI
# ensure unique index on username
try:
    db.users.create_index('username', unique=True)
except Exception:
    pass

# users collection ensured via index above

# seed default admin if missing
try:
    if db.users.count_documents({'username': 'admin'}, limit=1) == 0:
        pwd_hash = bcrypt.generate_password_hash('123').decode()
        db.users.insert_one({'username': 'admin', 'password_hash': pwd_hash})
except Exception as _e:
    pass

class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash
    
    def get_id(self):
        return str(self.id)
    
    def is_active(self):
        return True
    
    def is_authenticated(self):
        return True
    
    def is_anonymous(self):
        return False

@login_manager.user_loader
def load_user(user_id):
    try:
        doc = db.users.find_one({'_id': ObjectId(user_id)})
    except Exception:
        doc = None
    if not doc:
        return None
    # Map Mongo doc to User(id, username, password_hash)
    return User(str(doc['_id']), doc.get('username'), doc.get('password_hash'))

# ---------------------------
# Load DataFrame used across pages
# ---------------------------
DF = load_df(app.config['DATA_CSV_PATH'])

# ---------------------------
# ML Models (predictor)
# Expecting: project_root/models/predictor.py + *.joblib
# ---------------------------
ML_MODELS_DIR = os.path.join(app.root_path, "models")
if ML_MODELS_DIR not in sys.path:
    sys.path.append(ML_MODELS_DIR)

try:
    from predictor import predict_all  # inside models/predictor.py
except Exception as e:
    raise RuntimeError(f"Could not import predictor from models: {e}")

# ---------------------------
# Security middleware
# ---------------------------
@app.before_request
def security_check():
    # Skip security check for login page and static files
    if request.endpoint in ['login', 'static']:
        return
    
    # Check if user is authenticated for all other routes
    if not current_user.is_authenticated:
        # Store the attempted URL for redirect after login
        if request.endpoint and request.endpoint != 'login':
            session['next'] = request.url
        return redirect(url_for('login'))
    
    # Log access for security monitoring
    app.logger.info(f"Access: {request.method} {request.path} | User: {current_user.username} | IP: {request.remote_addr}")

@app.before_request
def _trace():
    app.logger.info(f"{request.method} {request.path} | auth={getattr(current_user, 'is_authenticated', False)} | next={request.args.get('next')}")

@app.before_request
def session_timeout():
    """Handle session timeout"""
    if current_user.is_authenticated:
        # Refresh session on each request
        session.permanent = True

# ---------------------------
# Helpers
# ---------------------------
def _normalize_next():
    n = (request.values.get("next") or "").strip()
    if not n:
        return None
    if n.lower() in ("none", "null", "undefined"):
        return None
    return n

def _is_safe_next_url(target):
    if not target:
        return False
    ref = urlparse(request.host_url)
    test = urlparse(urljoin(request.host_url, target))
    return (test.scheme in ("http", "https")) and (ref.netloc == test.netloc)

# ---------------------------
# Routes
# ---------------------------
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    # If user is already logged in, redirect to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Username and password are required', 'error')
            return render_template('login.html')
        
        doc = db.users.find_one({'username': username})
        if doc and bcrypt.check_password_hash(doc.get('password_hash',''), password):
            user = User(str(doc['_id']), doc.get('username'), doc.get('password_hash'))
            login_user(user, remember=True)
            
            # Set session as permanent
            session.permanent = True
            
            # Check for stored next URL from security middleware
            next_url = session.get('next') or _normalize_next()
            if next_url and _is_safe_next_url(next_url):
                session.pop('next', None)  # Clear the stored URL
                return redirect(next_url)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    username = current_user.username
    logout_user()
    session.clear()  # Clear all session data
    flash(f'Successfully logged out, {username}', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/add-admin', methods=['GET','POST'])
@login_required
def add_admin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            flash('Username and password required', 'error')
            return redirect(url_for('add_admin'))
        try:
            pwd_hash = bcrypt.generate_password_hash(password).decode()
            try:
                db.users.insert_one({'username': username, 'password_hash': pwd_hash})
            except DuplicateKeyError:
                raise ValueError('Username already exists')
            flash('Admin added', 'success')
        except Exception as e:
            flash(f'Error: {e}', 'error')
    return render_template('add_admin.html')

@app.route('/attrition')
@login_required
def attrition_view():
    table = who_is_going_to_leave(DF).to_dict(orient='records')
    return render_template('attrition.html', rows=table)

@app.route('/medical')
@login_required
def medical_view():
    table = medical_scores(DF).to_dict(orient='records')
    return render_template('medical.html', rows=table)

@app.route('/training')
@login_required
def training_view():
    thresh = int(request.args.get('thresh', 60))
    table = who_needs_training(DF, thresh=thresh).to_dict(orient='records')
    return render_template('training.html', rows=table, thresh=thresh)

@app.route('/leadership')
@login_required
def leadership_view():
    table = leadership_list(DF).to_dict(orient='records')
    return render_template('leadership.html', rows=table)

@app.route('/skills')
@login_required
def skills_view():
    groups = skill_grouping(DF)
    return render_template('skills.html', groups=groups)

@app.route("/readiness", methods=["GET", "POST"], endpoint="readiness_view")
@login_required
def readiness():
    headcount = int(request.values.get("headcount", 10))
    roles_raw = (request.values.get("roles") or "").strip()
    required_roles = [r.strip() for r in roles_raw.split(",") if r.strip()]
    restrict_to_roles = bool(required_roles)

    team_df = select_best_team(
        DF,
        headcount=headcount,
        required_roles=required_roles or None,
        restrict_to_roles=restrict_to_roles,
    )
    rows = team_df.to_dict(orient="records")
    return render_template("readiness.html", team=rows)

@app.route('/whatif', methods=['GET','POST'])
@login_required
def whatif_view():
    result = None
    if request.method == 'POST':
        text = request.form.get('query', '')
        result = what_if_simulation(DF, text)
    return render_template('whatif.html', result=result)

@app.route("/readiness-status")
@login_required
def readiness_status():
    from utils import logic
    data = logic.get_readiness_data()
    return render_template("readiness_status.html", data=data)

# ---------------------------
# Add Personnel (Predictive) — ONLY necessary inputs; targets are predicted
# ---------------------------
@app.route("/add-personnel", methods=["GET", "POST"])
@login_required
def add_personnel():
    # choices discovered in your dataset; adjust if you standardize differently
    ROLE_CHOICES = ["Pilot", "Engineer", "Technician", "Radar Operator", "Cybersecurity", "Admin", "Medical"]
    SKILL_CHOICES = ["Technician", "Engineer", "Pilot", "Radar Operator", "Cybersecurity", "Admin", "Medical"]

    if request.method == "POST":
        try:
            person_name = (request.form.get("name") or "").strip()
            role = (request.form.get("role") or "").strip()
            skills = (request.form.get("skills") or "").strip()
            experience_years = int(request.form.get("experience_years") or 0)
            training_completed = (request.form.get("training_completed") == "yes")
            medical_score = float(request.form.get("medical_score") or 0)

            if not person_name:
                raise BadRequest("Name is required.")
            if not role or not skills:
                raise BadRequest("Role and Skills are required.")
            if experience_years < 0 or medical_score < 0:
                raise BadRequest("Experience years and medical score must be non-negative.")

            preds = predict_all(role, skills, experience_years, training_completed, medical_score)

            # (optional) save to DB here if you have a model
            flash("Personnel added. Predictions generated successfully.", "success")
            return render_template("add_personnel.html",
                                   role_choices=ROLE_CHOICES,
                                   skill_choices=SKILL_CHOICES,
                                   preds=preds,
                                   name=person_name)
        except Exception as e:
            flash(f"Error: {e}", "error")
            return render_template("add_personnel.html",
                                   role_choices=ROLE_CHOICES,
                                   skill_choices=SKILL_CHOICES,
                                   preds=None,
                                   name=request.form.get("name") or "")

    return render_template("add_personnel.html",
                           role_choices=ROLE_CHOICES,
                           skill_choices=SKILL_CHOICES,
                           preds=None,
                           name="")

# ---------------------------
# Main
# ---------------------------
if __name__ == '__main__':
    app.run(debug=True)
