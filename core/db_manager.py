import csv
import os

"""
هذه الكلاسس مسؤولة عن معالجة البيانات 
تقوم بالتحقق من مجلد data
و اذا لم يكن موجود تقوم بانشائه 
و تقوم بالتحقق من الملفات و تقوم باضافة لهم العناوين ان لم تكن موجودة
"""

class DBManager:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.files = {
            "targets.csv": ["target_id", "name", "email", "department"],
            "templates.csv": ["template_id", "subject", "body_html"],
            "campaigns.csv": ["campaign_id", "name", "template_id", "status"],
            "results.csv": ["tracking_uuid", "campaign_id", "target_id", "is_opened", "is_clicked", "is_submitted"]
        }
        self._initialize_files()

    def _initialize_files(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        for filename, headers in self.files.items():
            path = os.path.join(self.data_dir, filename)
            if not os.path.exists(path):
                with open(path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(headers)

    def get_all_targets(self):
        path = os.path.join(self.data_dir, "targets.csv")
        with open(path, mode='r', encoding='utf-8') as f:
            return list(csv.DictReader(f))

    def get_template(self, template_id):
        path = os.path.join(self.data_dir, "templates.csv")
        with open(path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['template_id'] == template_id:
                    return row
        return None