"""Titler, beskrivelser og delingsbilde per side – én kilde for <head> (seo-head.py) og for generatorene.
Grenser: tittel ≤ 60 tegn, beskrivelse ≤ 155 tegn (sjekkes ved bygging). Alle på norsk med «burger» + sted."""

PAGES = {
 'index': dict(
    title='Kverneriet – burgerrestaurant i Oslo og Tønsberg',
    desc='Burgere av kjøtt vi kverner selv, fries som tar tre dager. 6 av 6 i Dagbladet. Majorstua og Solli i Oslo, og Tønsberg. Book bord eller ta med.',
    img='/assets/img/index-hero.jpg'),
 'majorstua': dict(
    title='Kverneriet Majorstua – burger på Majorstuen, Oslo',
    desc='Burgerrestaurant i Kirkeveien 64B på Majorstuen. 5 av 6 i Finansavisen og VG. Lunsj tir–fre fra 11, kjøkken til 22, bar til 23. Book bord eller hent selv.',
    img='/assets/img/majorstua-hero.jpg'),
 'solli': dict(
    title='Kverneriet Solli – burger ved Solli plass, Oslo',
    desc='Burgerrestaurant og cocktailbar i Henrik Ibsens gate 100 ved Solli plass. 6 av 6 i Dagbladet. Lunsj tir–fre fra 11.30. Book bord, Wolt eller Foodora.',
    img='/assets/img/solli-hero.jpg'),
 'tonsberg': dict(
    title='Kverneriet Tønsberg – burger på Kaldnes brygge',
    desc='Burgerrestaurant på Kaldnes brygge i Tønsberg, Rambergveien 15, siden 2013. Kjøtt vi kverner selv, fries som tar tre dager, uteservering ved kanalen.',
    img='/assets/img/tonsberg-hero.jpg'),
 'meny': dict(
    title='Meny – burgere, fries og milkshake | Kverneriet',
    desc='Menyene på Majorstua, Solli og i Tønsberg: burgere av kjøtt vi kverner selv, trippelkokte fries, hot wings, soft serve og milkshakes. Priser og allergener.',
    img='/assets/img/trio-majorstua.jpg'),
 'majorstua-menu': dict(
    title='Meny Kverneriet Majorstua – burgere, fries og milkshake',
    desc='Menyen på Kverneriet Majorstua med priser og allergener: burgere med 150 g kjøtt vi kverner selv, trippelkokte fries, hot wings, soft serve og milkshakes.',
    img='/assets/img/trio-majorstua.jpg'),
 'solli-menu': dict(
    title='Meny Kverneriet Solli – burgere, fries og milkshake',
    desc='Menyen på Kverneriet Solli med priser og allergener: burgere med 150 g kjøtt vi kverner selv, trippelkokte fries, hot wings, soft serve og milkshakes.',
    img='/assets/img/meny-solli.jpg'),
 'tonsberg-menu': dict(
    title='Meny Kverneriet Tønsberg – burgere, fries og milkshake',
    desc='Menyen på Kverneriet Tønsberg med priser og allergener: burgere med 150 g kjøtt vi kverner selv, trippelkokte fries, salater, soft serve og milkshakes.',
    img='/assets/img/meny-tonsberg.jpg'),
 'takeaway': dict(
    title='Take-away burger i Oslo og Tønsberg – Kverneriet',
    desc='Oslos beste take-away-burger ifølge Finansavisen, 6 av 6 i Dagbladet. Hent selv på Majorstua, Solli eller i Tønsberg, eller få levert med Wolt og Foodora.',
    img='/assets/img/ta-hero.jpg'),
 'lunsj': dict(
    title='Burgerlunsj på Majorstuen, Solli og i Tønsberg – Kverneriet',
    desc='Lunsj med burger: kjøkkenet åpner 11 på Majorstua, 11.30 på Solli og 12 tor–søn i Tønsberg. Kjøtt vi kverner selv, fries som tar tre dager. Book bord.',
    img='/assets/img/tonsberg-about.jpg'),
 'julebord': dict(
    title='Julebord med burgere i Oslo og Tønsberg – Kverneriet',
    desc='Julebord uten ribbe: matpakker fra 429 kr per person for grupper over 8 (7 i Tønsberg) på Majorstua, Solli og i Tønsberg. Send forespørsel til oss.',
    img='/assets/img/solli-hero.jpg'),
 'selskap': dict(
    title='Selskap og gruppebooking – burger i Oslo og Tønsberg',
    desc='Bursdag, firmafest eller vennegjeng? Grupper over 8 (7 i Tønsberg) velger matpakke fra 429 kr på Majorstua, Solli eller i Tønsberg. Send forespørsel.',
    img='/assets/img/tonsberg-hero.jpg'),
 'late-night': dict(
    title='Late night burger i Oslo – kjøkken til 22 | Kverneriet',
    desc='Spise sent i Oslo? Kjøkkenet på Majorstua og Solli serverer burgere til 22, baren holder åpent til 23 tir–lør. Milkshake med sprit, øl fra tappen. Drop-in.',
    img='/assets/img/ln-hero.jpg'),
}

def check():
    for k, p in PAGES.items():
        assert len(p['title']) <= 60, f'{k}: tittel {len(p["title"])} tegn'
        assert len(p['desc']) <= 155, f'{k}: beskrivelse {len(p["desc"])} tegn'
check()
