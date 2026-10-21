/* S99 Marketing — site behaviour: menu, work gallery from data/work.json, video lightbox, WhatsApp form. */
(function () {
  'use strict';
  var body = document.body;
  var cfg = document.getElementById('site') || body;
  var AR = cfg.getAttribute('data-lang') === 'ar';
  var ROOT = cfg.getAttribute('data-root') || '';
  var WA = cfg.getAttribute('data-wa') || '';
  var T = {
    missing: cfg.getAttribute('data-t-missing') || 'Video not added yet',
    reel: cfg.getAttribute('data-t-reel') || 'Reel',
    play: cfg.getAttribute('data-t-play') || 'Play',
    featured: cfg.getAttribute('data-t-featured') || 'Featured film',
    watch: cfg.getAttribute('data-t-watch') || 'Watch film'
  };

  /* ---------- Mobile menu ---------- */
  var header = document.querySelector('.site-header');
  var menuBtn = document.querySelector('.menu-btn');
  if (header && menuBtn) {
    menuBtn.addEventListener('click', function () {
      var open = header.classList.toggle('is-open');
      menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    header.querySelectorAll('.nav-links a').forEach(function (a) {
      a.addEventListener('click', function () { header.classList.remove('is-open'); menuBtn.setAttribute('aria-expanded', 'false'); });
    });
  }

  /* ---------- Helpers ---------- */
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function pick(item, key) { return (AR && item[key + '_ar']) ? item[key + '_ar'] : (item[key] || ''); }
  function url(p) { if (!p) return ''; return /^(https?:)?\/\//.test(p) ? p : ROOT + p.replace(/^\//, ''); }
  function ytId(link) {
    if (!link) return '';
    var m = String(link).match(/(?:youtu\.be\/|youtube\.com\/(?:watch\?(?:.*&)?v=|embed\/|shorts\/|live\/))([A-Za-z0-9_-]{11})/);
    return m ? m[1] : '';
  }
  var PLAY_SVG = '<svg width="20" height="20" viewBox="0 0 24 24" fill="#fff" aria-hidden="true"><path d="M7 4.5v15l13-7.5z"/></svg>';
  var PLAY_SVG_DARK = '<svg width="18" height="18" viewBox="0 0 24 24" fill="#000" aria-hidden="true"><path d="M7 4.5v15l13-7.5z"/></svg>';
  var REEL_SVG = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5"/><path d="M10 9l5 3-5 3z"/></svg>';

  /* ---------- Lightbox ---------- */
  var lb = document.getElementById('lightbox');
  var lbFrame = lb && lb.querySelector('.lb-frame');
  var lbTitle = lb && lb.querySelector('.lb-caption b');
  if (lbTitle) lbTitle.setAttribute('dir', 'auto');
  var lbType = lb && lb.querySelector('.lb-caption span');
  var lbLink = lb && lb.querySelector('.lb-yt');
  var lastFocus = null;

  function openVideo(item, vertical) {
    if (!lb) return;
    lastFocus = document.activeElement;
    lbFrame.className = 'lb-frame' + (vertical ? ' is-vertical' : '');
    var id = ytId(item.youtube);
    if (id) {
      lbFrame.innerHTML = '<iframe src="https://www.youtube-nocookie.com/embed/' + id + '?autoplay=1&rel=0&playsinline=1&modestbranding=1" title="' + esc(pick(item, 'client')) + '" allow="autoplay; encrypted-media; picture-in-picture; fullscreen" allowfullscreen></iframe>';
    } else if (item.image && !item.video) {
      lbFrame.className = 'lb-frame is-image';
      lbFrame.innerHTML = '<img src="' + esc(url(item.image)) + '" alt="' + esc(pick(item, 'client')) + '">';
    } else if (item.video) {
      lbFrame.innerHTML = '<video src="' + esc(url(item.video)) + '" poster="' + esc(url(item.poster)) + '" controls autoplay playsinline></video>';
    } else {
      lbFrame.innerHTML = (item.poster ? '<img src="' + esc(url(item.poster)) + '" alt="">' : '') + '<div class="lb-missing">' + esc(T.missing) + '</div>';
    }
    lbTitle.textContent = pick(item, 'client');
    lbType.textContent = pick(item, 'type');
    if (lbLink) {
      if (id) { lbLink.href = 'https://www.youtube.com/watch?v=' + id; lbLink.hidden = false; } else { lbLink.hidden = true; }
    }
    lb.hidden = false;
    body.style.overflow = 'hidden';
    lb.querySelector('.lb-close').focus();
  }
  function closeVideo() {
    if (!lb || lb.hidden) return;
    lb.hidden = true;
    lbFrame.innerHTML = '';
    body.style.overflow = '';
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }
  if (lb) {
    lb.querySelector('.lb-close').addEventListener('click', closeVideo);
    lb.addEventListener('click', function (e) { if (e.target === lb) closeVideo(); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeVideo(); });
  }

  /* ---------- Work (home + service pages), all from data/work.json ---------- */
  var reelsEl = document.getElementById('reels');
  var moreWrap = document.getElementById('reels-more-wrap');
  var moreEl = document.getElementById('reels-more');
  var moreBtn = document.getElementById('reels-more-btn');
  var filmsEl = document.getElementById('films');
  var featuredEl = document.getElementById('featured');
  var infRail = document.getElementById('inf-rail');
  var showreelBtn = document.getElementById('showreel-btn');
  var svcWork = document.getElementById('svc-work');
  var svcFilters = document.getElementById('svc-filters');
  T.allClients = cfg.getAttribute('data-t-all-clients') || 'All clients';
  T.all = cfg.getAttribute('data-t-all') || 'All';

  function cover(item, label) {
    if (item.video && !ytId(item.youtube)) {
      return '<video class="hover-vid" src="' + esc(url(item.video)) + '"' + (item.poster ? ' poster="' + esc(url(item.poster)) + '"' : '') + ' muted loop playsinline preload="none" aria-hidden="true"></video>';
    }
    if (item.poster) return '<img src="' + esc(url(item.poster)) + '" alt="" loading="lazy">';
    var ph = '<span class="ph" aria-hidden="true">' + esc(label) + '</span>';
    var id = ytId(item.youtube);
    if (!id) return ph;
    /* YouTube cover: vertical Shorts thumbnail first, then the standard one; if both fail the name placeholder stays */
    return ph + '<img src="https://i.ytimg.com/vi/' + id + '/oar2.jpg" data-fallback="https://i.ytimg.com/vi/' + id + '/hqdefault.jpg" alt="" loading="lazy" class="yt-cover">';
  }
  function nextCover(img) {
    var fb = img.getAttribute('data-fallback');
    if (fb) { img.removeAttribute('data-fallback'); img.src = fb; } else { img.remove(); }
  }
  /* silent preview of local videos on hover (desktop) */
  document.addEventListener('mouseover', function (e) {
    var btn = e.target.closest && e.target.closest('.media-btn');
    var v = btn && btn.querySelector('video.hover-vid');
    if (v && v.paused) { var p = v.play(); if (p && p.catch) p.catch(function () {}); }
  });
  document.addEventListener('mouseout', function (e) {
    var btn = e.target.closest && e.target.closest('.media-btn');
    if (!btn || (e.relatedTarget && btn.contains(e.relatedTarget))) return;
    var v = btn.querySelector('video.hover-vid');
    if (v) v.pause();
  });
  document.addEventListener('error', function (e) {
    var img = e.target;
    if (img && img.tagName === 'IMG' && img.classList.contains('yt-cover')) nextCover(img);
  }, true);
  document.addEventListener('load', function (e) {
    var img = e.target;
    /* YouTube answers a missing size with a 120x90 grey image */
    if (img && img.tagName === 'IMG' && img.classList.contains('yt-cover') && img.naturalWidth <= 120) nextCover(img);
  }, true);
  function mediaInner(item, opts) {
    var title = opts.title || pick(item, 'client');
    var sub = opts.sub != null ? opts.sub : pick(item, 'type');
    return cover(item, item.client || item.influencer || '') +
      '<span class="shade"></span>' +
      (opts.tag ? '<span class="tag">' + REEL_SVG + esc(opts.tag) + '</span>' : '') +
      '<span class="play">' + PLAY_SVG + '</span>' +
      '<span class="cap"><b><bdi>' + esc(title) + '</bdi></b><span>' + esc(sub) + '</span></span>';
  }
  function mediaButtons(list, cls, opts) {
    return list.map(function (it, i) {
      var o = typeof opts === 'function' ? opts(it) : (opts || {});
      return '<button type="button" class="' + cls + ' media-btn" data-i="' + i + '" aria-label="' + esc(T.play + ': ' + (o.title || pick(it, 'client'))) + '">' + mediaInner(it, o) + '</button>';
    }).join('');
  }
  function bind(container, list, vertical) {
    container.querySelectorAll('button[data-i]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var it = list[+btn.getAttribute('data-i')];
        openVideo(it, typeof vertical === 'function' ? vertical(it) : vertical);
      });
    });
  }
  function infAsVideo(it) { var j = function (a, b) { return b ? a + ' · ' + b : a; }; return { client: it.influencer, client_ar: it.influencer_ar, type: j(it.client, it.country), type_ar: j(it.client_ar || it.client, it.country_ar || it.country), poster: it.poster, youtube: it.youtube, video: it.video, vertical: it.vertical !== false }; }

  /* filter chips: groups items by keyFn, draws with drawFn(list) */
  function filtered(list, keyFn, allLabel, drawFn) {
    var keys = [];
    list.forEach(function (it) { var k = keyFn(it); if (k && keys.indexOf(k) < 0) keys.push(k); });
    if (svcFilters) {
      if (keys.length > 1) {
        svcFilters.innerHTML = ['__all'].concat(keys).map(function (k, i) {
          return '<button type="button" class="filter" data-k="' + esc(k) + '" aria-pressed="' + (i === 0 ? 'true' : 'false') + '"><bdi>' + esc(k === '__all' ? allLabel : k) + '</bdi></button>';
        }).join('');
        svcFilters.querySelectorAll('.filter').forEach(function (btn) {
          btn.addEventListener('click', function () {
            svcFilters.querySelectorAll('.filter').forEach(function (b) { b.setAttribute('aria-pressed', 'false'); });
            btn.setAttribute('aria-pressed', 'true');
            var k = btn.getAttribute('data-k');
            drawFn(k === '__all' ? list : list.filter(function (it) { return keyFn(it) === k; }));
          });
        });
      } else { svcFilters.hidden = true; }
    }
    drawFn(list);
  }

  function render(data) {
    if (showreelBtn && data.showreel) {
      showreelBtn.addEventListener('click', function () { openVideo(data.showreel, false); });
    }
    if (reelsEl && data.reels) {
      var top = data.reels.filter(function (r) { return r.top !== false; });
      var more = data.reels.filter(function (r) { return r.top === false; });
      reelsEl.innerHTML = mediaButtons(top, 'reel', { tag: T.reel });
      bind(reelsEl, top, true);
      if (more.length && moreWrap) {
        moreEl.innerHTML = mediaButtons(more, 'reel', { tag: T.reel });
        bind(moreEl, more, true);
        moreWrap.hidden = false;
        moreBtn.addEventListener('click', function () {
          var open = moreEl.hidden;
          moreEl.hidden = !open;
          moreBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
          moreBtn.textContent = moreBtn.getAttribute(open ? 'data-less' : 'data-more');
        });
      }
    }
    if (filmsEl && data.films && data.films.length) {
      var bts = data.films.filter(function (f) { return f.bts; });
      var rest = data.films.filter(function (f) { return !f.bts; });
      if (bts.length) {
        /* Behind the scenes: vertical clips side by side */
        featuredEl.innerHTML = '<div class="bts-wrap"><div class="bts-intro"><span class="tag-line">BTS</span><h3>' + esc(featuredEl.getAttribute('data-bts-h') || '') + '</h3><p>' + esc(featuredEl.getAttribute('data-bts-p') || '') + '</p></div>' +
          '<div class="bts-row">' + mediaButtons(bts, 'reel', { tag: 'BTS' }) + '</div></div>';
        bind(featuredEl.querySelector('.bts-row'), bts, true);
      } else if (rest.length) {
        var feat = rest.shift();
        featuredEl.innerHTML = '<button type="button" class="featured media-btn" data-i="0" aria-label="' + esc(T.play + ': ' + pick(feat, 'client')) + '">' +
          cover(feat, feat.client) + '<span class="shade"></span>' +
          '<span class="info"><small>' + esc(pick(feat, 'type') || T.featured) + '</small><strong><bdi>' + esc(pick(feat, 'client')) + '</bdi></strong><em><i>' + PLAY_SVG_DARK + '</i>' + esc(T.watch) + '</em></span></button>';
        bind(featuredEl, [feat], false);
      }
      filmsEl.innerHTML = mediaButtons(rest, 'film', {});
      bind(filmsEl, rest, function (it) { return !!it.vertical; });
    }
    if (infRail) {
      /* home rail: in the order set in data/work.json */
      var inf = (data.influencers || []).map(infAsVideo);
      if (!inf.length) { var sec = document.getElementById('influencers'); if (sec) sec.hidden = true; }
      else {
        infRail.innerHTML = mediaButtons(inf, 'reel', {});
        bind(infRail, inf, function (it) { return it.vertical; });
      }
    }
    if (svcWork) {
      var kind = svcWork.getAttribute('data-kind');
      if (kind === 'social') {
        filtered(data.social || [], function (g) { return pick(g, 'client'); }, T.allClients, function (list) {
          svcWork.innerHTML = list.map(function (g) {
            return '<figure class="shot"><img src="' + esc(url(g.image)) + '" alt="' + esc(pick(g, 'client') + ' — ' + pick(g, 'type')) + '" loading="lazy">' +
              '<figcaption><b><bdi>' + esc(pick(g, 'client')) + '</bdi></b><span>' + esc(pick(g, 'type')) + '</span></figcaption></figure>';
          }).join('');
        });
      } else if (kind === 'production') {
        filtered(data.production || [], function (p) { return pick(p, 'client'); }, T.allClients, function (list) {
          svcWork.innerHTML = mediaButtons(list, 'tile', {});
          bind(svcWork, list, function (it) { return !!it.vertical; });
        });
      } else if (kind === 'influencers') {
        var infl = data.influencers || [];
        filtered(infl, function (it) { return pick(it, 'client'); }, T.all, function (list) {
          var vids = list.map(infAsVideo);
          svcWork.innerHTML = mediaButtons(vids, 'reel', {});
          bind(svcWork, vids, function (it) { return it.vertical; });
        });
      }
    }
  }

  if (reelsEl || svcWork || showreelBtn || infRail) {
    fetch(ROOT + 'data/work.json', { cache: 'no-cache' })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(render)
      .catch(function (err) { if (window.console) console.warn('Could not load data/work.json', err); });
  }

  /* ---------- Contact form → WhatsApp ---------- */
  var form = document.getElementById('contact-form');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var f = form.elements;
      var name = f['cf-name'].value.trim();
      var phone = f['cf-phone'].value.trim();
      var err = form.querySelector('.form-error');
      if (!name || !phone) { err.textContent = form.getAttribute('data-required'); return; }
      err.textContent = '';
      var lines = [
        form.getAttribute('data-intro'),
        '',
        form.getAttribute('data-l-name') + ': ' + name,
        form.getAttribute('data-l-company') + ': ' + f['cf-company'].value.trim(),
        form.getAttribute('data-l-phone') + ': ' + phone,
        form.getAttribute('data-l-service') + ': ' + f['cf-service'].value,
        '',
        f['cf-message'].value.trim()
      ];
      var link = 'https://wa.me/' + WA + '?text=' + encodeURIComponent(lines.join('\n'));
      var w = window.open(link, '_blank');
      if (w) { try { w.opener = null; } catch (x) {} } else { window.location.href = link; }
    });
  }
  /* =========================== Home v2 =========================== */
  var RM = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var docEl = document.documentElement;

  /* ---------- Preloader: logo + 0–100% once per session ---------- */
  var pl = document.getElementById('preloader');
  if (pl && docEl.classList.contains('pl-on')) {
    var plNum = pl.querySelector('.pl-num'), plBar = pl.querySelector('.pl-bar i');
    var t0 = performance.now(), DUR = RM ? 200 : 1500;
    (function tick(now) {
      var k = Math.min(1, (now - t0) / DUR);
      var v = Math.round((1 - Math.pow(1 - k, 3)) * 100);
      plNum.textContent = v; plBar.style.width = v + '%';
      if (k < 1) requestAnimationFrame(tick);
      else {
        pl.classList.add('is-done');
        setTimeout(function () { docEl.classList.remove('pl-on'); pl.remove(); }, 520);
      }
    })(t0);
  }

  /* ---------- Hook: two statements while scrolling ---------- */
  var hook = document.querySelector('.hook');
  function progress(el) {
    var r = el.getBoundingClientRect();
    var span = el.offsetHeight - window.innerHeight;
    if (span <= 0) return r.top < window.innerHeight ? 1 : 0;
    return Math.min(1, Math.max(0, -r.top / span));
  }
  if (hook && !RM) {
    var ticking = false;
    var onScroll = function () {
      var p = progress(hook);
      hook.setAttribute('data-stage', p < 0.3 ? '1' : (p < 0.62 ? '2' : '3'));
    };
    window.addEventListener('scroll', function () {
      if (ticking) return; ticking = true;
      requestAnimationFrame(function () { ticking = false; onScroll(); });
    }, { passive: true });
    window.addEventListener('resize', onScroll);
    onScroll();
  }

  /* ---------- Portfolio coverflow ---------- */
  var cf = document.querySelector('.cf');
  if (cf) {
    var cards = [].slice.call(cf.querySelectorAll('.cf-card'));
    var capNum = document.querySelector('.cf-num'), capName = document.querySelector('.cf-cap b bdi'), capType = document.querySelector('.cf-cap small');
    var ctrlI = document.querySelector('.cf-i'), ctrlLine = document.querySelector('.cf-line i');
    var cur = 0, N = cards.length, drag = null, moved = false;
    var pad2 = function (n) { return (n < 10 ? '0' : '') + n; };
    var spacing = function () { var w = cards[0] ? cards[0].offsetWidth : 300; return window.innerWidth < 640 ? w * 0.62 : w * 0.82; };
    function layout(dx) {
      var sp = spacing();
      cards.forEach(function (c, i) {
        var r = i - cur; if (r > N / 2) r -= N; else if (r < -N / 2) r += N;   /* endless loop */
        var d = r + (dx || 0) / sp;
        var a = Math.abs(d);
        var x = d * sp - (c.offsetWidth / 2);
        var rot = Math.max(-1, Math.min(1, d)) * -32;
        var z = -Math.min(a, 4) * 140;
        var s = a < 1 ? 1 - a * 0.12 : 0.88 - Math.min(a - 1, 3) * 0.06;
        c.style.transform = 'translate3d(' + x.toFixed(1) + 'px,-50%,' + z.toFixed(0) + 'px) rotateY(' + rot.toFixed(1) + 'deg) scale(' + s.toFixed(3) + ')';
        c.style.opacity = a > 3.6 ? 0 : (a > 2.5 ? 0.35 : 1 - a * 0.12);
        c.style.filter = a < 0.5 ? 'none' : 'brightness(' + Math.max(0.35, 1 - a * 0.25).toFixed(2) + ')';
        c.style.zIndex = 100 - Math.round(a * 10);
        c.style.visibility = a > 4 ? 'hidden' : 'visible';
        c.classList.toggle('is-center', i === cur && !dx);
        c.tabIndex = i === cur ? 0 : -1;
      });
    }
    function go(i) {
      cur = (i + N) % N;
      var c = cards[cur];
      if (capNum) capNum.textContent = pad2(cur + 1);
      if (capName) capName.textContent = c.getAttribute('data-name');
      if (capType) capType.textContent = c.getAttribute('data-type');
      if (ctrlI) ctrlI.textContent = pad2(cur + 1);
      if (ctrlLine) ctrlLine.style.width = ((cur + 1) / N * 100) + '%';
      layout(0);
      livePlay();
    }
    /* the centre card plays its video silently; the others show their cover */
    var cfVisible = false;
    function livePlay() {
      cards.forEach(function (c, i) {
        var v = c.querySelector('video.cf-live');
        if (i === cur && cfVisible && c.getAttribute('data-video')) {
          if (!v) {
            v = document.createElement('video');
            v.className = 'cf-live'; v.muted = true; v.loop = true; v.playsInline = true; v.setAttribute('playsinline', ''); v.preload = 'auto';
            v.setAttribute('aria-hidden', 'true');
            v.src = url(c.getAttribute('data-video'));
            v.addEventListener('playing', function () { v.classList.add('is-on'); });
            c.insertBefore(v, c.firstChild.nextSibling);
          }
          var pr = v.play(); if (pr && pr.catch) pr.catch(function () {});
        } else if (v) { v.pause(); v.classList.remove('is-on'); }
      });
    }
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (en) { cfVisible = en[0].isIntersecting; livePlay(); }, { threshold: 0.35 }).observe(cf);
    }
    function openCard(c) {
      var item = { client: c.getAttribute('data-name'), type: c.getAttribute('data-type'), youtube: c.getAttribute('data-youtube') || '', video: c.getAttribute('data-video') || '', poster: c.getAttribute('data-img') || '' };
      if (!item.youtube && !item.video) item.image = item.poster;
      openVideo(item, !!c.getAttribute('data-vertical'));
    }
    cards.forEach(function (c, i) {
      c.addEventListener('click', function (e) {
        if (moved) { e.preventDefault(); return; }
        if (i === cur) openCard(c); else go(i);
      });
    });
    var prevB = document.querySelector('.cf-prev'), nextB = document.querySelector('.cf-next');
    if (prevB) prevB.addEventListener('click', function () { go(cur - 1); });
    if (nextB) nextB.addEventListener('click', function () { go(cur + 1); });
    cf.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight') { e.preventDefault(); go(cur + 1); }
      else if (e.key === 'ArrowLeft') { e.preventDefault(); go(cur - 1); }
    });
    cf.addEventListener('pointerdown', function (e) {
      if (e.button !== 0) return;
      drag = { x: e.clientX, y: e.clientY, id: e.pointerId, on: false }; moved = false;
    });
    window.addEventListener('pointermove', function (e) {
      if (!drag || e.pointerId !== drag.id) return;
      var dx = e.clientX - drag.x;
      if (!drag.on) {
        if (Math.abs(dx) < 8) return;
        if (Math.abs(e.clientY - drag.y) > Math.abs(dx)) { drag = null; return; }
        drag.on = true; moved = true; cf.classList.add('is-drag');
      }
      layout(dx);
    });
    var endDrag = function (e) {
      if (!drag || e.pointerId !== drag.id) return;
      var dx = e.clientX - drag.x, was = drag.on;
      drag = null; cf.classList.remove('is-drag');
      if (was) {
        var steps = Math.round(-dx / spacing());
        if (!steps && Math.abs(dx) > 40) steps = dx < 0 ? 1 : -1;
        go(cur + steps);
        setTimeout(function () { moved = false; }, 0);
      }
    };
    window.addEventListener('pointerup', endDrag);
    window.addEventListener('pointercancel', endDrag);
    window.addEventListener('resize', function () { layout(0); });
    go(0);
  }

  /* ---------- Reveal on scroll + count-up ---------- */
  function countUp(el) {
    var end = +el.getAttribute('data-count'), suf = el.getAttribute('data-suffix') || '';
    if (RM) { el.textContent = end + suf; return; }
    var t0 = performance.now(), D = 1600;
    (function step(now) {
      var k = Math.min(1, (now - t0) / D), e2 = 1 - Math.pow(1 - k, 4);
      el.textContent = Math.round(end * e2) + (k === 1 ? suf : '');
      if (k < 1) requestAnimationFrame(step);
    })(t0);
  }
  var revealEls = document.querySelectorAll('.reveal');
  var counters = document.querySelectorAll('[data-count]');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        en.target.classList.add('in');
        var c = en.target.matches('[data-count]') ? en.target : en.target.querySelector('[data-count]');
        if (c && !c.__done) { c.__done = true; countUp(c); }
        io.unobserve(en.target);
      });
    }, { threshold: 0.2, rootMargin: '0px 0px -40px 0px' });
    revealEls.forEach(function (el) { io.observe(el); });
    counters.forEach(function (c) { if (!c.closest('.reveal')) io.observe(c); else c.textContent = '0'; });
  } else {
    revealEls.forEach(function (el) { el.classList.add('in'); });
  }

  /* ---------- S99 System tabs ---------- */
  var sysTabs = [].slice.call(document.querySelectorAll('.sys-tab'));
  if (sysTabs.length) {
    var sysPanels = sysTabs.map(function (t) { return document.getElementById(t.getAttribute('aria-controls')); });
    var sysSel = function (i, focus) {
      sysTabs.forEach(function (t, j) {
        var on = j === i;
        t.setAttribute('aria-selected', on ? 'true' : 'false');
        t.tabIndex = on ? 0 : -1;
        sysPanels[j].hidden = !on;
      });
      if (focus) sysTabs[i].focus();
      sysTabs[i].scrollIntoView && sysTabs[i].parentNode.scrollWidth > sysTabs[i].parentNode.clientWidth &&
        sysTabs[i].parentNode.scrollTo({ left: sysTabs[i].offsetLeft - 24, behavior: RM ? 'auto' : 'smooth' });
    };
    sysTabs.forEach(function (t, i) {
      t.addEventListener('click', function () { sysSel(i); });
      t.addEventListener('keydown', function (e) {
        var fwd = AR ? 'ArrowLeft' : 'ArrowRight', back = AR ? 'ArrowRight' : 'ArrowLeft';
        if (e.key === fwd) { e.preventDefault(); sysSel((i + 1) % sysTabs.length, true); }
        else if (e.key === back) { e.preventDefault(); sysSel((i - 1 + sysTabs.length) % sysTabs.length, true); }
      });
    });
    sysSel(0);
  }

  /* ---------- Myth / fact flip ---------- */
  document.querySelectorAll('.myth').forEach(function (m) {
    m.addEventListener('click', function () { m.setAttribute('aria-pressed', m.getAttribute('aria-pressed') === 'true' ? 'false' : 'true'); });
  });

  /* ---------- Before / after slider ---------- */
  document.querySelectorAll('.ba').forEach(function (ba) {
    var r = ba.querySelector('.ba-range');
    var set = function () { ba.style.setProperty('--x', r.value + '%'); };
    r.addEventListener('input', set); set();
  });
})();
