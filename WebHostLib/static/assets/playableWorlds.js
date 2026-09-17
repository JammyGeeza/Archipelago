// Only handles the List View / Spreadsheet View toggle. Everything
// else on this page (search, expand/collapse, Steam ownership check,
// Group by Category) is handled by the shared supportedGames.js,
// loaded alongside this file.

window.addEventListener('load', () => {
    const viewToggle = document.getElementById('view-toggle');
    const gamesEl = document.getElementById('games');
    const listLabel = document.getElementById('view-toggle-list-label');
    const spreadsheetLabel = document.getElementById('view-toggle-spreadsheet-label');
  
    if (!viewToggle) {
      return;
    }
  
    // Default OFF (List View) - never persisted, resets every load.
    viewToggle.checked = false;
  
    const applyView = () => {
      const showSpreadsheet = viewToggle.checked;
      // Toggling a class on #games itself (rather than a wrapper div)
      // survives supportedGames.js re-parenting every <details> to be
      // a direct child of #games on every sort - see playableWorlds.css.
      gamesEl.classList.toggle('spreadsheet-mode', showSpreadsheet);
      listLabel.classList.toggle('inactive', showSpreadsheet);
      spreadsheetLabel.classList.toggle('inactive', !showSpreadsheet);
    };
  
    viewToggle.addEventListener('change', applyView);
    applyView();
  });