const STEAM_COOKIE_NAME = 'ap_steam_id';

// The five sort/display groups, top to bottom. Uncatalogued (no row
// in the backend's game table at all) always sorts last, and is
// deliberately a full tier beyond "not owned" - not lumped in with it.
const STATUS_TIER = {
  owned: 0,
  emulator: 1,
  itch: 2,
  not_owned: 3,
};
const UNCATALOGUED_TIER = 4;

const STATUS_EMOJI = {
  owned: '✅',
  emulator: '💿',
  itch: '❔',
  not_owned: '❌',
};

// Mirrors Utils.title_sorted() in the Python codebase - sorts
// ignoring a leading "a" or "the" so e.g. "The Legend of Zelda"
// sorts under "L", matching the same ordering the template already
// uses for the initial (pre-ownership-check) game list.
const TITLE_SORT_IGNORE_WORDS = new Set(['a', 'the']);

function titleSortKey(title) {
  const spaceIndex = title.indexOf(' ');
  if (spaceIndex === -1) {
    return title.toLowerCase();
  }
  const firstWord = title.slice(0, spaceIndex).toLowerCase();
  const rest = title.slice(spaceIndex + 1);
  return TITLE_SORT_IGNORE_WORDS.has(firstWord) ? rest.toLowerCase() : title.toLowerCase();
}

// ============================================================
// COOKIE HELPERS
// ============================================================
// The userID/vanity name is public information (it's literally
// visible on the person's own Steam profile URL), so this is
// stored in plain text on purpose - no need to obscure it.

function setCookie(name, value, days) {
  const maxAge = days * 24 * 60 * 60;
  document.cookie = `${name}=${encodeURIComponent(value)}; max-age=${maxAge}; path=/; SameSite=Lax`;
}

function getCookie(name) {
  const match = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : null;
}

function deleteCookie(name) {
  document.cookie = `${name}=; max-age=0; path=/; SameSite=Lax`;
}

// ============================================================
// STATE
// ============================================================

// Captured once on load. This is the original alphabetical
// order the Jinja template already renders (via title_sorted),
// so it doubles as our "reset to default" order.
let originalOrder = [];

// Original summary text for each <details>, keyed by element,
// so we can restore "Aquaria" after it's been rewritten to
// "✅ Aquaria" or "❌ Aquaria - £9.99".
const originalSummaryText = new Map();

window.addEventListener('load', () => {
  // ----------------------------------------------------
  // Existing behaviour (search, expand/collapse) - unchanged
  // ----------------------------------------------------

  const toggleButtons = document.querySelectorAll('details');

  originalOrder = Array.from(toggleButtons);
  originalOrder.forEach((details) => {
    const summary = details.querySelector('summary');
    if (summary) {
      originalSummaryText.set(details, summary.textContent);
    }
  });

  const gameSearch = document.getElementById('game-search');
  gameSearch.value = '';
  gameSearch.addEventListener('input', (evt) => {
    if (!evt.target.value.trim()) {
      // If input is empty, display all games as collapsed
      return toggleButtons.forEach((header) => {
        header.style.display = null;
        header.removeAttribute('open');
      });
    }

    // Loop over all the games
    toggleButtons.forEach((header) => {
      // If the game name includes the search string, display the game. If not, hide it
      if (header.getAttribute('data-game').toLowerCase().includes(evt.target.value.toLowerCase())) {
        header.style.display = null;
        header.setAttribute('open', '1');
      } else {
        header.style.display = 'none';
        header.removeAttribute('open');
      }
    });
  });

  document.getElementById('expand-all').addEventListener('click', expandAll);
  document.getElementById('collapse-all').addEventListener('click', collapseAll);

  // ----------------------------------------------------
  // Steam ownership feature
  // ----------------------------------------------------

  const steamUserInput = document.getElementById('steam-user');
  const rememberCheckbox = document.getElementById('remember-id');
  const steamCheckButton = document.getElementById('steam-check');
  const steamForgetButton = document.getElementById('steam-forget');

  steamCheckButton.addEventListener('click', () => {
    const value = steamUserInput.value.trim();

    if (!value) {
      showSteamError('Please enter a Steam UserID or vanity name.');
      return;
    }

    if (rememberCheckbox.checked) {
      setCookie(STEAM_COOKIE_NAME, value, 365);
    } else {
      deleteCookie(STEAM_COOKIE_NAME);
    }

    runSteamCheck(value);
  });

  // Unchecking immediately forgets - no need to click submit again.
  rememberCheckbox.addEventListener('change', () => {
    if (!rememberCheckbox.checked) {
      deleteCookie(STEAM_COOKIE_NAME);
    }
  });

  steamForgetButton.addEventListener('click', () => {
    deleteCookie(STEAM_COOKIE_NAME);
    steamUserInput.value = '';
    rememberCheckbox.checked = false;
    hideSteamError();
    resetOwnership();
  });

  // On load: if we have a saved userID, re-run the check
  // automatically against fresh data (results are never cached
  // in the cookie, only the ID itself).
  const savedId = getCookie(STEAM_COOKIE_NAME);
  if (savedId) {
    steamUserInput.value = savedId;
    rememberCheckbox.checked = true;
    runSteamCheck(savedId);
  }
});

