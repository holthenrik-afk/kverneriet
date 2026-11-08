#!/usr/bin/env python3
"""Dagen hos Kverneriet: lunsj, middag og late night som en 1-2-3 med klokkeslett (ønske fra Viktor 05.11.2026).

Gjesten skal se med en gang at Kverneriet er mer enn en burger til middag. Stegene går av seg
selv med en linje som fylles, og stopper når gjesten klikker. Uten JavaScript står første steg
åpent, og knappene virker ikke, men lenkene gjør det. Ikke scroll-animasjon: Henrik mener det
er mer pynt enn nytte.

Klokkeslettene er ment som en pekepinn for dagen. De nøyaktige tidene per sted står i
åpningstidene på restaurantsidene.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kv, chrome, i18n_gen as G

e = kv.esc

# nøkkel, side, klokkeslett, tittel, tekst, lenketekst, bilde, alt-tekst – norsk og engelsk.
STEG = [
    ('lunsj', 'lunsj',
     ('Fra kl. 11', 'From 11.00'),
     ('Lunsj', 'Lunch'),
     ('En rask burger midt på dagen, med venner eller med hele jobben.',
      'A quick burger in the middle of the day, with friends or the whole office.'),
     ('Les om lunsj', 'About lunch'),
     '/assets/img/hero-lunsj.jpg',
     ('Gjester på uteserveringen en lys ettermiddag', 'Guests on the terrace on a bright afternoon')),
    ('middag', 'middag',
     ('Fra kl. 16', 'From 16.00'),
     ('Middag', 'Dinner'),
     ('En spontan burger på en tirsdag eller hele vennegjengen på en lørdag.',
      'A spontaneous burger on a Tuesday or the whole gang on a Saturday.'),
     ('Les om middag', 'About dinner'),
     '/assets/img/hero-grupper.jpg',
     ('Servitør på vei til et fullt bord med drikke på brettet', 'A waiter bringing drinks to a full table')),
    ('latenight', 'late-night',
     ('Til sent', 'Until late'),
     ('Late night', 'Late night'),
     ('Når kvelden ikke er over ennå og du vil ha et ordentlig måltid før du går hjem.',
      "When the night isn't over yet and you want a proper meal before heading home."),
     ('Les om late night', 'About late night'),
     '/assets/img/ln-hero.jpg',
     ('Gjester skåler rundt et bord om kvelden', 'Guests raising a toast around a table in the evening')),
]


def section():
    G.add('home.dagEyebrow', 'Fra lunsj til langt på kveld', 'From lunch until late')
    G.add('home.dagTitle', 'Dagen hos Kverneriet', 'A day at Kverneriet')
    G.add('dag.pause', 'Stopp bildene', 'Stop the images'); G.add('dag.play', 'Spill av bildene', 'Play the images')
    rader = ''
    for i, (k, side, tid, tit, tekst, lenke, bilde, alt) in enumerate(STEG):
        p = f'dag.{k}'
        G.add(f'{p}.tid', tid[0], tid[1]); G.add(f'{p}.title', tit[0], tit[1])
        G.add(f'{p}.tekst', tekst[0], tekst[1]); G.add(f'{p}.lenke', lenke[0], lenke[1])
        G.add(f'{p}.alt', alt[0], alt[1])
        aktiv = ' data-aktiv' if i == 0 else ''
        rader += (f'        <div class="dognet__steg" data-dognet-steg{aktiv}>\n'
                  f'          <button class="dognet__knapp" type="button" data-dognet-knapp aria-expanded="{"true" if i == 0 else "false"}" aria-controls="dag-{k}" data-track="dag:{k}">'
                  f'<span class="dognet__linje" aria-hidden="true"><span class="dognet__fyll"></span></span>'
                  f'<span class="dognet__nr" aria-hidden="true">{i + 1}</span>'
                  f'<span class="dognet__tid" data-i18n="{p}.tid">{e(tid[0])}</span>'
                  f'<span class="dognet__navn" data-i18n="{p}.title">{e(tit[0])}</span></button>\n'
                  f'          <figure class="dognet__bilde"><img src="{bilde}" alt="{e(alt[0])}" loading="lazy" decoding="async"></figure>\n'
                  f'          <div class="dognet__tekst" id="dag-{k}">\n'
                  f'            <p data-i18n="{p}.tekst">{e(tekst[0])}</p>\n'
                  f'            <div class="dognet__handling">'
                  f'<button class="btn btn--primary btn--md" type="button" data-book-open data-track="dag:book:{k}" data-i18n="act.book">Book bord</button>'
                  f'<a class="dognet__lenke" href="{kv.url(side)}" data-i18n="{p}.lenke">{e(lenke[0])}</a></div>\n'
                  f'          </div>\n'
                  f'        </div>\n')
    return ('  <section class="section section--flush-top dognet" id="dagen" data-dognet>\n'
            '    <div class="wrap">\n'
            '      <header class="sec-head"><div class="sec-head__rule"></div>'
            '<span class="kv-eyebrow" data-i18n="home.dagEyebrow">Fra lunsj til langt på kveld</span>'
            '<h2 class="display-2" data-i18n="home.dagTitle">Dagen hos Kverneriet</h2></header>\n'
            f'      <div class="dognet__spor">\n{rader}'
            f'        <button class="bg-video__knapp dognet__pause" type="button" data-dognet-pause data-i18n-label="dag.pause" aria-label="Stopp bildene">'
            f'{chrome._IKON_PAUSE}{chrome._IKON_SPILL}</button>\n      </div>\n'
            '    </div>\n  </section>\n')
