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
    document.querySelectorAll('video.cf-live, video.hover-vid').forEach(function(v) { v.pause(); });
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
    document.dispatchEvent(new Event('s99-resume-media'));
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
        autoRail(infRail);
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
      var phone = window.s99Phone(form, 'cf');
      var err = form.querySelector('.form-error');
      if (!name) { err.textContent = form.getAttribute('data-required'); f['cf-name'].focus(); return; }
      if (!phone) { err.textContent = window.s99PhoneError; f['cf-phone'].focus(); return; }
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

  /* ---------- Preloader: a technology sphere that assembles itself, once per session ---------- */
  (function () { /* own scope: the names below must not clash with the rest of the file */
  var pl = document.getElementById('preloader');
  if (pl && docEl.classList.contains('pl-on')) {
    var plBar = pl.querySelector('.pl-bar i'), cv = pl.querySelector('.pl-sphere');
    var ctx = cv && cv.getContext && cv.getContext('2d');
    if (ctx) ctx.setTransform(2, 0, 0, 2, 0, 0);
    var t0 = performance.now(), DUR = RM ? 300 : 3000;
    var W = 600, C = W / 2, R = 205, pts = [], N = 650, GA = Math.PI * (3 - Math.sqrt(5));
    for (var i = 0; i < N; i++) {                      /* even points on a sphere (fibonacci) */
      var y = 1 - (i / (N - 1)) * 2, r = Math.sqrt(1 - y * y), th = GA * i;
      var sx = Math.random() * 2 - 1, sy = Math.random() * 2 - 1, sz = Math.random() * 2 - 1;
      pts.push({ x: Math.cos(th) * r, y: y, z: Math.sin(th) * r, sx: sx * 2.6, sy: sy * 2.6, sz: sz * 2.6, d: Math.random() * 0.35 });
    }
    var stars = [];
    for (var si = 0; si < 42; si++) {
      var sa = si * GA, sr = R * (1.19 + .22 * ((si * 17 % 41) / 41));
      stars.push({ x: C + Math.cos(sa) * sr, y: C + Math.sin(sa) * sr, size: si % 9 === 0 ? 1.6 : .7, phase: si * .73 });
    }
    function ease(k) { return 1 - Math.pow(1 - k, 3); }
    function draw(now, k) {
      if (!ctx) return;
      var t = (now - t0) / 1000, rotY = t * 0.9, rotX = 0.42 + Math.sin(t * 0.6) * 0.08;
      var cy = Math.cos(rotY), sy_ = Math.sin(rotY), cx = Math.cos(rotX), sx_ = Math.sin(rotX);
      ctx.clearRect(0, 0, W, W);
      /* halo */
      var g = ctx.createRadialGradient(C, C, R * 0.2, C, C, R * 1.55);
      g.addColorStop(0, 'rgba(31,90,138,' + (0.08 + 0.12 * k) + ')'); g.addColorStop(0.55, 'rgba(74,125,166,' + (0.03 + 0.05 * k) + ')'); g.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.fillStyle = g; ctx.fillRect(0, 0, W, W);
      /* S99's blue and silver: a calm star field around a luminous lunar core. */
      stars.forEach(function(star) {
        var light = RM ? .7 : .55 + .2 * Math.sin(t * 1.1 + star.phase);
        ctx.strokeStyle = ctx.fillStyle = 'rgba(205,229,246,' + light + ')';
        ctx.beginPath(); ctx.arc(star.x, star.y, star.size, 0, Math.PI * 2); ctx.fill();
        if (star.size > 1) {
          ctx.lineWidth = .6; ctx.beginPath(); ctx.moveTo(star.x - 4, star.y); ctx.lineTo(star.x + 4, star.y);
          ctx.moveTo(star.x, star.y - 4); ctx.lineTo(star.x, star.y + 4); ctx.stroke();
        }
      });
      var coreR = R * (0.62 + 0.22 * ease(k));
      ctx.save();
      ctx.beginPath(); ctx.arc(C, C, coreR, 0, Math.PI * 2); ctx.clip();
      var metal = ctx.createRadialGradient(C - coreR * .38, C - coreR * .45, 0, C, C, coreR * 1.15);
      metal.addColorStop(0, '#afc7d9'); metal.addColorStop(.18, '#426d8e');
      metal.addColorStop(.4, '#102b40'); metal.addColorStop(.72, '#030b14'); metal.addColorStop(.9, '#123f65'); metal.addColorStop(1, '#8baec7');
      ctx.globalAlpha = Math.min(1, k * 3); ctx.fillStyle = metal; ctx.fillRect(0, 0, W, W);
      /* Subtle lunar relief, generated once per position rather than a heavy texture. */
      for (var crater = 0; crater < 22; crater++) {
        var ca = crater * GA, cr = coreR * Math.sqrt((crater + .5) / 24);
        var crx = C + Math.cos(ca) * cr, cry = C + Math.sin(ca) * cr, size = 5 + crater % 5 * 2;
        var relief = ctx.createRadialGradient(crx - 2, cry - 2, 1, crx, cry, size);
        relief.addColorStop(0, 'rgba(4,16,26,.16)'); relief.addColorStop(.7, 'rgba(4,16,26,.08)'); relief.addColorStop(1, 'rgba(215,235,249,.05)');
        ctx.fillStyle = relief; ctx.beginPath(); ctx.arc(crx, cry, size, 0, Math.PI * 2); ctx.fill();
      }
      for (var band = 0; band < 3; band++) {
        ctx.save(); ctx.translate(C, C); ctx.rotate(-.55 + Math.sin(t * .65 + band) * .24);
        var shine = ctx.createLinearGradient(0, -coreR, 0, coreR);
        shine.addColorStop(0, 'rgba(159,203,234,0)'); shine.addColorStop(.35, 'rgba(159,203,234,.04)');
        shine.addColorStop(.48, 'rgba(42,103,150,.3)'); shine.addColorStop(.52, 'rgba(180,207,226,.28)'); shine.addColorStop(.64, 'rgba(18,63,101,0)');
        ctx.strokeStyle = shine; ctx.lineWidth = 7 + band * 4;
        ctx.beginPath(); ctx.ellipse(Math.sin(t * .7 + band) * 24, 0, coreR * (1.1 - band * .1), coreR * (.32 + band * .09), band * .42, 0, Math.PI * 2); ctx.stroke(); ctx.restore();
      }
      ctx.restore();
      ctx.save(); ctx.strokeStyle = 'rgba(220,238,250,' + .65 * k + ')'; ctx.lineWidth = 2;
      ctx.shadowColor = '#9fcbea'; ctx.shadowBlur = 15;
      ctx.beginPath(); ctx.arc(C, C, coreR, Math.PI * 1.02, Math.PI * 1.73); ctx.stroke(); ctx.restore();
      /* orbit rings (glass bands) */
      for (var o = 0; o < 3; o++) {
        var tilt = [0.35, -0.55, 1.15][o], spin = t * [0.7, -0.5, 0.35][o];
        ctx.save(); ctx.translate(C, C); ctx.rotate(tilt + spin * 0.15);
        var rg = ctx.createLinearGradient(-R * 1.3, 0, R * 1.3, 0);
        rg.addColorStop(0, 'rgba(159,203,234,0)'); rg.addColorStop(0.35, 'rgba(159,203,234,' + 0.45 * k + ')');
        rg.addColorStop(0.65, 'rgba(42,103,150,' + 0.55 * k + ')'); rg.addColorStop(1, 'rgba(42,103,150,0)');
        ctx.strokeStyle = rg; ctx.lineWidth = 2.2 - o * 0.5;
        ctx.beginPath(); ctx.ellipse(0, 0, R * (1.22 + o * 0.08), R * (0.32 + 0.1 * Math.sin(spin)), 0, 0, Math.PI * 2); ctx.stroke();
        ctx.restore();
      }
      /* wireframe: latitudes and longitudes, drawn as the sphere settles */
      function proj(X, Y, Z) { var x1 = X * cy - Z * sy_, z1 = X * sy_ + Z * cy, y1 = Y * cx - z1 * sx_, z2 = Y * sx_ + z1 * cx, pr = 2.8 / (2.8 + z2); return [C + x1 * R * pr, C + y1 * R * pr, z2]; }
      ctx.lineWidth = 1;
      for (var la = -2; la <= 2; la++) {
        var yy = la / 3, rr = Math.sqrt(1 - yy * yy); ctx.beginPath();
        for (var a4 = 0; a4 <= 64; a4++) { var an = a4 / 64 * Math.PI * 2, P = proj(Math.cos(an) * rr, yy, Math.sin(an) * rr); a4 ? ctx.lineTo(P[0], P[1]) : ctx.moveTo(P[0], P[1]); }
        ctx.strokeStyle = 'rgba(74,155,212,' + (0.22 * k) + ')'; ctx.stroke();
      }
      for (var lo = 0; lo < 6; lo++) {
        var ph = lo / 6 * Math.PI; ctx.beginPath();
        for (var a5 = 0; a5 <= 64; a5++) { var an2 = a5 / 64 * Math.PI * 2, P2 = proj(Math.cos(an2) * Math.cos(ph), Math.sin(an2), Math.cos(an2) * Math.sin(ph)); a5 ? ctx.lineTo(P2[0], P2[1]) : ctx.moveTo(P2[0], P2[1]); }
        ctx.strokeStyle = 'rgba(159,203,234,' + (0.16 * k) + ')'; ctx.stroke();
      }
      /* points: fly in from a cloud, settle on the sphere */
      var list = [];
      for (var j = 0; j < N; j++) {
        var p = pts[j], kk = Math.max(0, Math.min(1, (k - p.d) / (1 - p.d))), e = ease(kk);
        var X = p.sx + (p.x - p.sx) * e, Y = p.sy + (p.y - p.sy) * e, Z = p.sz + (p.z - p.sz) * e;
        var x1 = X * cy - Z * sy_, z1 = X * sy_ + Z * cy, y1 = Y * cx - z1 * sx_, z2 = Y * sx_ + z1 * cx;
        var per = 2.8 / Math.max(1.2, 2.8 + z2);
        list.push([C + x1 * R * per, C + y1 * R * per, z2, per, e]);
      }
      list.sort(function (a2, b2) { return b2[2] - a2[2]; });
      for (var q = 0; q < list.length; q++) {
        var L = list[q], front = Math.max(0, Math.min(1, (1 - L[2]) / 2)), a3 = (0.35 + 0.65 * front) * (0.6 + 0.4 * L[4]);
        ctx.fillStyle = front > 0.82 ? 'rgba(220,238,255,' + a3 + ')' : 'rgba(' + Math.round(74 + 60 * front) + ',' + Math.round(155 + 50 * front) + ',212,' + a3 + ')';
        ctx.beginPath(); ctx.arc(L[0], L[1], (0.9 + 1.7 * front) * L[3], 0, Math.PI * 2); ctx.fill();
      }
      /* glass highlight */
      var hl = ctx.createRadialGradient(C - R * 0.35, C - R * 0.4, 2, C - R * 0.35, C - R * 0.4, R * 0.9);
      hl.addColorStop(0, 'rgba(255,255,255,' + 0.16 * k + ')'); hl.addColorStop(1, 'rgba(255,255,255,0)');
      ctx.fillStyle = hl; ctx.beginPath(); ctx.arc(C, C, R, 0, Math.PI * 2); ctx.fill();
    }
    (function tick(now) {
      var k = Math.min(1, (now - t0) / DUR);
      if (plBar) plBar.style.width = Math.round(ease(k) * 100) + '%';
      draw(now, ease(k));
      if (k < 1 || now - t0 < DUR + 350) requestAnimationFrame(tick);
      else {
        pl.classList.add('is-done');
        setTimeout(function () { docEl.classList.remove('pl-on'); pl.remove(); }, 620);
      }
    })(t0);
  }
  })();

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
      var cardWidth = cards[0] ? cards[0].offsetWidth : 300;
      var sp = cardWidth * (window.innerWidth < 640 ? 0.62 : 0.82);
      cards.forEach(function (c, i) {
        var r = i - cur; if (r > N / 2) r -= N; else if (r < -N / 2) r += N;   /* endless loop */
        var d = r + (dx || 0) / sp;
        var a = Math.abs(d);
        var x = d * sp - (cardWidth / 2);
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
        if (i === cur && cfVisible && !document.hidden && (!lb || lb.hidden) && c.getAttribute('data-video')) {
          if (!v) {
            v = document.createElement('video');
            v.className = 'cf-live'; v.muted = true; v.loop = true; v.playsInline = true; v.setAttribute('playsinline', ''); v.preload = 'auto';
            v.setAttribute('aria-hidden', 'true');
            v.src = url(c.getAttribute('data-video'));
            v.addEventListener('playing', function () { v.classList.add('is-on'); });
            c.insertBefore(v, c.firstChild.nextSibling);
          }
          var pr = v.play(); if (pr && pr.catch) pr.catch(function () {});
        } else if (v) { v.pause(); v.removeAttribute('src'); v.load(); v.remove(); }
      });
    }
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (en) { cfVisible = en[0].isIntersecting; livePlay(); }, { threshold: 0.35 }).observe(cf);
    }
    document.addEventListener('visibilitychange', livePlay);
    document.addEventListener('s99-resume-media', livePlay);
    /* moves on by itself; pauses while the visitor hovers, drags or watches a video */
    var hold = false, manualPause = RM, drift = 0, lastFrame = 0, resumeAt = 0;
    var pauseB = document.createElement('button');
    pauseB.type = 'button'; pauseB.className = 'auto-toggle';
    function pauseLabel() { pauseB.textContent = manualPause ? (AR ? 'تشغيل الحركة' : 'Play motion') : (AR ? 'إيقاف الحركة' : 'Pause motion'); pauseB.setAttribute('aria-pressed', String(manualPause)); }
    pauseLabel(); document.querySelector('.cf-ctrl').appendChild(pauseB);
    pauseB.addEventListener('click', function () { manualPause = !manualPause; pauseLabel(); });
    cf.addEventListener('mouseenter', function () { hold = true; });
    cf.addEventListener('mouseleave', function () { hold = false; });
    cf.addEventListener('focusin', function () { hold = true; });
    cf.addEventListener('focusout', function (e) { hold = cf.contains(e.relatedTarget); });
    cf.addEventListener('wheel', function () { resumeAt = performance.now() + 6000; }, { passive: true });
    (function advance(now) {
      var dt = Math.min(50, now - (lastFrame || now)); lastFrame = now;
      var active = !manualPause && !hold && !drag && cfVisible && !document.hidden && now > resumeAt && !(lb && !lb.hidden);
      cf.classList.toggle('is-auto', active || drift > 0);
      if (active && N > 1) { drift += dt / 5000; if (drift >= 1) { drift -= 1; go(cur + 1); } layout(-drift * spacing()); }
      requestAnimationFrame(advance);
    })(performance.now());
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
      drift = 0; resumeAt = performance.now() + 6000; layout(0);
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

  function autoRail(rail) {
    var paused = window.matchMedia('(prefers-reduced-motion: reduce)').matches, hover = false, touching = false, focused = false, until = 0, visible = false, direction = 1, last = 0;
    var control = document.createElement('button'); control.type = 'button'; control.className = 'auto-toggle rail-toggle';
    function label() { control.textContent = paused ? (AR ? 'تشغيل حركة المؤثرين' : 'Play influencer motion') : (AR ? 'إيقاف حركة المؤثرين' : 'Pause influencer motion'); control.setAttribute('aria-pressed', String(paused)); }
    label(); rail.before(control); rail.classList.add('auto-rail');
    control.addEventListener('click', function() { paused = !paused; label(); });
    rail.addEventListener('mouseenter', function() { hover = true; });
    rail.addEventListener('mouseleave', function() { hover = false; });
    rail.addEventListener('focusin', function() { focused = true; });
    rail.addEventListener('focusout', function(e) { focused = rail.contains(e.relatedTarget); });
    rail.addEventListener('pointerdown', function() { touching = true; });
    window.addEventListener('pointerup', function() { if(touching) until = performance.now() + 5000; touching = false; });
    window.addEventListener('pointercancel', function() { touching = false; until = performance.now() + 5000; });
    rail.addEventListener('wheel', function() { until = performance.now() + 5000; }, {passive:true});
    if ('IntersectionObserver' in window) new IntersectionObserver(function(e) { visible = e[0].isIntersecting; }).observe(rail); else visible = true;
    (function scroll(now) {
      var dt = Math.min(50, now - (last || now)); last = now;
      if (!paused && !hover && !touching && !focused && visible && !document.hidden && now > until && !(lb && !lb.hidden)) {
        var max = rail.scrollWidth - rail.clientWidth, pos = Math.abs(rail.scrollLeft);
        if (pos >= max - 1) direction = -1; else if (pos <= 1) direction = 1;
        rail.scrollLeft += (AR ? -1 : 1) * direction * dt * .035;
      }
      requestAnimationFrame(scroll);
    })(performance.now());
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
