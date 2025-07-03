#---------------------------------------------IMPORTS-----------------------------------------------------
from flask import Flask, render_template, request, session, redirect, url_for , flash
import google.generativeai as genai 
from flask_session import Session
from markupsafe import Markup
from markdown import markdown
import os 
import re
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from Database import User_cred, Cars ,addtocars, db , app 


#---------------------------------------------INITTIALISATION---------------------------------------------
app = Flask(__name__) 
secret_key = os.environ.get('SECRET_KEY') 
app.config["SECRET_KEY"] = secret_key 
app.config["SESSION_PERMANENT"] = False 
app.config["SESSION_TYPE"] = "filesystem" 
Session(app)


api_key = os.environ['API_KEY']   
genai.configure(api_key=api_key)  
model = genai.GenerativeModel("models/gemini-2.5-flash-preview-05-20") 

app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://myapp_user:root@localhost/prime_base'
app.config['SQLALCHEMY_BINDS'] = {'sqlite_db': 'sqlite:///demo.db'}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app) # same as db.SQLAlchemy(app) .but not initialising in same way, because dupicate error occurs.


# -----------------------------------------------------ADMIN PANEL----------------------------------------
with app.app_context():
    db.create_all()
    addtocars()

admin = Admin(app, name='My Admin', template_mode='bootstrap4')
admin.add_view(ModelView(User_cred, db.session))
admin.add_view(ModelView(Cars, db.session))
#---------------------------------------------------RESPONSE FORMATTING.----------------------------------
def format_code_blocks(text):
    # First, convert markdown to HTML
    html = markdown(text, extensions=["fenced_code", "codehilite", "tables"])
    
    # Pattern to match code blocks with optional language
    pattern = r'<pre><code(?:\s+class="language-(\w+)")?>(.*?)</code></pre>'
    
    def replacer(match):
        lang = match.group(1) or "text"  # Default to "text" if no language specified
        code = match.group(2)
        
        # Don't double-escape if already escaped
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
    
    # Apply the replacement
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
    eth_data = ['', 'ETH', 'Proof of Stake (PoS)', '', 'Moderate. ~15-30 TPS', 'Variable', '', 'DeFi, NFTs, DAOs',
                'Significant', '', 'Launched in 2015', '', '']
    sol_data = ['', '', '', '', 'High-performance, aiming for speed', 'Low costs', '', '', 'Lower', '', 'Newer',
                'Speed, low costs', '']

    for i in range(len(features)):
        row = f"| {features[i]} | {btc_data[i]} | {eth_data[i]} | {sol_data[i]} |"
        table_md += row + "\n"
    return table_md

#----------------------------------------------------AUTHENTICATION.--------------------------------------
@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        entries = [
            (firstname,lastname,username,email,password)
        ]

        for firstname,lastname,username,email,password in entries:
          exists = User_cred.query.filter_by(firstname=firstname,lastname=lastname,username=username,email=email,password=password).first()
          if not exists:
                adding = User_cred(firstname=firstname,lastname=lastname,username=username,email=email,password=password)
                db.session.add(adding)
                db.session.commit()

        
        return redirect('/signin')
    return render_template('/signup.html')

@app.route('/signin', methods=["GET", "POST"]) 
def signin():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User_cred.query.filter_by(email=email, password=password).first()
        if user: 
            session['user_id'] = user.id
            session['username'] = user.username
            session['signin_user'] = user.email
            print(session)
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('signin'))
    return render_template('signin.html',user=session.get('signin_user'))
   
@app.route('/logout', methods=["GET", "POST"]) 
def logout():
    session.clear()
    flash("Logged out")
    return redirect(url_for('dashboard'))

#----------------------------------------------------DASHBOARD.-------------------------------------------
@app.route('/', methods=['POST', 'GET'])
def dashboard():
    user = session.get('signin_user')
    username = session.get('username')
    if request.method == 'POST':
        prompt = request.form.get("prompt")
        if prompt and "comparison table" in prompt.lower():
            response_text = generate_comparison_table({})
        else:
            response = model.generate_content(prompt)
            response_text = response.text
        formatted = format_code_blocks(response_text)
        return render_template('dashboard.html', prompt=prompt,response=Markup(formatted),user=user,username=username)
    return render_template('dashboard.html',user=user,username=username)


app.run(debug=True, port=3000)