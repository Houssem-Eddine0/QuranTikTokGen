import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ Clé API introuvable dans .env")
else:
    genai.configure(api_key=api_key)
    print("🔍 Recherche des modèles disponibles pour ta clé...")
    try:
        for m in genai.list_models():
            # On cherche seulement les modèles qui savent générer du texte
            if 'generateContent' in m.supported_generation_methods:
                print(f"✅ Disponible : {m.name}")
    except Exception as e:
        print(f"❌ Erreur de connexion : {e}")