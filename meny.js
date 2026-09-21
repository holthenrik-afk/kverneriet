/* Kverneriet — menysidene. Menyen er forhåndsrendret i HTML av tools/build_menu.py (samme markup som her),
   så søkemotorer og svarmotorer ser retter, priser og allergener uten JavaScript. Dette scriptet gjør
   bare to ting: (1) tegner menyen på nytt fra window.KV_CONTENT hvis HTML-en av en eller annen grunn er
   tom, og (2) oppdaterer allergen-nøkkelen og PDF-lenken ved språkbytte. Tittelen røres ikke. */
(function(){
  'use strict';
  var C=window.KV_CONTENT;
  if(!C)return;
  var slug=document.body.getAttribute('data-menu-venue');
  if(!slug)return;
  var v=null;
  for(var i=0;i<C.venues.length;i++)if(C.venues[i].slug===slug)v=C.venues[i];
  if(!v)return;

  var el={content:document.getElementById('menu-content'),navList:document.getElementById('menu-sections-list'),allergenKey:document.getElementById('allergen-key')};
  function T(key){return (window.KVT&&window.KVT(key))||'';}
  function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
  function escAttr(s){return esc(s).replace(/"/g,'&quot;');}

  function tagHtml(code,opts){
    opts=opts||{};
    var label=C.allergenKey[code]||code;
    return '<span class="kv-tag'+(opts.maybe?' kv-tag--maybe':'')+'" title="'+escAttr(label)+'">'+(opts.parens?'('+esc(code)+')':esc(code))+'</span>';
  }
  function itemHtml(it){
    var h='<article class="menu-item"><div class="menu-item__row"><h3>'+esc(it.name)+'</h3><span class="menu-item__price">'+esc(it.price)+'</span></div>';
    if(it.description){h+='<p class="menu-item__desc">'+esc(it.description)+(it.emphasis?' <strong>'+esc(it.emphasis)+'</strong>':'')+'</p>';}
    else if(it.emphasis){h+='<p class="menu-item__desc"><strong>'+esc(it.emphasis)+'</strong></p>';}
    if(it.quote){h+='<p class="menu-item__quote">'+esc(it.quote)+'</p>';}
    var tags=(it.allergens||[]).map(function(a){return tagHtml(a);}).concat((it.maybeAllergens||[]).map(function(a){return tagHtml(a,{maybe:true,parens:true});}));
    if(tags.length){h+='<div class="menu-item__tags">'+tags.join('')+'</div>';}
    return h+'</article>';
  }
  function upgradeHtml(u){
    var delta=u.delta||'';
    var h='<div class="upgrade-row"><span class="upgrade-row__glyph" aria-hidden="true">➼</span><span class="upgrade-row__body"><span class="upgrade-row__name">'+esc(u.name)+'</span>';
    if(u.note)h+='<span class="upgrade-row__note">'+esc(u.note)+'</span>';
    h+='</span>';
    var tags=(u.allergens||[]).map(function(a){return tagHtml(a,{maybe:true});});
    if(tags.length)h+='<span class="upgrade-row__tags">'+tags.join('')+'</span>';
    if(delta)h+='<span class="upgrade-row__delta'+(delta==='free'?' upgrade-row__delta--free':'')+'">'+esc(delta)+'</span>';
    return h+'</div>';
  }
  function sectionHtml(s){
    var h='<section class="menu-sec" id="'+escAttr(s.id)+'"><header class="sec-head"><div class="sec-head__rule"></div><h2 class="display-2">'+esc(s.title)+'</h2>';
    if(s.intro)h+='<p class="sec-head__intro">'+esc(s.intro)+'</p>';
    h+='</header><div style="margin-top:var(--space-5)">'+s.items.map(itemHtml).join('')+'</div>';
    if(s.upgrades)h+='<div style="margin-top:var(--space-7)"><div class="divider"><span>'+esc(s.upgradesTitle)+'</span></div><div style="margin-top:var(--space-3)">'+s.upgrades.map(upgradeHtml).join('')+'</div></div>';
    if(s.dips)h+='<div style="margin-top:var(--space-7)"><div class="divider"><span>'+esc(s.dipsTitle)+'</span></div><div style="margin-top:var(--space-3)">'+s.dips.map(upgradeHtml).join('')+'</div></div>';
    if(s.id==='kids'&&v.menu.kidsPdf)h+='<p style="margin-top:var(--space-6);color:var(--text-muted);font-size:var(--type-body-sm)"><a href="'+escAttr(v.menu.kidsPdf)+'" target="_blank" rel="noopener" data-i18n="menu.kidsPdf">'+esc(T('menu.kidsPdf')||'Barnemenyen finnes også som utskriftsvennlig PDF.')+'</a></p>';
    return h+'</section>';
  }

  /* Fallback: bare hvis HTML-en mangler menyen */
  if(el.content&&!el.content.querySelector('.menu-sec')&&v.menu.sections&&v.menu.sections.length){
    el.content.innerHTML=v.menu.sections.map(sectionHtml).join('');
    if(el.navList)el.navList.innerHTML=v.menu.sections.map(function(s){return '<li><a href="#'+escAttr(s.id)+'">'+esc(s.label)+'</a></li>';}).join('');
    if(window.KVSpyRefresh)window.KVSpyRefresh();
  }
})();
