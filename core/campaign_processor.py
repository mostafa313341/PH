import uuid
import csv
import os
from core.mailer import Mailer

"""
هذه الدالة المسؤولة عن قرائة الملفات و اضافة و بناء الايميل لكل هدف مع القالب الذي تم اختياره في ملف القوالب
كما انه بها كود الصورة المرفقة في الايميل و التي تحدث حالة فتح الرسالة في لوحة الادمن 
"""

def start_campaign(campaign_id, template_id, sender_name, sender_email, base_url="http://127.0.0.1:7777"):
    results_path = 'data/victims.csv'
    targets_path = 'data/targets.csv'
    templates_path = 'data/templates.csv'
    
    mailer = Mailer()
    
    template = None
    if not os.path.exists(templates_path):
        return False
        
    with open(templates_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['template_id'] == template_id:
                template = row
                break
    
    if not template:
        return False

    if not os.path.exists(targets_path):
        return False

    with open(targets_path, mode='r', encoding='utf-8') as f_in, \
         open(results_path, mode='a', newline='', encoding='utf-8') as f_out:
        
        targets = csv.DictReader(f_in)
        writer = csv.writer(f_out)
        
        for target in targets:
            u_id = str(uuid.uuid4())
            tracking_link = f"{base_url}/login?id={u_id}"
            
            tracking_pixel = f'<img src="{base_url}/track_open?id={u_id}" width="1" height="1" style="display:none !important;">'
            
            email_body = template['body_html'].replace("{{name}}", target['name'])
            email_body = email_body.replace("{{link}}", tracking_link)
            
            full_html_content = f"<html><body>{email_body}{tracking_pixel}</body></html>"
            
            sent = mailer.send_phishing_email(
                target['email'], 
                template['subject'], 
                full_html_content, 
                sender_name, 
                sender_email
            )
            
            if sent:
                writer.writerow([u_id, campaign_id, target['target_id'], "False", "False", "False"])
    
    return True