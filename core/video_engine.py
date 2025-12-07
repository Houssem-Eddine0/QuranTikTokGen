import os
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip, ColorClip
from moviepy.config import change_settings
import arabic_reshaper
from bidi.algorithm import get_display

# --- 1. CONFIGURATION DES CHEMINS (A modifier selon ton PC) ---
# Si tu es sur Windows, laisse cette ligne. Sinon, commente-la.
change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})

# --- 2. CONFIGURATION DU DESIGN (C'est ici que tu changes la position !) ---
POSITION_ARABE = ('center', 450)    # (Horizontal, Vertical en pixels depuis le haut)
POSITION_FR = ('center', 1100)      # Le français est plus bas
TAILLE_FONT_ARABE = 80              # Gros texte pour le Coran
TAILLE_FONT_FR = 40                 # Texte moyen pour la trad

# Chemins des polices
FONT_ARABIC = "assets/fonts/arabic.ttf" 
FONT_LATIN = "assets/fonts/latin.ttf"

def process_arabic_text(text):
    """
    Fonction magique pour réparer l'arabe.
    """
    if not text:
        return ""
    # 1. On lie les lettres entre elles
    reshaped_text = arabic_reshaper.reshape(text)
    # 2. On inverse le sens pour le Right-to-Left
    bidi_text = get_display(reshaped_text)
    return bidi_text

def create_video(verse_data, background_path, output_filename="output/video_finale.mp4"):
    print(f"🎬 Montage : {verse_data['surah_name']} {verse_data['ayah_number']}")

    try:
        # --- AUDIO ---
        # Note: Si tu utilises une URL, assure-toi d'avoir une bonne connexion
        audio_clip = AudioFileClip(verse_data['audio_url'])
        duration = audio_clip.duration + 2 # On rajoute 2 sec de silence à la fin

        # --- FOND VIDÉO ---
        if os.path.exists(background_path):
            bg_clip = VideoFileClip(background_path)
            # Boucle si nécessaire
            if bg_clip.duration < duration:
                bg_clip = bg_clip.loop(duration=duration)
            else:
                bg_clip = bg_clip.subclip(0, duration)
            
            # Crop 9:16 (Format TikTok)
            # On redimensionne pour que la hauteur fasse 1920px
            bg_clip = bg_clip.resize(height=1920)
            # On coupe le centre (Crop Center)
            bg_clip = bg_clip.crop(x1=bg_clip.w/2 - 540, y1=0, width=1080, height=1920)
        else:
            print("⚠️ Pas de vidéo de fond. Fond noir utilisé.")
            bg_clip = ColorClip(size=(1080, 1920), color=(0, 0, 0), duration=duration)

        # --- CALQUE SOMBRE (Pour mieux lire) ---
        dark_layer = ColorClip(size=(1080, 1920), color=(0, 0, 0)).set_opacity(0.5).set_duration(duration)

        # --- TEXTE ARABE ---
        # On traite le texte pour qu'il ne soit pas à l'envers
        texte_arabe_corrige = process_arabic_text(verse_data['text_ar'])
        
        txt_arabe = TextClip(
            texte_arabe_corrige,
            font=FONT_ARABIC,   # Utilise bien la police Amiri !
            fontsize=TAILLE_FONT_ARABE,
            color='white',
            size=(900, None),   # Largeur max 900px
            method='caption',   # Permet le retour à la ligne auto
            align='center'      # Centre le texte dans sa boite
        ).set_position(POSITION_ARABE).set_duration(duration)

        # --- TEXTE FRANÇAIS ---
        txt_fr = TextClip(
            verse_data['text_fr'],
            font=FONT_LATIN,
            fontsize=TAILLE_FONT_FR,
            color='yellow',     # Jaune pour bien ressortir
            size=(900, None),
            method='caption',
            align='center'
        ).set_position(POSITION_FR).set_duration(duration)

        # --- ASSEMBLAGE ---
        final_video = CompositeVideoClip([bg_clip, dark_layer, txt_arabe, txt_fr])
        final_video = final_video.set_audio(audio_clip)

        # --- EXPORT ---
        print("⚡ Rendu en cours...")
        # preset='ultrafast' pour tester plus vite (qualité un peu moindre mais rapide)
        final_video.write_videofile(output_filename, fps=24, codec="libx264", audio_codec="aac", preset='ultrafast')
        print(f"✅ Vidéo terminée : {output_filename}")
        return True

    except Exception as e:
        print(f"❌ Erreur : {e}")
        return False

# --- ZONE DE TEST ---
if __name__ == "__main__":
    dummy_data = {
        "surah_name": "Al-Ikhlas",
        "ayah_number": 1,
        "audio_url": "https://cdn.islamic.network/quran/audio/128/ar.alafasy/6236.mp3", # Qul huwa Allahu Ahad
        "text_ar": "قُلْ هُوَ ٱللَّهُ أَحَدٌ", # Texte brut (sera corrigé par le script)
        "text_fr": "Dis : Il est Allah, Unique."
    }
    # Mets une vidéo nommée 'test_video.mp4' dans assets/backgrounds/ pour tester le fond
    create_video(dummy_data, "assets/backgrounds/test_video.mp4")