const expandAll = () => {
  document.querySelectorAll('details').forEach((detail) => {
    detail.setAttribute('open', '1');
  });
};

const collapseAll = () => {
  document.querySelectorAll('details').forEach((detail) => {
    detail.removeAttribute('open');
  });
};

// ============================================================
// STEAM OWNERSHIP CHECK
// ============================================================

function showSteamError(message) {
  const errorEl = document.getElementById('steam-error');
  errorEl.textContent = message;
  errorEl.classList.add('visible');
}

function hideSteamError() {
  const errorEl = document.getElementById('steam-error');
  errorEl.textContent = '';
  errorEl.classList.remove('visible');
}

function runSteamCheck(user) {
  hideSteamError();

  const steamCheckButton = document.getElementById('steam-check');
  steamCheckButton.disabled = true;
  steamCheckButton.textContent = 'Checking...';

  fetch('/api/steam_ownership', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (!data.success) {
        showSteamError(data.error || 'Profile not found, check your profile is public');
        resetOwnership();
        return;
      }

      applyOwnershipData(data.games);
      sortGames();
    })
    .catch(() => {
      showSteamError('Something went wrong checking your Steam library. Please try again.');
      resetOwnership();
    })
    .finally(() => {
      steamCheckButton.disabled = false;
      steamCheckButton.textContent = 'Check My Games';
    });
}

// Rewrite each <details> summary/body based on the status data
// returned from the backend, keyed by game name. Games absent from
// the response (uncatalogued) are left completely untouched.
function applyOwnershipData(gamesData) {
  originalOrder.forEach((details) => {
    const gameName = details.getAttribute('data-game');
    const info = gamesData[gameName];

    // Always clear any previously-injected store link first.
    const existingLink = details.querySelector('.steam-store-link');
    if (existingLink) {
      existingLink.remove();
    }

    const summary = details.querySelector('summary');

    if (!info) {
      // Uncatalogued - no annotation, sits at the very bottom.
      details.dataset.tier = String(UNCATALOGUED_TIER);
      details.dataset.sortPrice = '';
      if (summary) {
        summary.textContent = originalSummaryText.get(details);
      }
      return;
    }

    const tier = STATUS_TIER[info.status];
    const emoji = STATUS_EMOJI[info.status];
    details.dataset.tier = String(tier);

    if (info.status === 'not_owned') {
      details.dataset.sortPrice = typeof info.sortPrice === 'number' ? String(info.sortPrice) : '';
      if (summary) {
        summary.textContent = `${emoji} ${gameName} - ${info.price}`;
      }

      if (info.url) {
        const link = document.createElement('p');
        link.className = 'steam-store-link';
        link.innerHTML = `<a href="${info.url}" target="_blank" rel="noopener noreferrer">View on Steam Store</a>`;
        // Insert right after the summary, as the first line of the expanded body.
        summary.insertAdjacentElement('afterend', link);
      }
    } else {
      // owned / emulator / itch - just the emoji, no price line.
      details.dataset.sortPrice = '';
      if (summary) {
        summary.textContent = `${emoji} ${gameName}`;
      }
    }
  });
}

// Five groups, in tier order: owned -> emulator -> itch -> not owned
// (cheapest first) -> uncatalogued (alphabetical, untouched).
function sortGames() {
  const container = document.getElementById('games');
  const details = Array.from(document.querySelectorAll('#games details'));

  details.sort((a, b) => {
    const tierA = a.dataset.tier === undefined || a.dataset.tier === '' ? UNCATALOGUED_TIER : parseInt(a.dataset.tier, 10);
    const tierB = b.dataset.tier === undefined || b.dataset.tier === '' ? UNCATALOGUED_TIER : parseInt(b.dataset.tier, 10);

    if (tierA !== tierB) return tierA - tierB;

    if (tierA === STATUS_TIER.not_owned) {
      const aPrice = a.dataset.sortPrice === '' ? Infinity : parseFloat(a.dataset.sortPrice);
      const bPrice = b.dataset.sortPrice === '' ? Infinity : parseFloat(b.dataset.sortPrice);
      if (aPrice !== bPrice) return aPrice - bPrice;
    }

    return titleSortKey(a.getAttribute('data-game')).localeCompare(titleSortKey(b.getAttribute('data-game')));
  });

  details.forEach((el) => container.appendChild(el));
}

// Strip all annotations and restore the default, alphabetical,
// un-checked list.
function resetOwnership() {
  const container = document.getElementById('games');

  originalOrder.forEach((details) => {
    details.dataset.tier = '';
    details.dataset.sortPrice = '';

    const summary = details.querySelector('summary');
    if (summary) {
      summary.textContent = originalSummaryText.get(details);
    }

    const existingLink = details.querySelector('.steam-store-link');
    if (existingLink) {
      existingLink.remove();
    }
  });

  originalOrder.forEach((el) => container.appendChild(el));
}