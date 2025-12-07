import os
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Chargement de la clé
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Configuration
if api_key:
    genai.configure(api_key=api_key)
else:
    print("⚠️ ATTENTION : Pas de clé API trouvée dans le fichier .env")

def generate_viral_metadata(surah_name, ayah_number, text_fr, theme):
    """
    Génère titre, description et hashtags via Google Gemini.
    """
    if not api_key:
        return "Erreur : Clé API manquante."

    try:
        # CORRECTION ICI : On utilise 'gemini-pro' qui est le standard stable
        model = genai.GenerativeModel('gemini-2.5-flash')

        prompt = f"""
        Rôle : Expert Community Manager Musulman pour TikTok.
        Tâche : Rédiger les métadonnées pour une vidéo de ce verset :
        - Sourate : {surah_name} ({ayah_number})
        - Thème : {theme}
        - Texte : "{text_fr}"

        Format de réponse OBLIGATOIRE :
        
        [TITRE]
        (Court, accrocheur, max 1 emoji)

        [DESCRIPTION]
        (2 phrases inspirantes et bienveillantes. Pas de texte générique.)

        [HASHTAGS]
        (5 hashtags pertinents mixant FR/EN)
        """

        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        # Si ça plante, on affiche l'erreur exacte pour débugger
        return f"Erreur IA : {str(e)}"

# --- ZONE DE TEST ---
if __name__ == "__main__":
    print("--- 🧠 TEST DU CERVEAU IA (GEMINI PRO) ---")
    
    # Simulation
    s_name = "Al-Asr"
    a_num = 1
    txt = "Par le Temps ! L'homme est certes en perdition."
    th = "Time"
    
    print("⏳ Envoi de la demande à Gemini Pro...")
    resultat = generate_viral_metadata(s_name, a_num, txt, th)
    
    print("\n--- RÉSULTAT REÇU ---")
    print(resultat)