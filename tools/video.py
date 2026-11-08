#!/usr/bin/env python3
"""Lager bakgrunnsvideoene i assets/video fra Henriks eksport.

Kjør:  python3 tools/video.py forside "/sti/til/eksport.mp4"

Gir to filer, se også chrome.bg_video():
  <navn>.mp4        960×540 til PC. Videostrømmen kopieres som levert (ingen ny koding),
                    lydsporet fjernes og moov legges først, så den spiller før hele fila er hentet.
  <navn>-mobil.mp4  432×540 til telefon på høykant, kodet på nytt med x264 (crf 26).

En telefon viser bare en stripe på ca. 285 px midt i den 432 px brede mobilfila
(feltet er rundt 375×710, og videoen fyller det med object-fit: cover). Det tilsvarer
kildekolonnene x+73 til x+358, der x er venstre kant av utsnittet. Står hovedpersonen
langt ut til siden i et klipp, havner hun utenfor. UTSNITT gir derfor x per klipp,
regnet fra bildenummeret der klippet begynner (25 bilder i sekundet). Videoer uten
oppføring beskjæres til midten (x = 264).

Første klipp må ha x = 264 på forsiden, for plakaten (forside-plakat.jpg) vises
sentrert før videoen starter. Ellers hopper bildet når videoen begynner.

Bytter Henrik klipp eller rekkefølge, må UTSNITT oppdateres. Finn kuttene med
  ffmpeg -i eksport.mp4 -vf scdet=threshold=8 -an -f null - 2>&1 | grep scd.time
og gang tiden med 25."""
import json, os, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kv

BREDDE, HOYDE, MOBIL = 960, 540, 432
MIDTEN = (BREDDE - MOBIL) // 2

# (første bilde i klippet, x). Forsiden: eksport 08.11.2026, 16 klipp, 1068 bilder. Hver x er
# midtverdien av tre uavhengige vurderinger av hvor hovedmotivet står i klippet.
UTSNITT = {
    'forside': [
        (0, 264),    # lysekronen, må matche plakaten
        (69, 306),   # burgere på passet
        (153, 140),  # servitør ved bordet
        (206, 230),  # servitør med logoen på ryggen
        (245, 270),  # servitør med tallerken
        (322, 195),  # øl og fries i baren
        (378, 470),  # bartender med shaker
        (444, 264),  # full restaurant
        (522, 300),  # passet med kokkene
        (596, 280),  # burgere på stål
        (660, 264),  # veggen med plakatene
        (734, 510),  # gjester som spiser, servitøren
        (791, 144),  # bordet med lyset
        (846, 285),  # servitør i rosa lys
        (942, 115),  # bartender med flaggene
        (993, 270),  # restauranten i bredde
    ],
}


def x_uttrykk(utsnitt):
    """Bygger crop-filterets x-uttrykk, evaluert for hvert bilde (n = bildenummer)."""
    if not utsnitt:
        return str(MIDTEN)
    expr = str(utsnitt[-1][1])
    for (start, x), (neste, _) in reversed(list(zip(utsnitt, utsnitt[1:]))):
        expr = f'if(lt(n,{neste}),{x},{expr})'
    return expr


def sjekk(navn, utsnitt):
    for start, x in utsnitt:
        if not 0 <= x <= BREDDE - MOBIL:
            sys.exit(f'{navn}: x={x} ved bilde {start} er utenfor 0–{BREDDE - MOBIL}')
    if [s for s, _ in utsnitt] != sorted({s for s, _ in utsnitt}) or (utsnitt and utsnitt[0][0] != 0):
        sys.exit(f'{navn}: UTSNITT må begynne på bilde 0 og stige')


def info(fil):
    r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-count_packets',
                        '-show_entries', 'stream=width,height,r_frame_rate,nb_read_packets', '-of', 'json', fil],
                       capture_output=True, text=True, check=True)
    return json.loads(r.stdout)['streams'][0]


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    navn, kilde = sys.argv[1], sys.argv[2]
    s = info(kilde)
    if (s['width'], s['height']) != (BREDDE, HOYDE) or s['r_frame_rate'] != '25/1':
        sys.exit(f'Forventet {BREDDE}×{HOYDE} i 25 bilder/s, fikk {s["width"]}×{s["height"]} i {s["r_frame_rate"]}')
    utsnitt = UTSNITT.get(navn, [])
    sjekk(navn, utsnitt)
    if utsnitt and utsnitt[-1][0] >= int(s['nb_read_packets']):
        sys.exit(f'{navn}: siste klipp i UTSNITT begynner etter at videoen er slutt. Er det en ny eksport?')
    ut = os.path.join(kv.ROOT, 'assets', 'video')
    pc, mobil = os.path.join(ut, f'{navn}.mp4'), os.path.join(ut, f'{navn}-mobil.mp4')
    felles = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', kilde, '-map', '0:v:0', '-an', '-map_metadata', '-1']
    subprocess.run(felles + ['-c:v', 'copy', '-movflags', '+faststart', pc], check=True)
    subprocess.run(felles + ['-vf', f"crop={MOBIL}:{HOYDE}:x='{x_uttrykk(utsnitt)}':y=0",
                             '-c:v', 'libx264', '-preset', 'slow', '-crf', '26', '-profile:v', 'high', '-pix_fmt', 'yuv420p',
                             '-movflags', '+faststart', mobil], check=True)
    for f in (pc, mobil):
        print(f'{os.path.relpath(f, kv.ROOT)}: {os.path.getsize(f) / 1e6:.1f} MB')
    if not utsnitt:
        print('Mobilfila er beskåret til midten. Legg inn UTSNITT hvis noen står langt ut til siden.')


if __name__ == '__main__':
    main()
