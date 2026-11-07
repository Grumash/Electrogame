/* ElectroGame Fuengirola: shared behaviour for every page */
(function () {
  var PHONE = '34613725715';
  var EMAIL = 'electrogamefuengirola@gmail.com';
  var DEFAULT_MSG = '¡Hola ElectroGame! Quiero un presupuesto para reparar: ';

  function waUrl(text) { return 'https://wa.me/' + PHONE + '?text=' + encodeURIComponent(text); }

  // WhatsApp links: data-wa (optional data-wa-msg for a page-specific message)
  document.querySelectorAll('[data-wa]').forEach(function (a) {
    a.href = waUrl(a.getAttribute('data-wa-msg') || DEFAULT_MSG);
    a.target = '_blank';
    a.rel = 'noopener';
  });

  // Open / closed status in Fuengirola time (minutes since midnight)
  var HOURS = { 1: [[600, 810], [960, 1170]], 2: [[600, 810], [960, 1170]], 3: [[600, 810], [960, 1170]], 4: [[600, 810], [960, 1170]], 5: [[600, 810], [960, 1170]], 6: [[600, 840]], 0: [] };
  var DAYS = ['domingo', 'lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado'];
  function fmt(m) { var h = Math.floor(m / 60), mm = m % 60; return h + ':' + (mm < 10 ? '0' : '') + mm; }
  try {
    var parts = new Intl.DateTimeFormat('en-GB', { timeZone: 'Europe/Madrid', weekday: 'short', hour: '2-digit', minute: '2-digit', hour12: false }).formatToParts(new Date());
    var get = function (t) { return (parts.find(function (p) { return p.type === t; }) || {}).value; };
    var d = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].indexOf(get('weekday'));
    var now = (parseInt(get('hour'), 10) % 24) * 60 + parseInt(get('minute'), 10);
    document.querySelectorAll('.hours tr[data-d="' + d + '"]').forEach(function (r) { r.classList.add('today'); });
    var open = (HOURS[d] || []).find(function (r) { return now >= r[0] && now < r[1]; });
    var el = document.getElementById('status'), txt = document.getElementById('status-text');
    if (el && txt) {
      if (open) { el.classList.add('open'); txt.textContent = 'Abierto ahora · cierra a las ' + fmt(open[1]); }
      else {
        var next = (HOURS[d] || []).find(function (r) { return now < r[0]; }), label = '';
        if (next) { label = 'hoy a las ' + fmt(next[0]); }
        else {
          for (var i = 1; i <= 7; i++) {
            var nd = (d + i) % 7;
            if (HOURS[nd].length) { label = (i === 1 ? 'mañana' : 'el ' + DAYS[nd]) + ' a las ' + fmt(HOURS[nd][0][0]); break; }
          }
        }
        txt.textContent = 'Cerrado · abre ' + label;
      }
    }
  } catch (e) { /* keep static hours text */ }

  var y = document.getElementById('y');
  if (y) y.textContent = new Date().getFullYear();

  // Header border on scroll
  var nav = document.getElementById('nav');
  if (nav) window.addEventListener('scroll', function () { nav.classList.toggle('scrolled', window.scrollY > 8); }, { passive: true });

  // Mobile menu
  var btn = document.getElementById('menu-btn'), menu = document.getElementById('mobile-menu');
  if (btn && menu) {
    btn.addEventListener('click', function () {
      var isOpen = menu.classList.toggle('open');
      btn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
      btn.querySelector('use').setAttribute('href', isOpen ? '#i-close' : '#i-menu');
    });
    menu.querySelectorAll('a').forEach(function (a) { a.addEventListener('click', function () { menu.classList.remove('open'); btn.setAttribute('aria-expanded', 'false'); }); });
  }

  // Reveal on scroll
  var reveals = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -8% 0px' });
    reveals.forEach(function (el) { io.observe(el); });
  } else { reveals.forEach(function (el) { el.classList.add('in'); }); }

  // Forms: build a message and send it by WhatsApp (submit) or email (data-send="mail")
  document.querySelectorAll('form[data-wa-form]').forEach(function (form) {
    var estimate = form.querySelector('.estimate');

    function updateEstimate() {
      if (!estimate) return;
      var act = form.querySelector('[name="actividad"]'), pl = form.querySelector('[name="jugadores"]');
      var opt = act && act.selectedOptions[0];
      if (!opt || !opt.dataset.p1 || !pl || !pl.value) { estimate.classList.remove('show'); return; }
      var price = pl.value === '1' ? opt.dataset.p1 : pl.value === '2' ? opt.dataset.p2 : null;
      estimate.innerHTML = price
        ? 'Precio orientativo: <b>' + price + '</b> por ' + opt.dataset.unit + '. Se paga en el local.'
        : 'Para 3 o más jugadores te confirmamos el precio por WhatsApp.';
      estimate.classList.add('show');
    }
    form.addEventListener('change', updateEstimate);

    function validate() {
      var ok = true, first = null;
      form.querySelectorAll('[required]').forEach(function (f) {
        var bad = f.type === 'checkbox' ? !f.checked : !String(f.value).trim();
        if (f.type === 'email' && f.value && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(f.value)) bad = true;
        if (f.type === 'checkbox') f.closest('.check').classList.toggle('invalid', bad);
        else f.setAttribute('aria-invalid', bad ? 'true' : 'false');
        if (bad) { ok = false; first = first || f; }
      });
      if (first) first.focus();
      return ok;
    }

    function message() {
      var lines = [form.getAttribute('data-intro') || '¡Hola ElectroGame!'];
      form.querySelectorAll('[data-label]').forEach(function (f) {
        var v = String(f.value).trim();
        if (!v) return;
        if (f.type === 'date') { var p = v.split('-'); v = p[2] + '/' + p[1] + '/' + p[0]; }
        lines.push('• ' + f.getAttribute('data-label') + ': ' + v);
      });
      return lines.join('\n');
    }

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!validate()) return;
      window.open(waUrl(message()), '_blank', 'noopener');
    });

    var mailBtn = form.querySelector('[data-send="mail"]');
    if (mailBtn) mailBtn.addEventListener('click', function () {
      if (!validate()) return;
      var subject = form.getAttribute('data-subject') || 'Consulta desde la web';
      window.location.href = 'mailto:' + EMAIL + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(message());
    });

    form.querySelectorAll('input,select,textarea').forEach(function (f) {
      f.addEventListener('input', function () {
        if (f.type === 'checkbox') f.closest('.check').classList.remove('invalid');
        else if (f.getAttribute('aria-invalid') === 'true' && String(f.value).trim()) f.setAttribute('aria-invalid', 'false');
      });
    });

    // Don't allow picking a past date
    var date = form.querySelector('input[type="date"]');
    if (date) date.min = new Date().toISOString().slice(0, 10);

    // Preselect an activity from the URL, e.g. /reserva-espacio/?actividad=ps5
    var key = new URLSearchParams(window.location.search).get('actividad');
    var act = form.querySelector('[name="actividad"]');
    if (key && act) {
      var match = act.querySelector('option[data-key="' + key.replace(/[^a-z0-9-]/gi, '') + '"]');
      if (match) { act.value = match.value; updateEstimate(); }
    }
  });
})();
