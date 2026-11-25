(() => {
  const yearPicker = document.createElement('section');
  yearPicker.className = 'rankings';
  yearPicker.setAttribute('aria-labelledby', 'rank-title');
  yearPicker.innerHTML = `<div class="rank-head"><div><div class="eyebrow">The annual fan poll</div><h2 id="rank-title">DJ MAG TOP 100</h2><p>Browse the full yearly rankings, with artist portraits. Choose a recent year or open the archive for earlier polls.</p></div></div><nav class="year-picker" aria-label="Choose Top 100 DJs year"><button class="year-btn recent active" data-year="2026">2026</button><button class="year-btn recent" data-year="2025">2025</button><button class="year-btn recent" data-year="2024">2024</button><details class="older-years"><summary>EARLIER YEARS</summary><select aria-label="Choose an earlier ranking year"><option value="">Select a year…</option></select></details></nav><div class="rank-toolbar"><span class="rank-count">Loading ranking…</span><a class="rank-source" href="https://djmag.com/top100djs" target="_blank" rel="noopener">DJ MAG SOURCE ↗</a></div><div class="dj-grid" aria-live="polite"></div><p class="rank-note">Rankings and portraits are from <a href="https://djmag.com/top100djs" target="_blank" rel="noopener">DJ Mag’s Top 100 DJs archive</a>.</p>`;
  document.querySelector('.hero').insertAdjacentElement('afterend', yearPicker);
  const grid = yearPicker.querySelector('.dj-grid');
  const count = yearPicker.querySelector('.rank-count');
  const source = yearPicker.querySelector('.rank-source');
  const select = yearPicker.querySelector('select');
  const yearButtons = [...yearPicker.querySelectorAll('.year-btn')];
  const years = {};
  for (let year = 2023; year >= 1995; year--) {
    const option = document.createElement('option');
    option.value = year;
    option.textContent = year;
    select.append(option);
  }
  const escapeHTML = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const initials = name => name.split(/\s+/).map(part => part[0] || '').slice(0, 2).join('').toUpperCase();
  function showYear(year) {
    year = String(year);
    const entries = years[year] || [];
    yearButtons.forEach(button => button.classList.toggle('active', button.dataset.year === year));
    select.value = Number(year) < 2024 ? year : '';
    source.href = year === '2026' ? 'https://djmag.com/top100djs' : `https://djmag.com/top100djs/${year}`;
    count.textContent = entries.length ? `${year} · ${entries.length} DJS` : `${year} · RANKINGS LOADING`;
    if (!entries.length) {
      grid.innerHTML = '<div class="rank-empty">This year’s ranking data is still being collected. Check back shortly, or open the official DJ Mag list.</div>';
      return;
    }
    grid.innerHTML = entries.map(dj => `<article class="dj-card"><span class="dj-rank">#${dj.rank}</span>${dj.avatar ? `<img class="dj-avatar" src="${escapeHTML(dj.avatar)}" alt="${escapeHTML(dj.name)} avatar" loading="lazy" referrerpolicy="no-referrer" onerror="this.hidden=true;this.nextElementSibling.hidden=false">` : ''}<span class="dj-avatar dj-fallback" ${dj.avatar ? 'hidden' : ''} aria-hidden="true">${escapeHTML(initials(dj.name))}</span><div><div class="dj-name">${escapeHTML(dj.name)}</div><div class="dj-credit">DJ MAG TOP 100 · ${year}</div></div></article>`).join('');
  }
  yearButtons.forEach(button => button.addEventListener('click', () => showYear(button.dataset.year)));
  select.addEventListener('change', () => { if (select.value) showYear(select.value); });
  fetch(`data/top100.json?t=${Date.now()}`, {cache:'no-store'}).then(response => { if (!response.ok) throw Error('Ranking archive not ready'); return response.json(); }).then(data => { Object.assign(years, data.years || {}); showYear('2026'); }).catch(() => { count.textContent = 'RANKING ARCHIVE STARTING'; showYear('2026'); });
})();
