import requests
import random

# --- CONFIGURATION DES RÉCITATEURS ---
# Tu pourras ajouter d'autres identifiants API ici si tu veux
RECITERS = {
    "Mishary Rashid Alafasy": "ar.alafasy",
    "Abdul Basit (Murattal)": "ar.abdulbasitmurattal",
    "Mahmoud Khalil Al-Husary": "ar.husary",
    "Mohamed Siddiq Al-Minshawi": "ar.minshawi",
    "Saud Al-Shuraim": "ar.shuraim",
    "Maher Al Muaiqly": "ar.mahermuaiqly"
}

def get_surah_list():
    """
    Récupère la liste de toutes les sourates pour le menu déroulant.
    Retourne un dictionnaire: {numero: {'nom': ..., 'versets': ...}}
    """
    url = "http://api.alquran.cloud/v1/surah"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()['data']
            surah_dict = {}
            for s in data:
                surah_dict[s['number']] = {
                    'nom_phonetique': s['englishName'],      # Ex: Al-Kahf
                    'nom_traduit': s['englishNameTranslation'], # Ex: The Cave
                    'nombre_versets': s['numberOfAyahs']
                }
            return surah_dict
        return None
    except Exception as e:
        print(f"❌ Erreur connexion API Sourates : {e}")
        return None

def get_ayah_data(surah_num, ayah_num, reciter_key="ar.alafasy"):
    """
    Récupère TOUTES les données pour un verset précis :
    - Audio (MP3)
    - Texte Arabe (Simple)
    - Traduction FR (Hamidullah)
    - Traduction EN (Sahih International)
    """
    # Construction de l'URL pour demander 4 éditions d'un coup
    # Ordre demandé : Audio, Arabe, Français, Anglais
    url = f"http://api.alquran.cloud/v1/ayah/{surah_num}:{ayah_num}/editions/{reciter_key},quran-simple,fr.hamidullah,en.sahih"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()['data']
            
            # L'API renvoie une liste. On map les données.
            # Note : On sécurise l'indexation au cas où l'API change l'ordre, 
            # mais généralement data[0] est la première édition demandée.
            
            audio_data = data[0] # Audio
            arabe_data = data[1] # Arabe
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
                "theme": audio_data['surah']['englishNameTranslation'] # Pour la recherche vidéo (ex: "The Sun")
            }
        else:
            return {"success": False, "error": "Verset introuvable"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_random_verse(reciter_key="ar.alafasy"):
    """
    Sélectionne un verset totalement au hasard dans le Coran
    """
    # 1. On choisit une sourate au hasard (1-114)
    surah_num = random.randint(1, 114)
    
    # 2. On doit savoir combien de versets elle a pour choisir un verset valide
    # Pour optimiser, on pourrait mettre la liste en cache, mais ici on refait un appel rapide
    # Ou mieux : on utilise une map simplifiée. 
    # Pour ce script, on va faire un appel à get_surah_list (un peu lent mais sûr)
    # Optimisation possible : hardcoder le nombre de versets par sourate plus tard.
    
    all_surahs = get_surah_list()
    if not all_surahs:
        return {"success": False, "error": "Impossible de récupérer la liste des sourates"}
    
    max_ayahs = all_surahs[surah_num]['nombre_versets']
    ayah_num = random.randint(1, max_ayahs)
    
    print(f"🎲 Aléatoire choisi : Sourate {surah_num}, Verset {ayah_num}")
    return get_ayah_data(surah_num, ayah_num, reciter_key)

# --- ZONE DE TEST (S'exécute seulement si on lance ce fichier directement) ---
if __name__ == "__main__":
    print("--- 🧪 TEST DU MODULE DATA_FETCHER ---")
    
    # Test 1 : Récupérer Al-Fatiha 1:1
    print("\n1. Test Verset Manuel (1:1)...")
    data = get_ayah_data(1, 1)
    if data['success']:
        print(f"✅ Audio: {data['audio_url']}")
        print(f"✅ Arabe: {data['text_ar']}")
        print(f"✅ Français: {data['text_fr']}")
        print(f"✅ Anglais: {data['text_en']}")
    else:
        print(f"❌ Erreur: {data.get('error')}")

    # Test 2 : Verset Aléatoire
    print("\n2. Test Verset Aléatoire...")
    rand_data = get_random_verse()
    if rand_data['success']:
        print(f"✅ Tiré au sort : {rand_data['surah_name']} {rand_data['surah_number']}:{rand_data['ayah_number']}")
        print(f"✅ Thème pour vidéo : {rand_data['theme']}")