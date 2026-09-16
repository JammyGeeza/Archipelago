const STEAM_COOKIE_NAME = 'ap_steam_id';
const GROUP_BY_CATEGORY_COOKIE = 'ap_group_by_category';

// Two tier maps, used depending on whether an ownership check has
// happened yet. Before a check, only platform is known (rendered
// server-side into data-platform). After a check, dataset.tier gets
// set explicitly from the backend's status - see getEffectiveTier().
const PRE_CHECK_TIER = {
  steam: 0,
  native: 1,
  emulator: 2,
  other: 3,
};
const POST_CHECK_TIER = {
  owned: 0,
  native: 1,
  emulator: 2,
  other: 3,
  not_owned: 4,
};
const UNCATALOGUED_TIER = 5;

// URLs for each icon, read once on load from data attributes on
// #games (rendered server-side via url_for, so JS never hardcodes
// a static path). See loadIconUrls().
let ICON_URLS = {};

function loadIconUrls() {
  const gamesEl = document.getElementById('games');
  ICON_URLS = {
    steam: gamesEl.dataset.iconSteam,
    steamGreen: gamesEl.dataset.iconSteamGreen,
    steamRed: gamesEl.dataset.iconSteamRed,
    native: gamesEl.dataset.iconNative,
    emulator: gamesEl.dataset.iconEmulator,
    other: gamesEl.dataset.iconOther,
  };
}

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

// Captured once on load. Used for iterating every game's <details>
// element when applying/resetting ownership data.
let originalOrder = [];

