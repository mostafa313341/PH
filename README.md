​4.1. Phishing Simulation Platform​
​4.1.1. Theoretical Framework and Industry Context​
​Phishing simulations are authorized, fake attacks sent to employees to test their susceptibility.​
​The goal is to measure metrics like "Click Rate" and "Reporting Rate".​ ​30​ ​These platforms​
​require a sophisticated email delivery infrastructure and tracking mechanisms​
​indistinguishable from real attacks.​ ​31​
​4.1.2. Architectural Considerations​
​The system must generate unique tracking links for every user to attribute clicks accurately. It​
​involves three main components: a Campaign Manager (admin UI), a Mailer (SMTP sender),​
​and a Landing Page (the "trap" site).​​Ethical Constraint:​​While the system simulates​
​credential harvesting, it must​​never​​store the actual​​passwords entered by users, only the​
​event​​that data was submitted.​ ​



# Run the install Libraries
 
pip install -r requirements.txt

# Defult

python main.py

# Docker compose

docker-compose up -d


# open the browser in
http://localhost:7777/admin

User: admin 
Password : 313123
