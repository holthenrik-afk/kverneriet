/* Kverneriet — site behaviour. No frameworks. Motion is short and flat (DS); the only scroll-driven thing is a
   one-time 240 ms fade-in of card groups, and it only runs where IntersectionObserver exists. */
(function(){
  'use strict';

  /* ---------- Language (Norwegian default, English via the header toggle) ---------- */
  var LANG='no';
  try{LANG=localStorage.getItem('kv-lang')||'no';}catch(e){}
  if(LANG!=='no'&&LANG!=='en')LANG='no';

  function dict(){
    var base=(window.KV_I18N&&window.KV_I18N[LANG])||{};
    var gen=(window.KV_I18N_GEN&&window.KV_I18N_GEN[LANG])||{};
    var d={};for(var k in base)d[k]=base[k];for(var g in gen)d[g]=gen[g];return d;
  }
  function t(key){return dict()[key];}
  function applyLang(lang){
    LANG=lang==='en'?'en':'no';
    try{localStorage.setItem('kv-lang',LANG);}catch(e){}
    document.documentElement.lang=LANG==='en'?'en':'nb';
    var d=dict();
    document.querySelectorAll('[data-i18n]').forEach(function(el){
      var s=d[el.getAttribute('data-i18n')];
      if(s===undefined)return;
      if(el.hasAttribute('data-i18n-n'))s=s.split('{n}').join(el.getAttribute('data-i18n-n'));
      el.textContent=s;
      if(el.hasAttribute('data-label'))el.setAttribute('data-label',s);
    });
    document.querySelectorAll('[data-i18n-title]').forEach(function(el){
      var s=d[el.getAttribute('data-i18n-title')];
      if(s!==undefined)el.setAttribute('title',s);
    });
    document.querySelectorAll('[data-i18n-ph]').forEach(function(el){
      var s=d[el.getAttribute('data-i18n-ph')];
      if(s!==undefined)el.setAttribute('placeholder',s);
    });
    document.querySelectorAll('[data-i18n-label]').forEach(function(el){
      var s=d[el.getAttribute('data-i18n-label')];
      if(s!==undefined)el.setAttribute('aria-label',s);
    });
    document.querySelectorAll('[data-i18n-html]').forEach(function(el){
      var s=d[el.getAttribute('data-i18n-html')];
      if(s!==undefined)el.innerHTML=s;
    });
    document.querySelectorAll('.lang-switch [data-lang]').forEach(function(b){
      var on=b.getAttribute('data-lang')===LANG;
      b.classList.toggle('is-on',on);b.setAttribute('aria-pressed',on?'true':'false');
    });
    document.dispatchEvent(new CustomEvent('kv:lang',{detail:{lang:LANG}}));
  }
  window.KVGetLang=function(){return LANG;};
  window.KVT=function(key){return t(key);};
  document.addEventListener('click',function(e){
    var b=e.target.closest('.lang-switch [data-lang]');
    if(b)applyLang(b.getAttribute('data-lang'));
  });

  /* ---------- Sporing ----------
     Alle konverteringsknapper og utgående bestillingslenker har data-track="kategori:sted:kanal".
     Klikk pushes til window.dataLayer, sendes til GA4 med gtag (taggen settes inn av
     tools/chrome.py) og som et kv:track-event. OrderX-lenkene bærer i tillegg UTM-parametre. */
  window.dataLayer=window.dataLayer||[];
  var VENUE_RE=/^(majorstua|solli|tonsberg)$/;
  function ga(name,params){if(typeof window.gtag==='function')window.gtag('event',name,params);meta(name,params);}
  /* De samme hendelsene går til Meta-pikselen. fbq finnes bare når gjesten har sagt ja til
     informasjonskapsler. Schedule, Lead og Contact er Metas standardhendelser, resten er egne.
     BookingStarted sendes én gang per side. */
  var META={booking_created:'Schedule',group_request:'Lead',click_call:'Contact',open_booking:'OpenBooking',
    open_group_booking:'OpenGroupBooking',zc_choose_pax:'BookingStarted',zc_choose_date:'BookingStarted',
    zc_choose_slot:'BookingSlotChosen',click_takeaway:'TakeawayClick',click_giftcard:'GiftcardClick'};
  var META_STD={Schedule:1,Lead:1,Contact:1},metaOnce={};
  function meta(name,params){
    var ev=META[name];if(!ev||typeof window.fbq!=='function')return;
    if(ev==='BookingStarted'){if(metaOnce[ev])return;metaOnce[ev]=1;}
    var d={content_name:(params&&params.kv_venue)||pageVenue()};
    if(params&&params.guests!=null)d.num_guests=params.guests;
    window.fbq(META_STD[ev]?'track':'trackCustom',ev,d);
  }
  function gaName(parts){
    var s=parts.join(':');
    if(parts[0]==='order')return 'click_takeaway';
    if(parts[0]==='booking'&&parts[2]==='group')return 'group_request';
    if(/:group$/.test(s))return 'open_group_booking';
    if(/(^|:)book(:|$)/.test(s))return 'open_booking';
    if(/(^|:)takeaway(:|$)/.test(s))return 'open_takeaway';
    if(parts[0]==='giftcard')return 'click_giftcard';
    if(parts[0]==='media')return 'click_press';
    return 'kv_click';
  }
  function pageVenue(){return document.body.getAttribute('data-venue')||'';}
  function track(name,extra){
    var parts=String(name).split(':');
    var payload={event:'kv_click',kv_action:parts[0]||'',kv_venue:parts[1]||'',kv_channel:parts[2]||'',kv_page:location.pathname||'index.html',kv_lang:LANG};
    if(extra)for(var k in extra)payload[k]=extra[k];
    window.dataLayer.push(payload);
    var venue=parts.filter(function(p){return VENUE_RE.test(p);})[0]||pageVenue();
    ga(gaName(parts),{kv_track:String(name),kv_venue:venue,kv_channel:parts[2]||'',kv_page:payload.kv_page});
    document.dispatchEvent(new CustomEvent('kv:track',{detail:payload}));
  }
  window.KVTrack=track;
  document.addEventListener('click',function(e){
    var el=e.target.closest('[data-track]');
    if(el){track(el.getAttribute('data-track'));return;}
    var tel=e.target.closest('a[href^="tel:"]');
    if(tel)ga('click_call',{kv_venue:pageVenue(),kv_page:location.pathname});
  },true);

  /* Zenchef-rammen i bookingen sender hendelser til siden med postMessage (zcf-bookings-*). De
     sendes videre til GA4 med rene navn. booking_created er hovedmålet og arver kilden (UTM, gclid)
     fra besøket. Bare antall gjester, dato og tid følger med, aldri noe om gjesten. */
  var ZC_EVENTS={'zcf-bookings-booking_created':'booking_created','zcf-bookings-choose_pax':'zc_choose_pax',
    'zcf-bookings-choose_date':'zc_choose_date','zcf-bookings-choose_slot':'zc_choose_slot',
    'zcf-bookings-choose_room':'zc_choose_room','zcf-bookings-open_calendar':'zc_open_calendar'};
  var ZC_FIELDS={pax:'guests',nb_guests:'guests',date:'zc_date',day:'zc_date',time:'zc_time',slot:'zc_time'};
  window.addEventListener('message',function(e){
    if(e.origin!=='https://bookings.zenchef.com'||!e.data||typeof e.data!=='object')return;
    var name=ZC_EVENTS[e.data.type];if(!name)return;
    var venue='';
    Array.prototype.forEach.call(document.querySelectorAll('.bk-frame iframe'),function(f){if(f.contentWindow===e.source)venue=f.getAttribute('data-venue')||'';});
    var p={kv_venue:venue||pageVenue(),kv_page:location.pathname},d=e.data.data||{};
    for(var k in ZC_FIELDS){var v=d[k];if(typeof v==='number'||(typeof v==='string'&&v.length<=20))p[ZC_FIELDS[k]]=v;}
    window.dataLayer.push({event:name,kv_venue:p.kv_venue});
    ga(name,p);
  });

  /* Samtykke: banneret vises til gjesten har valgt. Valget lagres i localStorage («kv-consent») og
     leses av Google-taggen i <head>. Meta-pikselen lastes bare etter ja. */
  var consentBox=document.querySelector('.consent');
  function loadMeta(){
    if(window.fbq)return;
    var n=window.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments);};
    if(!window._fbq)window._fbq=n;n.push=n;n.loaded=true;n.version='2.0';n.queue=[];
    var s=document.createElement('script');s.async=true;s.src='https://connect.facebook.net/en_US/fbevents.js';
    document.head.appendChild(s);
    window.fbq('init','1328532094743171');window.fbq('track','PageView');
  }
  function applyConsent(v){
    var g=v==='granted'?'granted':'denied';
    if(typeof window.gtag==='function')window.gtag('consent','update',{ad_storage:g,ad_user_data:g,ad_personalization:g,analytics_storage:g});
    if(v==='granted')loadMeta();
    else if(typeof window.fbq==='function')window.fbq('consent','revoke');
  }
  var stored=null;try{stored=localStorage.getItem('kv-consent');}catch(e){}
  if(stored==='granted')loadMeta();
  if(consentBox&&stored!=='granted'&&stored!=='denied')consentBox.hidden=false;
  document.addEventListener('click',function(e){
    var b=e.target.closest('[data-consent]');
    if(b){var v=b.getAttribute('data-consent');try{localStorage.setItem('kv-consent',v);}catch(err){}applyConsent(v);if(consentBox)consentBox.hidden=true;return;}
    if(e.target.closest('[data-consent-open]')&&consentBox){consentBox.hidden=false;var f=consentBox.querySelector('button');if(f)f.focus();}
  });

  /* Sticky offsets: measure the real header so section navs and anchors line up. */
  var header=document.querySelector('.site-header');
  function setStickTop(){
    if(header){document.documentElement.style.setProperty('--stick-top',header.offsetHeight+'px');}
    var navStack=document.querySelector('.nav-stack')||document.querySelector('.section-nav');
    if(navStack){document.documentElement.style.setProperty('--nav-h',navStack.offsetHeight+'px');}
  }
  setStickTop();
  window.addEventListener('resize',setStickTop);

  /* Book / take-away modal. One entry point, two modes. */
  var modal=document.getElementById('order-modal');
  var lastFocus=null;
  var modalMode='book';
  function setModalMode(mode){
    modalMode=mode==='ta'?'ta':'book';
    var seg=document.getElementById('action-mode');
    if(seg)Array.prototype.forEach.call(seg.querySelectorAll('button'),function(b){
      var on=b.getAttribute('data-amode')===modalMode;b.classList.toggle('is-on',on);b.setAttribute('aria-pressed',on?'true':'false');
    });
    var book=document.getElementById('modal-book');
    var ta=document.getElementById('modal-ta');
    if(book)book.hidden=modalMode!=='book';
    if(ta)ta.hidden=modalMode!=='ta';
    var title=document.getElementById('order-title');
    if(title){var s=t(modalMode==='book'?'act.book':'modal.title');if(s)title.textContent=s;}
  }
  function setModalVenue(slug){
    if(!modal)return;
    if(!/^(majorstua|solli|tonsberg)$/.test(slug||''))slug='';
    var seg=document.getElementById('modal-venue');
    if(seg)Array.prototype.forEach.call(seg.querySelectorAll('button'),function(b){var on=b.getAttribute('data-mvenue')===slug;b.classList.toggle('is-on',on);b.setAttribute('aria-pressed',on?'true':'false');});
    var bk=modal.querySelector('.bk');
    if(bk&&bk._kv)bk._kv.setVenue(slug);
    modal.classList.toggle('is-novenue',!slug);
    var taPick=document.getElementById('modal-ta-pick');
    if(taPick)taPick.hidden=!!slug;
    Array.prototype.forEach.call(modal.querySelectorAll('#modal-ta .order-group[data-venue]'),function(g){g.hidden=g.getAttribute('data-venue')!==slug;});
  }
  function openModal(mode,opts){
    if(!modal)return;
    opts=opts||{};
    setModalMode(mode);
    setModalVenue(opts.venue||document.body.getAttribute('data-venue')||'');
    var bk=modal.querySelector('.bk');
    if(bk&&bk._kv){
      bk._kv.setMode(opts.bookMode||'online');
      bk._kv.reset();
    }
    lastFocus=document.activeElement;
    modal.classList.add('is-open');
    document.body.style.overflow='hidden';
    if(bk&&bk._kv&&bk._kv.loadFrame)bk._kv.loadFrame();
    var close=modal.querySelector('.modal__close');
    if(close)close.focus();
  }
  function closeModal(){
    if(!modal)return;
    modal.classList.remove('is-open');
    document.body.style.overflow='';
    if(lastFocus)lastFocus.focus();
  }
  document.addEventListener('click',function(e){
    var book=e.target.closest('[data-book-open]');
    if(book){e.preventDefault();openModal('book',{venue:book.getAttribute('data-book-venue'),bookMode:book.getAttribute('data-book-mode')});return;}
    var opener=e.target.closest('[data-order-open]');
    if(opener){e.preventDefault();openModal('ta');return;}
    var amode=e.target.closest('#action-mode [data-amode]');
    if(amode){setModalMode(amode.getAttribute('data-amode'));return;}
    var mvenue=e.target.closest('#modal-venue [data-mvenue]');
    if(mvenue){setModalVenue(mvenue.getAttribute('data-mvenue'));return;}
    if(modal&&modal.classList.contains('is-open')&&e.target.closest('#modal-ta a[href]')){closeModal();return;}
    if(e.target.closest('[data-order-close]')){e.preventDefault();closeModal();}
  });
  document.addEventListener('kv:lang',function(){setModalMode(modalMode);});
  var modalParam=new URLSearchParams(location.search).get('modal');
  if(modalParam==='book'||modalParam==='ta')openModal(modalParam);
  document.addEventListener('keydown',function(e){
    if(e.key==='Escape'){closeModal();closeMobile();}
  });

  /* Mobile / overflow menu */
  var panel=document.getElementById('mobile-panel');
  var panelBtn=document.getElementById('menu-toggle');
  function closeMobile(){if(panel){panel.classList.remove('is-open');if(panelBtn){panelBtn.setAttribute('aria-expanded','false');panelBtn.classList.remove('is-open');}}}
  if(panelBtn&&panel){
    panelBtn.addEventListener('click',function(){
      var open=panel.classList.toggle('is-open');
      panelBtn.setAttribute('aria-expanded',open?'true':'false');
      panelBtn.classList.toggle('is-open',open);
    });
    document.addEventListener('click',function(e){
      if(!e.target.closest('#mobile-panel')&&!e.target.closest('#menu-toggle'))closeMobile();
    });
  }

  /* Scrollspy for sticky section navs. Re-scannable: pages that render their nav at
     runtime call window.KVSpyRefresh() after each render. */
  var spyNav=document.querySelector('[data-scrollspy]');
  var spyLinks=[],spySections=[],spyCurrent=null;
  function spySetActive(id){
    spyLinks.forEach(function(a){a.classList.toggle('is-active',a.getAttribute('href')==='#'+id);});
    var active=spyLinks.filter(function(a){return a.getAttribute('href')==='#'+id;})[0];
    if(active&&active.scrollIntoView){active.scrollIntoView({block:'nearest',inline:'nearest'});}
  }
  function spyOnScroll(){
    if(!spySections.length)return;
    var stack=document.querySelector('.nav-stack')||document.querySelector('.section-nav');
    var offset=(header?header.offsetHeight:64)+(stack?stack.offsetHeight:56)+64;
    var id=spyCurrent;
    for(var i=0;i<spySections.length;i++){
      if(spySections[i].getBoundingClientRect().top-offset<=0)id=spySections[i].id;
    }
    if(!id)id=spySections[0].id;
    if(id!==spyCurrent){spyCurrent=id;spySetActive(id);}
  }
  function spyRefresh(){
    if(!spyNav)return;
    spyLinks=Array.prototype.slice.call(spyNav.querySelectorAll('a[href^="#"]'));
    spySections=spyLinks.map(function(a){return document.getElementById(a.getAttribute('href').slice(1));}).filter(Boolean);
    spyCurrent=null;
    if(spySections.length){spyOnScroll();if(!spyCurrent){spyCurrent=spySections[0].id;spySetActive(spyCurrent);}}
  }
  if(spyNav){
    window.addEventListener('scroll',spyOnScroll,{passive:true});
    spyRefresh();
  }
  window.KVSpyRefresh=spyRefresh;

  /* Booking (.bk): restaurantvelger, online booking (Zenchef i en ramme inne i modalen – samme
     løsning som kverneriet.com bruker i dag) og større grupper (forespørsel som åpnes ferdig utfylt i
     e-postprogrammet, siden siden er statisk uten backend). Én instans i modalen og én i #booking på
     hver restaurantside. */
  var VENUE_NAMES={majorstua:'Majorstua',solli:'Solli',tonsberg:'Tønsberg'};
  function wireBooking(root){
    var venueSeg=root.querySelector('.bk-venue');
    var modeSeg=root.querySelector('.bk-mode');
    var online=root.querySelector('.bk-online');
    var large=root.querySelector('.bk-large');
    var sent=root.querySelector('.bk-sent');
    var frame=root.querySelector('.bk-frame');
    var zcLink=root.querySelector('.bk-zenchef-link');
    function zenchefUrl(slug){return root.getAttribute('data-zenchef-'+slug)||'';}
    function loadFrame(){
      if(!frame||online.hidden||root.offsetParent===null)return;
      var slug=root.getAttribute('data-venue');
      if(!slug)return;
      var url=zenchefUrl(slug);
      if(!url)return;
      var cur=frame.querySelector('iframe');
      if(cur&&cur.getAttribute('data-venue')===slug)return;
      url=url.replace(/lang=no/, 'lang='+(window.KVGetLang&&window.KVGetLang()==='en'?'en':'no'));
      frame.innerHTML='<iframe src="'+url+'" title="Online booking – Kverneriet '+(VENUE_NAMES[slug]||'')+'" loading="lazy" data-venue="'+slug+'" allow="payment"></iframe>';
      frame.classList.add('is-loaded');
    }
    var api={
      setVenue:function(slug){
        if(!VENUE_NAMES[slug])slug='';
        root.setAttribute('data-venue',slug);
        root.classList.toggle('bk--novenue',!slug);
        if(venueSeg)Array.prototype.forEach.call(venueSeg.querySelectorAll('button'),function(b){var on=!!slug&&b.getAttribute('data-bvenue')===slug;b.classList.toggle('is-on',on);b.setAttribute('aria-pressed',on?'true':'false');});
        if(zcLink&&slug&&zenchefUrl(slug))zcLink.setAttribute('href',zenchefUrl(slug));
        var fb=root.querySelector('.bk-zenchef-fallback');if(fb)fb.hidden=!slug;
        var pick=root.querySelector('.bk-pick');if(pick)pick.hidden=!!slug;
        var sb=large&&large.querySelector('button[type="submit"]');if(sb)sb.disabled=!slug;
        var intro=root.querySelector('.bk-online__intro');var thr=slug&&root.getAttribute('data-threshold-'+slug);
        if(intro){
          if(thr){intro.setAttribute('data-i18n','book.onlineIntro');intro.setAttribute('data-i18n-n',thr);var txt=t('book.onlineIntro');if(txt)intro.textContent=txt.split('{n}').join(thr);}
          else{intro.setAttribute('data-i18n','book.pickVenue');intro.removeAttribute('data-i18n-n');var p=t('book.pickVenue');if(p)intro.textContent=p;}
        }
        if(!slug&&frame){frame.innerHTML='';frame.classList.remove('is-loaded');}
        loadFrame();
      },
      setMode:function(mode){
        mode=mode==='large'?'large':'online';
        if(modeSeg)Array.prototype.forEach.call(modeSeg.querySelectorAll('button'),function(b){var on=b.getAttribute('data-mode')===mode;b.classList.toggle('is-on',on);b.setAttribute('aria-pressed',on?'true':'false');});
        if(online)online.hidden=mode!=='online';
        if(large)large.hidden=mode!=='large';
        if(sent)sent.hidden=true;
        loadFrame();
      },
      loadFrame:loadFrame,
      reset:function(){
        if(sent)sent.hidden=true;
        var on=modeSeg&&modeSeg.querySelector('button.is-on');
        api.setMode(on?on.getAttribute('data-mode'):'online');
      }
    };
    root._kv=api;
    if(venueSeg)venueSeg.addEventListener('click',function(e){var b=e.target.closest('[data-bvenue]');if(b)api.setVenue(b.getAttribute('data-bvenue'));});
    if(modeSeg)modeSeg.addEventListener('click',function(e){var b=e.target.closest('[data-mode]');if(b)api.setMode(b.getAttribute('data-mode'));});
    function wire(form){
      if(!form)return;
      form.addEventListener('submit',function(e){
        e.preventDefault();
        if(!form.reportValidity())return;
        var btn=form.querySelector('button[type="submit"]');
        if(btn){btn.disabled=true;btn.textContent=t('f.sending')||'…';}
        var src=form.querySelector('[name="source"]');var nl=form.querySelector('[name="newsletter"]');
        var venue=root.getAttribute('data-venue');
        if(!venue){var vs=root.querySelector('.bk-venue button');if(vs)vs.focus();return;}
        track('booking:'+venue+':'+(form===large?'group':'online'),{kv_source:src?src.value:'',kv_newsletter:nl?!!nl.checked:false});
        if(form===large){
          var to=root.getAttribute('data-email-'+venue)||'book.major@kverneriet.com';
          var f=function(n){var el=form.querySelector('[name="'+n+'"]');return (el&&el.value)||'–';};
          var body=['Gruppeforespørsel – Kverneriet '+VENUE_NAMES[venue],'','Navn: '+f('name'),'Telefon: '+f('phone'),'E-post: '+f('email'),'Dato: '+f('date'),'Tidligste start: '+f('earliest'),'Seneste start: '+f('latest'),'Antall gjester: '+f('guests'),'Matpakke: '+f('package'),'Barnemenyer: '+f('kids'),'Anledning: '+f('occasion'),'Andre ønsker: '+f('request'),'Hørte om oss via: '+f('source'),'Nyhetsbrev: '+(nl&&nl.checked?'ja':'nei'),'','(Sendt fra kverneriet.com)'].join('\n');
          window.location.href='mailto:'+to+'?subject='+encodeURIComponent('Gruppeforespørsel '+f('date')+' – '+f('guests')+' gjester')+'&body='+encodeURIComponent(body);
        }
        window.setTimeout(function(){
          if(btn){btn.disabled=false;btn.textContent=btn.getAttribute('data-label')||btn.textContent;}
          if(online)online.hidden=true;
          if(large)large.hidden=true;
          if(sent){
            sent.hidden=false;
            var badge=sent.querySelector('.badge');
            if(badge){var base=t('book.sentBadge')||'Forespørsel sendt';badge.textContent=base+' – Kverneriet '+VENUE_NAMES[venue];}
          }
        },600);
      });
    }
    wire(large);
    var today=new Date();var iso=today.getFullYear()+'-'+String(today.getMonth()+1).padStart(2,'0')+'-'+String(today.getDate()).padStart(2,'0');
    Array.prototype.forEach.call(root.querySelectorAll('input[type="date"]'),function(i){i.setAttribute('min',iso);if(!i.value)i.value=iso;});
    var again=root.querySelector('.bk-again');
    if(again)again.addEventListener('click',function(){api.reset();});
    api.setVenue(root.getAttribute('data-venue')||document.body.getAttribute('data-venue')||'');
  }
  Array.prototype.forEach.call(document.querySelectorAll('.bk'),wireBooking);
  document.addEventListener('kv:lang',function(){
    Array.prototype.forEach.call(document.querySelectorAll('.bk .bk-sent:not([hidden]) .badge'),function(b){
      var root=b.closest('.bk');var v=root.getAttribute('data-venue');if(!v)return;
      b.textContent=(t('book.sentBadge')||'')+' – Kverneriet '+VENUE_NAMES[v];
    });
  });

  /* Rolig inntoning av kortgrupper første gang de kommer i syne (én gang, kort, flat).
     Grupper som allerede er i viewporten ved lasting vises med en gang. */
  if('IntersectionObserver' in window&&!window.matchMedia('(prefers-reduced-motion: reduce)').matches){
    var groups=document.querySelectorAll('.venue-trio,.grid-3,.occ-grid,.gallery-grid,.media-scroller,.faq');
    var io=new IntersectionObserver(function(entries){
      entries.forEach(function(en){if(en.isIntersecting){en.target.classList.add('is-in');io.unobserve(en.target);}});
    },{rootMargin:'0px 0px -10% 0px',threshold:0.05});
    Array.prototype.forEach.call(groups,function(g){
      var r=g.getBoundingClientRect();
      if(r.top<window.innerHeight&&r.bottom>0)return;
      g.classList.add('reveal');io.observe(g);
    });
  }

  /* Hero-video: ren dekor. Lastes bare der den gir noe – ikke på smale skjermer, ikke for
     dem som har slått av bevegelse, og ikke i strømsparemodus der autoplay uansett nektes. */
  (function(){
    var v=document.querySelector('[data-hero-video]');
    if(!v)return;
    var still=window.matchMedia('(prefers-reduced-motion: reduce)');
    var bred=window.matchMedia('(min-width: 760px)');
    var startet=false;
    function start(){
      if(startet||still.matches||!bred.matches)return;
      startet=true;
      ['/assets/video/hero.webm|video/webm','/assets/video/hero.mp4|video/mp4'].forEach(function(d){
        var p=d.split('|'),s=document.createElement('source');
        s.src=p[0];s.type=p[1];v.appendChild(s);
      });
      v.load();
      var spill=v.play();
      if(spill&&spill.catch)spill.catch(function(){});
    }
    if('requestIdleCallback' in window)requestIdleCallback(start,{timeout:1800});
    else window.setTimeout(start,900);
    document.addEventListener('visibilitychange',function(){
      if(!startet)return;
      document.hidden?v.pause():v.play().catch(function(){});
    });
  })();

  /* Karusellene: piler, prikker og tastatur. Sporet scroller allerede uten JS. */
  Array.prototype.forEach.call(document.querySelectorAll('[data-kar]'),function(rot){
    var spor=rot.querySelector('.kar__spor');
    var kort=Array.prototype.slice.call(spor.children);
    var prikker=Array.prototype.slice.call(rot.querySelectorAll('[data-kar-goto]'));
    if(kort.length<2){var st=rot.querySelector('.kar__styring');if(st)st.hidden=true;return;}
    var cur=0;
    function mark(i){cur=i;prikker.forEach(function(d,j){
      if(j===i)d.setAttribute('aria-current','true');else d.removeAttribute('aria-current');});}
    function go(i){
      i=Math.max(0,Math.min(kort.length-1,i));
      spor.scrollTo({left:kort[i].offsetLeft-spor.offsetLeft,behavior:'smooth'});mark(i);
    }
    var p=rot.querySelector('[data-kar-prev]'),n=rot.querySelector('[data-kar-next]');
    if(p)p.addEventListener('click',function(){go(cur-1);});
    if(n)n.addEventListener('click',function(){go(cur+1);});
    prikker.forEach(function(d,i){d.addEventListener('click',function(){go(i);});});
    var t;
    spor.addEventListener('scroll',function(){
      window.clearTimeout(t);
      t=window.setTimeout(function(){
        var v=spor.scrollLeft+spor.clientWidth/2,best=0,bd=Infinity;
        kort.forEach(function(k,i){
          var c=k.offsetLeft-spor.offsetLeft+k.offsetWidth/2,d=Math.abs(c-v);
          if(d<bd){bd=d;best=i;}});
        if(best!==cur)mark(best);
      },90);
    },{passive:true});
    spor.addEventListener('keydown',function(e){
      if(e.key==='ArrowRight'){e.preventDefault();go(cur+1);}
      else if(e.key==='ArrowLeft'){e.preventDefault();go(cur-1);}
    });
    mark(0);
  });

  /* ---------- Søk i spørsmålene (/sporsmal/) ----------
     Filtrerer <details>-radene mens gjesten skriver. Søkestrengen i data-sok inneholder
     spørsmål og svar på begge språk pluss synonymer fra faq.SOKEORD, så «hund», «dog» og
     «hundevennlig» treffer det samme. Æ, ø og å foldes ned, slik at «apent» finner «åpent».
     Uten JavaScript står alle spørsmålene åpne for filtrering, som før. */
  (function(){
    var rot=document.querySelector('[data-faq-sok]');
    if(!rot)return;
    var felt=rot.querySelector('input');
    var tomKnapp=rot.querySelector('[data-faq-tom]');
    var status=rot.querySelector('[data-faq-status]');
    var seksjon=document.getElementById('faq');
    var tomt=document.querySelector('[data-faq-tomt]');
    var rader=[].slice.call(document.querySelectorAll('.faq__item[data-sok]'));
    var grupper=[].slice.call(document.querySelectorAll('.faq-gruppe'));
    if(!felt||!rader.length)return;

    function flat(s){
      return String(s).toLowerCase()
        .replace(/[æä]/g,'ae').replace(/[øö]/g,'o').replace(/å/g,'a')
        .replace(/[éèê]/g,'e').replace(/[^a-z0-9 ]+/g,' ')
        .replace(/\s+/g,' ').trim();
    }
    function ordliste(s){var o=flat(s);return o?o.split(' '):[];}
    rader.forEach(function(r){
      r.kvSterk=ordliste(r.getAttribute('data-sok'));        /* spørsmål + synonymer */
      r.kvSvak=ordliste(r.getAttribute('data-sok-tekst'));   /* selve svaret */
    });
    /* Sterkt lag godtar ordstart, svakt lag krever hele ord. Ellers finner «hund»
       også «hundrevis», og «bar» finner «barnemeny». */
    function treffer(r,o){
      var i;
      for(i=0;i<r.kvSterk.length;i++)if(r.kvSterk[i].lastIndexOf(o,0)===0)return true;
      for(i=0;i<r.kvSvak.length;i++)if(r.kvSvak[i]===o)return true;
      return false;
    }

    var apnet=[];
    function lukkApnede(){apnet.forEach(function(r){r.open=false;});apnet=[];}

    function kjor(){
      var raa=felt.value||'';
      if(tomKnapp)tomKnapp.hidden=!raa;
      var q=flat(raa);
      if(!q){
        lukkApnede();
        rader.forEach(function(r){r.hidden=false;});
        grupper.forEach(function(g){g.hidden=false;});
        if(seksjon)seksjon.classList.remove('is-sok');
        if(tomt)tomt.hidden=true;
        if(status)status.textContent='';
        return;
      }
      var ord=q.split(' ');
      var treff=0;
      lukkApnede();
      rader.forEach(function(r){
        var ok=ord.every(function(o){return treffer(r,o);});
        r.hidden=!ok;
        if(ok){treff++;if(!r.open){r.open=true;apnet.push(r);}}
      });
      grupper.forEach(function(g){g.hidden=!g.querySelector('.faq__item:not([hidden])');});
      if(seksjon)seksjon.classList.add('is-sok');
      if(tomt)tomt.hidden=treff>0;
      if(status){
        var mal=(window.KVT&&window.KVT('faq.sokTreff'))||'';
        status.textContent=treff&&mal?mal.split('{n}').join(treff).split('{m}').join(rader.length):'';
      }
    }

    var timer=null;
    felt.addEventListener('input',function(){clearTimeout(timer);timer=setTimeout(kjor,120);});
    felt.addEventListener('keydown',function(e){
      if(e.key==='Escape'){felt.value='';kjor();}
      else if(e.key==='Enter')e.preventDefault();
    });
    if(tomKnapp)tomKnapp.addEventListener('click',function(){felt.value='';kjor();felt.focus();});
    document.addEventListener('kv:lang',function(){if(felt.value)kjor();});
  })();

  /* Apply the stored language once the DOM is in place */
  applyLang(LANG);
})();