window.addEventListener('load', () => {
  loadIconUrls();

  // ----------------------------------------------------
  // Existing behaviour (search, expand/collapse) - unchanged
  // ----------------------------------------------------

  const toggleButtons = document.querySelectorAll('details');

  originalOrder = Array.from(toggleButtons);

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
  // Group by Category toggle
  // ----------------------------------------------------

  const groupToggle = document.getElementById('group-by-category');
  const savedGroupPref = getCookie(GROUP_BY_CATEGORY_COOKIE);
  // Default OFF. Always usable - platform categories (Steam/native/
  // emulator/other) exist from page load, before any Steam check.
  groupToggle.checked = savedGroupPref === 'true';

  groupToggle.addEventListener('change', () => {
    setCookie(GROUP_BY_CATEGORY_COOKIE, groupToggle.checked ? 'true' : 'false', 365);
    renderList();
  });

  // Apply the saved preference immediately - pre-check categories
  // (Steam/native/emulator/other) already exist from the server
  // render, so this can group without waiting on any Steam check.
  renderList();

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
      renderList();
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

// Update each <details> based on the status data returned from the
// backend, keyed by game name. Games absent from the response
// (uncatalogued - shouldn't happen in practice) are left completely
// untouched, same as before any check.
function applyOwnershipData(gamesData) {
  originalOrder.forEach((details) => {
    const gameName = details.getAttribute('data-game');
    const info = gamesData[gameName];

    // Always clear any previously-injected store link first.
    const existingLink = details.querySelector('.steam-store-link');
    if (existingLink) {
      existingLink.remove();
    }

    if (!info) {
      details.dataset.tier = '';
      details.dataset.sortPrice = '';
      return;
    }

    details.dataset.tier = String(POST_CHECK_TIER[info.status]);

    if (info.status !== 'owned' && info.status !== 'not_owned') {
      // native / emulator / other - icon and name never change,
      // only the sort tier does.
      details.dataset.sortPrice = '';
      return;
    }

    const icon = details.querySelector('.game-icon');
    const nameSpan = details.querySelector('.game-name-text');

    if (info.status === 'owned') {
      details.dataset.sortPrice = '';
      if (icon) {
        icon.src = ICON_URLS.steamGreen;
        icon.alt = 'Owned on Steam';
      }
      if (nameSpan) {
        nameSpan.textContent = gameName;
      }
    } else {
      // not_owned
      details.dataset.sortPrice = typeof info.sortPrice === 'number' ? String(info.sortPrice) : '';
      if (icon) {
        icon.src = ICON_URLS.steamRed;
        icon.alt = 'Not owned on Steam';
      }
      if (nameSpan) {
        nameSpan.textContent = `${gameName} - ${info.price}`;
      }

      if (info.url) {
        const link = document.createElement('p');
        link.className = 'steam-store-link';
        link.innerHTML = `<a href="${info.url}" target="_blank" rel="noopener noreferrer">View on Steam Store</a>`;
        // Insert right after the summary, as the first line of the expanded body.
        details.querySelector('summary').insertAdjacentElement('afterend', link);
      }
    }
  });
}

// Resolves the current sort tier for a game, whether or not an
// ownership check has happened yet. Post-check (dataset.tier set)
// takes priority; otherwise falls back to the pre-check platform tier.
function getEffectiveTier(details) {
  if (details.dataset.tier !== undefined && details.dataset.tier !== '') {
    return parseInt(details.dataset.tier, 10);
  }

  const platform = details.dataset.platform;
  if (platform && PRE_CHECK_TIER[platform] !== undefined) {
    return PRE_CHECK_TIER[platform];
  }

  return UNCATALOGUED_TIER;
}

// Dispatches to the right ordering based on the Group by Category
// toggle. Called both right after a fresh ownership check and
// whenever the toggle itself is flipped - reordering is instant,
// no re-fetch, since it only ever rearranges DOM nodes already
// annotated with dataset.tier/sortPrice from the last check.
function renderList() {
  const groupToggle = document.getElementById('group-by-category');
  if (groupToggle && groupToggle.checked) {
    sortGames();
  } else {
    sortAlphabeticalOnly();
  }
}

// Six possible tiers depending on check state - see PRE_CHECK_TIER/
// POST_CHECK_TIER/getEffectiveTier above.
function sortGames() {
  const container = document.getElementById('games');
  const details = Array.from(document.querySelectorAll('#games details'));

  details.sort((a, b) => {
    const tierA = getEffectiveTier(a);
    const tierB = getEffectiveTier(b);

    if (tierA !== tierB) return tierA - tierB;

    if (tierA === POST_CHECK_TIER.not_owned) {
      const aPrice = a.dataset.sortPrice === '' || a.dataset.sortPrice === undefined ? Infinity : parseFloat(a.dataset.sortPrice);
      const bPrice = b.dataset.sortPrice === '' || b.dataset.sortPrice === undefined ? Infinity : parseFloat(b.dataset.sortPrice);
      if (aPrice !== bPrice) return aPrice - bPrice;
    }

    return titleSortKey(a.getAttribute('data-game')).localeCompare(titleSortKey(b.getAttribute('data-game')));
  });

  details.forEach((el) => container.appendChild(el));
}

// Plain alphabetical order, completely ignoring tier/ownership -
// used when Group by Category is switched off. Annotations
// (emoji/price/store link) are left in place; only the ORDER changes.
function sortAlphabeticalOnly() {
  const container = document.getElementById('games');
  const details = Array.from(document.querySelectorAll('#games details'));

  details.sort((a, b) =>
    titleSortKey(a.getAttribute('data-game')).localeCompare(titleSortKey(b.getAttribute('data-game')))
  );

  details.forEach((el) => container.appendChild(el));
}

// Strip all ownership annotations, restoring each game to its
// pre-check state (neutral Steam icon where applicable; native/
// emulator/other/uncatalogued never changed in the first place),
// then re-render using whatever the Group by Category toggle is
// currently set to.
function resetOwnership() {
  originalOrder.forEach((details) => {
    details.dataset.tier = '';
    details.dataset.sortPrice = '';

    if (details.dataset.platform === 'steam') {
      const icon = details.querySelector('.game-icon');
      const nameSpan = details.querySelector('.game-name-text');
      if (icon) {
        icon.src = ICON_URLS.steam;
        icon.alt = 'Steam';
      }
      if (nameSpan) {
        nameSpan.textContent = details.getAttribute('data-game');
      }
    }

    const existingLink = details.querySelector('.steam-store-link');
    if (existingLink) {
      existingLink.remove();
    }
  });

  renderList();
}