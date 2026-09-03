Qualtrics.SurveyEngine.addOnReady(function() {
  var root = this.getQuestionContainer().querySelector('.smcm-atlas-mid');
  if (!root || root.dataset.inited) return;
  root.dataset.inited = '1';

  var MARKERS = [
    {flag:"inc_mid_habenula",             text:"Habenula",             target:{x:0.4315,y:0.4555}, label:{x:0.4406,y:0.0663}},
    {flag:"inc_mid_thalamus",             text:"Thalamus",             target:{x:0.3617,y:0.5241}, label:{x:0.3640,y:0.8002}},
    {flag:"inc_mid_corpus_callosum",      text:"Corpus Callosum",      target:{x:0.2241,y:0.4620}, label:{x:0.0684,y:0.7118}},
    {flag:"inc_mid_arbor_vitae",          text:"Arbor Vitae",          target:{x:0.8018,y:0.4880}, label:{x:0.9047,y:0.2781}},
    {flag:"inc_mid_cerebral_aqueduct",    text:"Cerebral Aqueduct",    target:{x:0.5658,y:0.5515}, label:{x:0.8384,y:0.2118}},
    {flag:"inc_mid_third_ventricle",      text:"Third Ventricle",      target:{x:0.3232,y:0.4959}, label:{x:0.3087,y:0.9006}},
    {flag:"inc_mid_cingulate_gyrus",      text:"Cingulate Gyrus",      target:{x:0.3267,y:0.3794}, label:{x:0.2990,y:0.0516}},
    {flag:"inc_mid_hypothalamus",         text:"Hypothalamus",         target:{x:0.3779,y:0.6136}, label:{x:0.4275,y:0.8564}},
    {flag:"inc_mid_optic_chiasm",         text:"Optic Chiasm",         target:{x:0.2999,y:0.6699}, label:{x:0.2431,y:0.8379}},
    {flag:"inc_mid_pineal_body",          text:"Pineal Body",          target:{x:0.4851,y:0.4389}, label:{x:0.6077,y:0.1262}},
    {flag:"inc_mid_superior_colliculus",  text:"Superior Colliculus",  target:{x:0.5485,y:0.4375}, label:{x:0.7072,y:0.0543}},
    {flag:"inc_mid_inferior_colliculus",  text:"Inferior Colliculus",  target:{x:0.5625,y:0.5053}, label:{x:0.7811,y:0.1252}},
    {flag:"inc_mid_fornix",               text:"Fornix",               target:{x:0.3674,y:0.4180}, label:{x:0.3619,y:0.1096}},
    {flag:"inc_mid_septum_pellucidum",    text:"Septum Pellucidum",    target:{x:0.2472,y:0.5055}, label:{x:0.1008,y:0.8094}},
    {flag:"inc_mid_posterior_commissure", text:"Posterior Commissure", target:{x:0.4559,y:0.4923}, label:{x:0.5580,y:0.0691}},
    {flag:"inc_mid_anterior_commissure",  text:"Anterior Commissure",  target:{x:0.3005,y:0.5638}, label:{x:0.1340,y:0.8996}},
    {flag:"inc_mid_central_sulcus",       text:"Central Sulcus",       target:{x:0.1443,y:0.2781}, label:{x:0.1291,y:0.0645}},
    {flag:"inc_mid_precentral_gyrus",     text:"Precentral Gyrus",     target:{x:0.1188,y:0.2947}, label:{x:0.0670,y:0.1851}},
    {flag:"inc_mid_postcentral_gyrus",    text:"Postcentral Gyrus",    target:{x:0.1644,y:0.2440}, label:{x:0.2079,y:0.1197}},
    {flag:"inc_mid_mammillary_bodies",    text:"Mammillary Bodies",    target:{x:0.4137,y:0.6786}, label:{x:0.4765,y:0.7578}},
    {flag:"inc_mid_pons",                 text:"Pons",                 target:{x:0.6008,y:0.7192}, label:{x:0.6084,y:0.8214}},
    {flag:"inc_mid_fourth_ventricle",     text:"Fourth Ventricle",     target:{x:0.7472,y:0.6492}, label:{x:0.8294,y:0.8444}},
    {flag:"inc_mid_cerebellum",           text:"Cerebellum",           target:{x:0.9102,y:0.4613}, label:{x:0.9434,y:0.3517}},
    {flag:"inc_mid_tegmentum",            text:"Tegmentum",            target:{x:0.5221,y:0.6133}, label:{x:0.5704,y:0.8831}},
    {flag:"inc_mid_medulla",              text:"Medulla",              target:{x:0.7403,y:0.7413}, label:{x:0.6913,y:0.8453}}
  ];

  var stage    = root.querySelector('#smcmStage');
  var atlasImg = root.querySelector('#smcmAtlasImg');
  var cntShown = root.querySelector('#smcmCntShown');
  var cntTotal = root.querySelector('#smcmCntTotal');
  var srList   = root.querySelector('#smcmSrList');
  var viewFull = root.querySelector('#smcmViewFull');
  if (viewFull && atlasImg) viewFull.href = atlasImg.src;

  function readFlags() {
    var params = new URLSearchParams(window.location.search);
    var excluded = {};
    params.forEach(function(v, k) {
      if (k.indexOf('inc_') === 0 && v === '0') excluded[k] = true;
    });
    return excluded;
  }

  function render() {
    var nodes = stage.querySelectorAll('.marker, .label-pill, svg.leaders');
    for (var i = 0; i < nodes.length; i++) nodes[i].remove();

    var svgNS = 'http://www.w3.org/2000/svg';
    var svg = document.createElementNS(svgNS, 'svg');
    svg.setAttribute('class', 'leaders');
    svg.setAttribute('viewBox', '0 0 100 100');
    svg.setAttribute('preserveAspectRatio', 'none');
    svg.setAttribute('aria-hidden', 'true');
    svg.setAttribute('focusable', 'false');
    stage.appendChild(svg);

    var excluded = readFlags();
    var visible = MARKERS.filter(function(m){ return !excluded[m.flag]; });
    cntShown.textContent = visible.length;
    cntTotal.textContent = MARKERS.length;

    srList.innerHTML = '';
    visible.forEach(function(m){
      var li = document.createElement('li');
      li.textContent = m.text;
      srList.appendChild(li);
    });

    visible.forEach(function(m){
      var line = document.createElementNS(svgNS, 'line');
      line.setAttribute('x1', m.target.x * 100);
      line.setAttribute('y1', m.target.y * 100);
      line.setAttribute('x2', m.label.x * 100);
      line.setAttribute('y2', m.label.y * 100);
      line.setAttribute('stroke', 'rgba(30, 58, 95, 0.7)');
      line.setAttribute('stroke-width', '1.75');
      line.setAttribute('vector-effect', 'non-scaling-stroke');
      svg.appendChild(line);

      var dot = document.createElement('button');
      dot.type = 'button';
      dot.className = 'marker';
      dot.style.left = (m.target.x * 100) + '%';
      dot.style.top  = (m.target.y * 100) + '%';
      dot.setAttribute('aria-label', m.text);
      stage.appendChild(dot);

      var pill = document.createElement('div');
      pill.className = 'label-pill';
      pill.style.left = (m.label.x * 100) + '%';
      pill.style.top  = (m.label.y * 100) + '%';
      pill.textContent = m.text;
      pill.setAttribute('aria-hidden', 'true');
      stage.appendChild(pill);

      function enter(){ dot.classList.add('hovered'); pill.classList.add('hovered'); line.classList.add('hovered'); }
      function leave(){ dot.classList.remove('hovered'); pill.classList.remove('hovered'); line.classList.remove('hovered'); }
      dot.addEventListener('mouseenter', enter);
      dot.addEventListener('mouseleave', leave);
      dot.addEventListener('focus', enter);
      dot.addEventListener('blur', leave);
      dot.addEventListener('touchstart', function(e){ e.preventDefault(); enter(); }, {passive:false});
      dot.addEventListener('touchend', leave);
      pill.addEventListener('mouseenter', enter);
      pill.addEventListener('mouseleave', leave);
    });
  }

  var modeButtons = root.querySelectorAll('.mode-group button');
  for (var i = 0; i < modeButtons.length; i++) {
    (function(btn){
      btn.addEventListener('click', function(){
        for (var j = 0; j < modeButtons.length; j++) {
          modeButtons[j].classList.remove('active');
          modeButtons[j].setAttribute('aria-checked', 'false');
        }
        btn.classList.add('active');
        btn.setAttribute('aria-checked', 'true');
        stage.classList.remove('mode-show', 'mode-hover', 'mode-hide');
        stage.classList.add('mode-' + btn.dataset.mode);
      });
    })(modeButtons[i]);
  }

  function updateIW() {
    var w = atlasImg.clientWidth;
    if (w > 0) stage.style.setProperty('--iw', w + 'px');
  }

  if (atlasImg.complete) { render(); updateIW(); }
  else atlasImg.addEventListener('load', function(){ render(); updateIW(); });
  window.addEventListener('resize', updateIW);

  // On narrow screens, default to "Hover to reveal" mode so the image
  // stays clean and students tap one dot at a time.
  if (window.matchMedia('(max-width: 720px)').matches) {
    var hoverBtn = root.querySelector('.mode-group button[data-mode="hover"]');
    if (hoverBtn) hoverBtn.click();
  }
});
