(function () {
  var d = document, up = d.body.dataset.up || '', slug = d.body.dataset.slug || '';
  function get(k) { try { return JSON.parse(localStorage.getItem(k)) || []; } catch (e) { return []; } }
  function put(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }
  var favs = get('ppg_favs'), recent = get('ppg_recent'), by = {}, w = {};
  if (slug) { recent = [slug].concat(recent.filter(function (x) { return x !== slug; })).slice(0, 12); put('ppg_recent', recent); }
  GAMES.forEach(function (g) { by[g.slug] = g; });
  function link(g) { return '<li><a href="' + up + 'games/' + g.slug + '/">' + g.title.replace(/&/g, '&amp;').replace(/</g, '&lt;') + '</a></li>'; }
  function box(id, title, list) { var el = d.getElementById(id); if (el && list.length) el.innerHTML = '<h2>' + title + '</h2><ul>' + list.map(link).join('') + '</ul>'; }
  favs.concat(recent.slice(0, 5)).forEach(function (s) { (by[s] ? by[s].tags : []).forEach(function (t) { w[t] = (w[t] || 0) + 1; }); });
  var rec = GAMES.filter(function (g) { return g.slug !== slug && favs.indexOf(g.slug) < 0 && recent.slice(0, 3).indexOf(g.slug) < 0; })
    .map(function (g) { return { g: g, s: g.tags.reduce(function (a, t) { return a + (w[t] || 0); }, 0) + (g.pick ? 0.5 : 0) }; })
    .sort(function (a, b) { return b.s - a.s; }).slice(0, 5).map(function (x) { return x.g; });
  box('recs', 'You might like', rec);
  box('recent', 'Played lately', recent.map(function (s) { return by[s]; }).filter(Boolean).slice(0, 5));
  var sv = d.getElementById('savedlist');
  if (sv) sv.innerHTML = favs.length ? '<ul>' + favs.map(function (s) { return by[s] ? link(by[s]) : ''; }).join('') + '</ul>' : '<p class="note">Nothing saved yet. Press "save" next to a game.</p>';
  function paint() { d.querySelectorAll('[data-fav]').forEach(function (b) { b.textContent = favs.indexOf(b.dataset.fav) < 0 ? 'save' : 'unsave'; }); }
  d.addEventListener('click', function (e) {
    var b = e.target.closest('[data-fav]'); if (!b) return; var s = b.dataset.fav;
    favs = favs.indexOf(s) < 0 ? favs.concat(s) : favs.filter(function (x) { return x !== s; }); put('ppg_favs', favs); paint();
  });
  paint();
  var q = d.getElementById('q');
  if (q) q.oninput = function () { var v = q.value.toLowerCase(); d.querySelectorAll('tr[data-s]').forEach(function (r) { r.hidden = r.dataset.s.indexOf(v) < 0; }); };
})();
