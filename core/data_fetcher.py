import requests
import random

# --- CONFIGURATION DES RÉCITATEURS ---
RECITERS = {
    "Mishary Rashid Alafasy": "ar.alafasy",
    "Abdul Basit (Murattal)": "ar.abdulbasitmurattal",
    "Mahmoud Khalil Al-Husary": "ar.husary",
    "Mohamed Siddiq Al-Minshawi": "ar.minshawi",
    "Saud Al-Shuraim": "ar.shuraim",
    "Maher Al Muaiqly": "ar.mahermuaiqly"
}

def get_surah_list():
    """ Récupère la liste des sourates """
    url = "http://api.alquran.cloud/v1/surah"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()['data']
            surah_dict = {}
            for s in data:
                surah_dict[s['number']] = {
                    'nom_phonetique': s['englishName'],
                    'nom_traduit': s['englishNameTranslation'],
                    'nombre_versets': s['numberOfAyahs']
                }
            return surah_dict
        return None
    except Exception as e:
        print(f"❌ Erreur connexion API Sourates : {e}")
        return None

def get_ayah_data(surah_num, ayah_num, reciter_key="ar.alafasy"):
    """
    Récupère l'audio et le texte UTHMANI (avec voyelles)
    """
    # ICI : On demande 'quran-uthmani' au lieu de 'quran-simple'
    url = f"http://api.alquran.cloud/v1/ayah/{surah_num}:{ayah_num}/editions/{reciter_key},quran-uthmani,fr.hamidullah,en.sahih"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()['data']
            
            audio_data = data[0] # Audio
            arabe_data = data[1] # Arabe Uthmani
            fr_data = data[2]    # Français
            en_data = data[3]    # Anglais

            return {
                "success": True,
                "surah_name": audio_data['surah']['englishName'],
                "surah_number": surah_num,
                "ayah_number": ayah_num,
                "audio_url": audio_data['audio'],
                "text_ar": arabe_data['text'],
                "text_fr": fr_data['text'],
                "text_en": en_data['text'],
                "theme": audio_data['surah']['englishNameTranslation']
            }
        else:
            return {"success": False, "error": "Verset introuvable"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_random_verse(reciter_key="ar.alafasy"):
    """ Sélectionne un verset au hasard """
    surah_num = random.randint(1, 114)
    all_surahs = get_surah_list()
    
    if not all_surahs:
        return {"success": False, "error": "Impossible de récupérer la liste des sourates"}
    
    max_ayahs = all_surahs[surah_num]['nombre_versets']
    ayah_num = random.randint(1, max_ayahs)
    
    print(f"🎲 Aléatoire choisi : Sourate {surah_num}, Verset {ayah_num}")
    return get_ayah_data(surah_num, ayah_num, reciter_key)

if __name__ == "__main__":
    print("--- 🧪 TEST DATA ---")
    data = get_random_verse()
    if data['success']:
        print(f"Arabe (Vérification voyelles) : {data['text_ar']}")