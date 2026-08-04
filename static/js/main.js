/* =====================================================================
   Arena FC — template behaviour
   Vanilla JavaScript only. Each feature is a guard-claused init.
   ===================================================================== */
(function () {
  'use strict';

  /* ---- Sticky header background on scroll ---- */
  function initHeaderScroll() {
    var header = document.getElementById('site-header');
    if (!header) return;
    var onScroll = function () {
      header.classList.toggle('scrolled', window.scrollY > 40);
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  /* ---- Live match countdown ---- */
  function initCountdown() {
    var box = document.querySelector('.countdown[data-kickoff]');
    if (!box) return;
    var target = new Date(box.getAttribute('data-kickoff')).getTime();
    if (isNaN(target)) return;

    var out = {
      days: box.querySelector('[data-cd="days"]'),
      hours: box.querySelector('[data-cd="hours"]'),
      mins: box.querySelector('[data-cd="mins"]'),
      secs: box.querySelector('[data-cd="secs"]')
    };
    if (!out.days || !out.hours || !out.mins || !out.secs) return;

    var pad = function (n) { return (n < 10 ? '0' : '') + n; };

    function tick() {
      var diff = target - Date.now();
      if (diff <= 0) {
        out.days.textContent = out.hours.textContent = out.mins.textContent = out.secs.textContent = '00';
        box.setAttribute('aria-label', 'Kick off');
        clearInterval(timer);
        return;
      }
      var s = Math.floor(diff / 1000);
      out.days.textContent = pad(Math.floor(s / 86400));
      out.hours.textContent = pad(Math.floor((s % 86400) / 3600));
      out.mins.textContent = pad(Math.floor((s % 3600) / 60));
      out.secs.textContent = pad(s % 60);
    }
    tick();
    var timer = setInterval(tick, 1000);
  }

  /* ---- Squad position filter ---- */
  function initSquadFilter() {
    var group = document.querySelector('.squad-filter');
    var grid = document.querySelector('.player-grid');
    if (!group || !grid) return;

    var chips = Array.prototype.slice.call(group.querySelectorAll('.chip'));
    var players = Array.prototype.slice.call(grid.querySelectorAll('.player'));
    var empty = document.querySelector('.squad-empty');

    group.addEventListener('click', function (e) {
      var chip = e.target.closest('.chip');
      if (!chip) return;
      var filter = chip.getAttribute('data-filter');

      chips.forEach(function (c) {
        var on = c === chip;
        c.classList.toggle('is-active', on);
        c.setAttribute('aria-selected', on ? 'true' : 'false');
      });

      var shown = 0;
      players.forEach(function (p) {
        var match = filter === 'all' || p.getAttribute('data-pos') === filter;
        p.hidden = !match;
        if (match) shown++;
      });
      if (empty) empty.hidden = shown !== 0;
    });
  }

  /* ---- Scroll reveal (IntersectionObserver) ---- */
  function initReveal() {
    var items = document.querySelectorAll('.reveal');
    if (!items.length) return;

    var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduce || !('IntersectionObserver' in window)) {
      items.forEach(function (el) { el.classList.add('is-visible'); });
      return;
    }

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });

    items.forEach(function (el) { io.observe(el); });
  }

  /* ---- Close mobile nav after a link is tapped ---- */
  function initNavClose() {
    var collapse = document.getElementById('primary-nav');
    if (!collapse) return;
    collapse.addEventListener('click', function (e) {
      if (!e.target.closest('a')) return;
      if (!collapse.classList.contains('show')) return;
      if (window.bootstrap && window.bootstrap.Collapse) {
        var inst = window.bootstrap.Collapse.getOrCreateInstance(collapse, { toggle: false });
        inst.hide();
      } else {
        collapse.classList.remove('show');
      }
    });
  }

  function ready(fn) {
    if (document.readyState !== 'loading') { fn(); }
    else { document.addEventListener('DOMContentLoaded', fn); }
  }

  ready(function () {
    initHeaderScroll();
    initCountdown();
    initSquadFilter();
    initReveal();
    initNavClose();
  });
})();
