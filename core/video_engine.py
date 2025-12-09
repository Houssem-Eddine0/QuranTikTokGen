import os
import sys
import numpy as np
import textwrap 
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoFileClip, CompositeVideoClip, AudioFileClip, ColorClip, ImageClip
from moviepy.config import change_settings
import arabic_reshaper # On importe le module
from bidi.algorithm import get_display

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.data_fetcher import get_random_verse

# --- 1. CONFIGURATION ---
change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"})

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_ARABIC = os.path.join(BASE_DIR, "assets", "fonts", "arabic.ttf")
FONT_LATIN = os.path.join(BASE_DIR, "assets", "fonts", "latin.ttf")

# --- 2. CONFIGURATION DU RESHAPER (POUR LES HARAKAT) ---
# C'est ici que la magie opère. On configure explicitement pour garder les voyelles.
configuration = {
    'delete_harakat': False,     # ⚠️ TRES IMPORTANT : Ne pas supprimer les voyelles
    'shift_harakat_position': False,
    'support_ligatures': True,
}
reshaper = arabic_reshaper.ArabicReshaper(configuration=configuration)

# --- 3. FONCTIONS UTILITAIRES ---
def get_optimal_font_scale(text_lines, font_path, max_width, start_size=80):
    """ Calcule la taille idéale pour que le texte rentre """
    size = start_size
    min_size = 30
    
    while size > min_size:
        try:
            font = ImageFont.truetype(font_path, size)
        except:
            return ImageFont.load_default(), size

        # On vérifie si la ligne la plus longue dépasse
        max_w_found = 0
        for line in text_lines:
            # Pour PIL, on utilise un dummy draw
            dummy = ImageDraw.Draw(Image.new('RGB', (1, 1)))
            left, top, right, bottom = dummy.textbbox((0, 0), line, font=font)
            line_w = right - left
            if line_w > max_w_found:
                max_w_found = line_w
        
        if max_w_found < (max_width - 100): # Marge de sécurité
            return font, size
        
        size -= 2
    return ImageFont.truetype(font_path, min_size), min_size

def split_arabic_text(text, max_chars=45):
    """ Découpe le texte intelligemment """
    words = text.split()
    lines = []
    current_line = []
    current_len = 0
    
    for word in words:
        # On estime la longueur (approximative)
        if current_len + len(word) > max_chars:
            lines.append(" ".join(current_line))
            current_line = [word]
            current_len = len(word)
        else:
            current_line.append(word)
            current_len += len(word) + 1
            
    if current_line:
        lines.append(" ".join(current_line))
    return lines # Retourne une liste de lignes, pas un string

def creer_clip_texte_pil(texte, font_path, base_size, color, video_size, position_y, is_arabic=False):
    w_video, h_video = video_size
    
    # A. Préparation du Texte & Police
    if is_arabic:
        # 1. On découpe en lignes brutes
        raw_lines = split_arabic_text(texte, max_chars=40)
        
        # 2. On traite chaque ligne individuellement
        processed_lines = []
        for line in raw_lines:
            # UTILISATION DU RESHAPER CONFIGURÉ
            reshaped = reshaper.reshape(line) 
            bidi = get_display(reshaped)
            processed_lines.append(bidi)
        
        final_text = "\n".join(processed_lines)
        alignement = 'center'
        
        # 3. Calcul taille optimale sur les lignes traitées
        font, final_size = get_optimal_font_scale(processed_lines, font_path, w_video, start_size=80)
        
    else:
        # Français
        final_text = textwrap.fill(texte, width=30)
        font = ImageFont.truetype(font_path, 40)
        alignement = 'center'

    # B. Création Image
    img = Image.new('RGBA', (w_video, h_video), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # C. Bounding Box & Fond
    left, top, right, bottom = draw.textbbox((0, 0), final_text, font=font, align=alignement, spacing=15)
    text_width = right - left
    text_height = bottom - top

    x = (w_video - text_width) / 2
    
    padding = 25
    box = [x - padding, position_y - padding, x + text_width + padding, position_y + text_height + padding]
    draw.rectangle(box, fill=(0, 0, 0, 160))

    # D. Dessin Texte (Avec Ombre)
    draw.multiline_text((x+2, position_y+2), final_text, font=font, fill="black", align=alignement, spacing=15)
    draw.multiline_text((x, position_y), final_text, font=font, fill=color, align=alignement, spacing=15)

    return ImageClip(np.array(img))

def create_video(verse_data, background_path, output_filename="output/video_finale.mp4"):
    print(f"🎬 Montage : {verse_data['surah_name']} {verse_data['ayah_number']}")
    try:
        # AUDIO
        print(f"   ⬇️ Audio...")
        audio_clip = AudioFileClip(verse_data['audio_url'])
        duration = audio_clip.duration + 2.0

        # FOND
        if os.path.exists(background_path):
            bg_clip = VideoFileClip(background_path)
            if bg_clip.duration < duration:
                bg_clip = bg_clip.loop(duration=duration)
            else:
                bg_clip = bg_clip.subclip(0, duration)
            bg_clip = bg_clip.resize(height=1920)
            bg_clip = bg_clip.crop(x1=bg_clip.w/2 - 540, y1=0, width=1080, height=1920)
        else:
            bg_clip = ColorClip(size=(1080, 1920), color=(0, 0, 0), duration=duration)

        dark_layer = ColorClip(size=(1080, 1920), color=(0, 0, 0)).set_opacity(0.3).set_duration(duration)

        # TEXTE ARABE
        print("   ✍️ Texte Arabe (Harakat activés)...")
        txt_arabe_clip = creer_clip_texte_pil(
            texte=verse_data['text_ar'],
            font_path=FONT_ARABIC,
            base_size=80, 
            color='white',
            video_size=(1080, 1920),
            position_y=500,
            is_arabic=True
        ).set_duration(duration)

        # TEXTE FRANÇAIS
        print("   ✍️ Texte Français...")
        txt_fr_clip = creer_clip_texte_pil(
            texte=verse_data['text_fr'],
            font_path=FONT_LATIN,
            base_size=40,
            color='#FFD700',
            video_size=(1080, 1920),
            position_y=1100,
            is_arabic=False
        ).set_duration(duration)

        final_video = CompositeVideoClip([bg_clip, dark_layer, txt_arabe_clip, txt_fr_clip])
        final_video = final_video.set_audio(audio_clip)

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

if __name__ == "__main__":
    print("--- 🧪 TEST FINAL (Harakat + Noto) ---")
    verset_reel = get_random_verse()
    if verset_reel['success']:
        bg_test = os.path.join(BASE_DIR, "assets", "backgrounds", "test_video.mp4")
        create_video(verset_reel, bg_test)