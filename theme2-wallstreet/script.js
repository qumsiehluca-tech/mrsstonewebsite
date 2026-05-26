/* ============================================
   STONE COLD LOANS — shared interaction script
   Nav · multi-step application form · scroll reveals
   ============================================ */
(function(){
  'use strict';

  /* ---- Sticky nav state ---- */
  var nav = document.getElementById('nav');
  function onScroll(){
    if(nav) nav.classList.toggle('scrolled', window.scrollY > 24);
  }
  window.addEventListener('scroll', onScroll, {passive:true});
  onScroll();

  /* ---- Mobile menu ---- */
  var toggle = document.getElementById('navToggle');
  var mobile = document.getElementById('navMobile');
  if(toggle && mobile){
    toggle.addEventListener('click', function(){
      mobile.classList.toggle('open');
      toggle.classList.toggle('active');
    });
    mobile.querySelectorAll('a').forEach(function(a){
      a.addEventListener('click', function(){
        mobile.classList.remove('open');
        toggle.classList.remove('active');
      });
    });
  }

  /* ---- Scroll reveal ---- */
  var reveals = document.querySelectorAll('.reveal');
  if('IntersectionObserver' in window){
    var io = new IntersectionObserver(function(entries){
      entries.forEach(function(e){
        if(e.isIntersecting){ e.target.classList.add('in'); io.unobserve(e.target); }
      });
    }, {threshold:.15});
    reveals.forEach(function(el){ io.observe(el); });
  } else {
    reveals.forEach(function(el){ el.classList.add('in'); });
  }

  /* ---- Multi-step application form ---- */
  var form = document.getElementById('applyForm');
  if(!form) return;

  var steps = form.querySelectorAll('.form-step');
  var progress = form.querySelectorAll('.progress-step');
  var current = 1;
  var TOTAL = 4;

  function showStep(n){
    steps.forEach(function(s){
      s.classList.toggle('active', s.dataset.step === String(n));
    });
    progress.forEach(function(p){
      p.classList.toggle('active', Number(p.dataset.step) <= n);
    });
    current = n;
    form.scrollIntoView({behavior:'smooth', block:'center'});
  }

  /* Validate the fields inside the currently visible step */
  function validateStep(n){
    var step = form.querySelector('.form-step[data-step="'+n+'"]');
    var fields = step.querySelectorAll('input[required], select[required], textarea[required]');
    var ok = true;
    fields.forEach(function(f){
      var valid = f.type === 'checkbox' ? f.checked : String(f.value).trim() !== '';
      if(f.type === 'email' && valid){
        valid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(f.value);
      }
      f.classList.toggle('err', !valid);
      if(!valid) ok = false;
    });
    return ok;
  }

  /* Clear error state as the user corrects a field */
  form.addEventListener('input', function(e){
    if(e.target.classList.contains('err')) e.target.classList.remove('err');
  });

  form.querySelectorAll('[data-next]').forEach(function(btn){
    btn.addEventListener('click', function(){
      if(validateStep(current) && current < TOTAL) showStep(current + 1);
    });
  });
  form.querySelectorAll('[data-prev]').forEach(function(btn){
    btn.addEventListener('click', function(){
      if(current > 1) showStep(current - 1);
    });
  });

  form.addEventListener('submit', function(e){
    e.preventDefault();
    if(!validateStep(current)) return;
    /* Demo only — no backend. Swap this for a real POST/endpoint later. */
    steps.forEach(function(s){ s.classList.remove('active'); });
    var success = form.querySelector('.form-step[data-step="success"]');
    if(success) success.classList.add('active');
    progress.forEach(function(p){ p.classList.add('active'); });
    form.scrollIntoView({behavior:'smooth', block:'center'});
  });

})();
