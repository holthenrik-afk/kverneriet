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
     Klikk pushes til window.dataLayer (Google Tag Manager / GA4 leser derfra) og som et
     kv:track-event. Sett inn GTM-containeren i <head> når kontoen er klar; ingenting annet
     må endres. OrderX-lenkene bærer i tillegg UTM-parametre. */
  window.dataLayer=window.dataLayer||[];
  function track(name,extra){
    var parts=String(name).split(':');
    var payload={event:'kv_click',kv_action:parts[0]||'',kv_venue:parts[1]||'',kv_channel:parts[2]||'',kv_page:location.pathname||'index.html',kv_lang:LANG};
    if(extra)for(var k in extra)payload[k]=extra[k];
    window.dataLayer.push(payload);
    document.dispatchEvent(new CustomEvent('kv:track',{detail:payload}));
  }
  window.KVTrack=track;
  document.addEventListener('click',function(e){
    var el=e.target.closest('[data-track]');
    if(el)track(el.getAttribute('data-track'));
  },true);

  /* Sticky offsets: measure the real header so section navs and anchors line up. */
  var header=document.querySelector('.site-header');
  function setStickTop(){
    if(header){document.documentElement.style.setProperty('--stick-top',header.offsetHeight+'px');}
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
    if(!/^(majorstua|solli|tonsberg)$/.test(slug||''))slug='majorstua';
    var seg=document.getElementById('modal-venue');
    if(seg)Array.prototype.forEach.call(seg.querySelectorAll('button'),function(b){var on=b.getAttribute('data-mvenue')===slug;b.classList.toggle('is-on',on);b.setAttribute('aria-pressed',on?'true':'false');});
    var bk=modal.querySelector('.bk');
    if(bk&&bk._kv)bk._kv.setVenue(slug);
    Array.prototype.forEach.call(modal.querySelectorAll('#modal-ta .order-group[data-venue]'),function(g){g.hidden=g.getAttribute('data-venue')!==slug;});
  }
  function openModal(mode,opts){
    if(!modal)return;
    opts=opts||{};
    setModalMode(mode);
    setModalVenue(opts.venue||document.body.getAttribute('data-venue')||'majorstua');
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
    var offset=(header?header.offsetHeight:64)+120;
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
      var slug=root.getAttribute('data-venue')||'majorstua';
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
        if(!VENUE_NAMES[slug])slug='majorstua';
        root.setAttribute('data-venue',slug);
        if(venueSeg)Array.prototype.forEach.call(venueSeg.querySelectorAll('button'),function(b){var on=b.getAttribute('data-bvenue')===slug;b.classList.toggle('is-on',on);b.setAttribute('aria-pressed',on?'true':'false');});
        if(zcLink&&zenchefUrl(slug))zcLink.setAttribute('href',zenchefUrl(slug));
        var intro=root.querySelector('.bk-online__intro');var thr=root.getAttribute('data-threshold-'+slug);
        if(intro&&thr){intro.setAttribute('data-i18n-n',thr);var txt=t('book.onlineIntro');if(txt)intro.textContent=txt.split('{n}').join(thr);}
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
        var venue=root.getAttribute('data-venue')||'majorstua';
        track('booking:'+venue+':'+(form===large?'group':'online'),{kv_source:src?src.value:'',kv_newsletter:nl?!!nl.checked:false});
        if(form===large){
          var to=root.getAttribute('data-email-'+venue)||'book.major@kverneriet.com';
          var f=function(n){var el=form.querySelector('[name="'+n+'"]');return el?el.value:'';};
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
    api.setVenue(root.getAttribute('data-venue')||document.body.getAttribute('data-venue')||'majorstua');
  }
  Array.prototype.forEach.call(document.querySelectorAll('.bk'),wireBooking);
  document.addEventListener('kv:lang',function(){
    Array.prototype.forEach.call(document.querySelectorAll('.bk .bk-sent:not([hidden]) .badge'),function(b){
      var root=b.closest('.bk');var v=root.getAttribute('data-venue')||'majorstua';
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

  /* Apply the stored language once the DOM is in place */
  applyLang(LANG);
})();
