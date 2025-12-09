import os
import sys
import numpy as np
import textwrap 
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoFileClip, CompositeVideoClip, AudioFileClip, ColorClip, ImageClip
from moviepy.config import change_settings
import arabic_reshaper
from bidi.algorithm import get_display

# Ajout du dossier parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.data_fetcher import get_random_verse

# --- 1. CONFIGURATION ---
# Ton chemin ImageMagick (Celui qui marche chez toi)
change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"})

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_ARABIC = os.path.join(BASE_DIR, "assets", "fonts", "arabic.ttf")
FONT_LATIN = os.path.join(BASE_DIR, "assets", "fonts", "latin.ttf")

# --- 2. FONCTION TEXTE AVANCÉE (PIL) ---
def creer_clip_texte_pil(texte, font_path, font_size, color, video_size, position_y):
    w_video, h_video = video_size
    
    # A. Chargement Police
    try:
        font = ImageFont.truetype(font_path, font_size)
    except:
        font = ImageFont.load_default()

    # B. Traitement du texte (Arabe vs Français)
    is_arabic = "arabic" in font_path
    if is_arabic:
        # Pour l'arabe, on reshape + bidi
        reshaped_text = arabic_reshaper.reshape(texte)
        final_text = get_display(reshaped_text)
        alignement = 'center'
    else:
        # Pour le français, on coupe les lignes trop longues (Wrap)
        final_text = textwrap.fill(texte, width=30) 
        alignement = 'center'

    # C. Création Image Vide
    img = Image.new('RGBA', (w_video, h_video), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # D. Calcul de la taille du texte pour le centrer et faire le fond noir
    left, top, right, bottom = draw.textbbox((0, 0), final_text, font=font, align=alignement)
    text_width = right - left
    text_height = bottom - top

    # Centrage horizontal
    x = (w_video - text_width) / 2
    
    # E. Dessiner le Rectangle Noir (Background Box)
    padding = 20
    box = [
        x - padding, 
        position_y - padding, 
        x + text_width + padding, 
        position_y + text_height + padding
    ]
    # Noir (0,0,0) avec opacité 160/255
    draw.rectangle(box, fill=(0, 0, 0, 160))

    # F. Dessiner le Texte
    # On ajoute une petite ombre portée noire pour le contraste
    draw.multiline_text((x+2, position_y+2), final_text, font=font, fill="black", align=alignement)
    draw.multiline_text((x, position_y), final_text, font=font, fill=color, align=alignement)

    return ImageClip(np.array(img))

def create_video(verse_data, background_path, output_filename="output/video_finale.mp4"):
    print(f"🎬 Montage : {verse_data['surah_name']} {verse_data['ayah_number']}")
    
    try:
        # --- AUDIO ---
        print(f"   ⬇️ Audio...")
        audio_clip = AudioFileClip(verse_data['audio_url'])
        duration = audio_clip.duration + 2.0

        # --- FOND ---
        if os.path.exists(background_path):
            bg_clip = VideoFileClip(background_path)
            if bg_clip.duration < duration:
                bg_clip = bg_clip.loop(duration=duration)
            else:
                bg_clip = bg_clip.subclip(0, duration)
            
            bg_clip = bg_clip.resize(height=1920)
            bg_clip = bg_clip.crop(x1=bg_clip.w/2 - 540, y1=0, width=1080, height=1920)
        else:
            print("   ⚠️ Fond noir.")
            bg_clip = ColorClip(size=(1080, 1920), color=(0, 0, 0), duration=duration)

        # --- CALQUE SOMBRE GÉNÉRAL ---
        dark_layer = ColorClip(size=(1080, 1920), color=(0, 0, 0)).set_opacity(0.3).set_duration(duration)

        # --- TEXTE ARABE ---
        print("   ✍️ Texte Arabe...")
        txt_arabe_clip = creer_clip_texte_pil(
            texte=verse_data['text_ar'],
            font_path=FONT_ARABIC,
            font_size=60, 
            color='white',
            video_size=(1080, 1920),
            position_y=500
        ).set_duration(duration)

        # --- TEXTE FRANÇAIS ---
        print("   ✍️ Texte Français...")
        txt_fr_clip = creer_clip_texte_pil(
            texte=verse_data['text_fr'],
            font_path=FONT_LATIN,
            font_size=40,
            color='#FFD700', # Jaune Or
            video_size=(1080, 1920),
            position_y=1100
        ).set_duration(duration)

        # --- ASSEMBLAGE ---
        final_video = CompositeVideoClip([bg_clip, dark_layer, txt_arabe_clip, txt_fr_clip])
        final_video = final_video.set_audio(audio_clip)

        # --- RENDU ---
        output_path = os.path.join(BASE_DIR, output_filename)
        print("   ⚡ Rendu...")
        final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac", preset='ultrafast')
        print(f"✅ Terminé : {output_path}")
        return True

    except Exception as e:
        print(f"❌ Erreur Montage : {e}")
        import traceback
        traceback.print_exc()
        return False

# --- TEST ---
if __name__ == "__main__":
    print("--- 🧪 TEST VIDÉO V2 (Design Pro) ---")
    verset_reel = get_random_verse()
    if verset_reel['success']:
        bg_test = os.path.join(BASE_DIR, "assets", "backgrounds", "test_video.mp4")
        create_video(verset_reel, bg_test)