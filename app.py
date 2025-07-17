#---------------------------------------------IMPORTS-----------------------------------------------------------------------------
from flask import Flask, render_template, request, session, redirect, url_for, flash
import google.generativeai as genai 
from flask_session import Session
from markupsafe import Markup
from markdown import markdown
import os 
import re
from authlib.integrations.flask_client import OAuth
from Database import User_cred, db
import hashlib
from dotenv import load_dotenv
import traceback
from api import api


#---------------------------------------------INITIALIZATION---------------------------------------------------------------------
load_dotenv()
app = Flask(__name__) 
app.register_blueprint(api)
secret_key = os.environ.get('SECRET_KEY') 
app.config["SECRET_KEY"] = secret_key 
app.config["SESSION_PERMANENT"] = False 
app.config["SESSION_TYPE"] = "filesystem" 
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

oauth = OAuth(app)
Session(app)

api_key = os.environ.get('API_KEY')   
genai.configure(api_key=api_key)  
model = genai.GenerativeModel("models/gemini-2.5-flash-preview-05-20") 

db.init_app(app)

client_id = os.environ.get('CLIENT_ID')
client_secret = os.environ.get('CLIENT_SECRET')

google = oauth.register(
    name='google',
    client_id=client_id,
    client_secret=client_secret,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

with app.app_context():
    db.create_all()
#---------------------------------------------------RESPONSE FORMATTING----------------------------------------------------------
def format_code_blocks(text):
    html = markdown(text, extensions=["fenced_code", "codehilite", "tables"])
    pattern = r'<pre><code(?:\s+class="language-(\w+)")?>(.*?)</code></pre>'
    
    def replacer(match):
        lang = match.group(1) or "text"
        code = match.group(2)
        
        if "&lt;" not in code and "&gt;" not in code:
            code = code.replace("<", "&lt;").replace(">", "&gt;")
        
        return f'''
<div class="code-block">
  <div class="code-header">
    <span class="code-lang">{lang}</span>
    <button class="copy-btn" onclick="copyCode(this)">📋 Copy</button>
  </div>
  <pre><code class="language-{lang}">{code}</code></pre>
</div>
'''
    
    result = re.sub(pattern, replacer, html, flags=re.DOTALL)
    return result

def generate_comparison_table(data):
    table_md = "| Feature                  | Bitcoin (BTC)                          | Ethereum (ETH)                        | Solana                                |\n"
    table_md += "|--------------------------|----------------------------------------|---------------------------------------|---------------------------------------|\n"
    
    features = [
        'Primary Goal/Purpose', 'Native Cryptocurrency', 'Consensus Mechanism', 'Smart Contract Capability',
        'Transaction Speed (TPS)', 'Transaction Cost (Gas Fees)', 'Scalability Approach', 'Ecosystem Focus',
        'Energy Consumption', 'Decentralization', 'Network History/Launch', 'Key Strengths', 'Key Weaknesses/Challenges'
    ]
    
    btc_data = [
        'Digital Gold, Store of Value, Peer-to-Peer Electronic Cash', 'BTC', 'Proof of Work (PoW)',
        'Limited. Supports basic scripting for transactions (e.g., multi-signature)', 'Low. ~3-7 TPS',
        'Variable. Can be high during network congestion.', 'Limited on-chain. Relies on Layer 2 solutions like Lightning Network',
        'Primarily payments and store of value', 'High. Due to PoW (requires significant computational power)',
        'Very High. Large number of independent miners and nodes globally', 'Launched in 2009',
        'Security, decentralization, censorship resistance, proven track record',
        'Slow transaction speed, high energy consumption (PoW), limited scalability'
    ]
    
    eth_data = ['World Computer, Smart Contract Platform', 'ETH', 'Proof of Stake (PoS)', 
                'Full smart contract support', 'Moderate. ~15-30 TPS', 'Variable, high during congestion', 
                'Layer 2 solutions (Polygon, Arbitrum)', 'DeFi, NFTs, DAOs',
                'Moderate (reduced after PoS)', 'High, but less than Bitcoin', 'Launched in 2015', 
                'Mature ecosystem, developer tools', 'Scalability, high gas fees']
    
    sol_data = ['High-performance blockchain', 'SOL', 'Proof of History + PoS', 
                'Full smart contract support', 'High. ~65,000 TPS', 'Low costs', 
                'High throughput native chain', 'DeFi, NFTs, Web3 apps',
                'Lower than Bitcoin/Ethereum', 'Moderate, fewer validators', 'Launched in 2020',
                'Speed, low costs, growing ecosystem', 'Newer, network outages, centralization concerns']

    for i in range(len(features)):
        row = f"| {features[i]} | {btc_data[i]} | {eth_data[i]} | {sol_data[i]} |"
        table_md += row + "\n"
    
    return table_md

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/auth/callback')
def callback():
    try:
        token = google.authorize_access_token()
        # print(" Got access token:", token) Enable this if you want to.
        user_info = token['userinfo']
        print(f"user_info {user_info}")
        
        user = User_cred.query.filter_by(email=user_info['email']).first()

        if not user:
            print("New user, adding to DB")
            # Create new user from Google profile
            user = User_cred(
                firstname=user_info.get('given_name', ''),
                lastname=user_info.get('family_name', ''),
                username=user_info.get('email'),  
                email=user_info['email'],
                password=None,  # OAuth users don't have passwords
                auth_provider='google',
                google_id=user_info.get('sub'),
                
            )

            db.session.add(user)
            db.session.commit()
            flash("Account created successfully via Google!", "success")
        else:
            # Update existing user's Google ID if not set
            if not user.google_id:
                user.google_id = user_info.get('sub')
                user.auth_provider = 'google'
                db.session.commit()
                print("user added to DB")
        
        # Set session variables consistently
        session['user_id'] = user.id # This user_id is database field.
        session['username'] = user.username
        session['signin_user'] = user.email
        session['auth_method'] = 'google'
        session['user_firstname'] = user.firstname
        
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        traceback.print_exc()  # 👈 shows the actual line that broke
        print("Google OAuth DB error:", str(e))
        flash(f"Authentication failed: {str(e)}", "error")
        return redirect(url_for('signin'))

@app.route('/signin', methods=["GET", "POST"])
def signin():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash("Email and password are required", "error")
            return render_template('signin.html')
        
        # Hash password for comparison
        hashed_password = hash_password(password)
        user = User_cred.query.filter_by(email=email, password=hashed_password).first()
        
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            session['signin_user'] = user.email
            session['auth_method'] = 'form'
            session['user_firstname'] = user.firstname
            print(user)
            flash(f"Welcome back, {user.firstname}!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password", "error")
    
    return render_template('signin.html')

@app.route('/auth/google')
def google_signin():
    redirect_uri = request.host_url.rstrip('/') + url_for('callback')
    print("Redirect URI:", redirect_uri)  # Debug print
    return google.authorize_redirect(redirect_uri)

@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == 'POST':
        # Get form data
        form_data = {
            'firstname': request.form.get('firstname', '').strip(),
            'lastname': request.form.get('lastname', '').strip(),
            'username': request.form.get('username', '').strip(),
            'email': request.form.get('email', '').strip(),
            'password': request.form.get('password', '')
        }
      
        # Check if user already exists
        existing_user = User_cred.query.filter(
            (User_cred.email == form_data['email']) | 
            (User_cred.username == form_data['username'])
        ).first()
        
        if existing_user:
            if existing_user.email == form_data['email']:
                flash("Email already exists", "error")
            else:
                flash("Username already exists", "error")
            return render_template('signup.html')
        
        
            # Create new user
        hashed_password = hash_password(form_data['password'])
        new_user = User_cred(
                firstname=form_data['firstname'],
                lastname=form_data['lastname'],
                username=form_data['username'],
                email=form_data['email'],
                password=hashed_password,
                auth_provider='form',
                
            )
            
        db.session.add(new_user)
        db.session.commit()
            
        flash("Account created successfully! Please sign in.", "success")
        return redirect(url_for('signin'))
            
    
    return render_template('signup.html')


@app.route('/logout', methods=["GET", "POST"]) 
def logout():
    user_name = session.get('user_firstname', 'User')
    session.clear()
    flash(f"Goodbye, {user_name}! You have been logged out.", "info")
    return redirect(url_for('dashboard'))

#----------------------------------------------------DASHBOARD-------------------------------------------------------------------
@app.route('/', methods=['POST', 'GET'])
def dashboard():
    user = session.get('signin_user')
    username = session.get('username')
    user_firstname = session.get('user_firstname')
    
    if request.method == 'POST':
        prompt = request.form.get("prompt", "").strip()
        
        if not prompt:
            flash("Please enter a prompt", "error")
            return render_template('dashboard.html', user=user, username=username, user_firstname=user_firstname)
        
        try:
            if "comparison table" in prompt.lower():
                response_text = generate_comparison_table({})
            else:
                response = model.generate_content(prompt)
                response_text = response.text
            
            formatted = format_code_blocks(response_text)
            return render_template('dashboard.html', 
                                 prompt=prompt, 
                                 response=Markup(formatted), 
                                 user=user, 
                                 username=username, 
                                 user_firstname=user_firstname)
        except Exception as e:
            flash(f"Error generating response: {str(e)}", "error")
            return render_template('dashboard.html', user=user, username=username, user_firstname=user_firstname)
        
    
    return render_template('dashboard.html', user=user, username=username, user_firstname=user_firstname)























@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3000)