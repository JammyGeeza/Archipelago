// Only handles the List View / Spreadsheet View toggle. Everything
// else on this page (search, expand/collapse, Steam ownership check,
// Group by Category) is handled by the shared supportedGames.js,
// loaded alongside this file.

window.addEventListener('load', () => {
    const viewToggle = document.getElementById('view-toggle');
    const listView = document.getElementById('dev-games-list-view');
    const spreadsheetView = document.getElementById('dev-games-spreadsheet-view');
    const listLabel = document.getElementById('view-toggle-list-label');
    const spreadsheetLabel = document.getElementById('view-toggle-spreadsheet-label');
  
    if (!viewToggle) {
      return;
    }
  
    // Default OFF (List View) - never persisted, resets every load.
    viewToggle.checked = false;
  
    const applyView = () => {
      const showSpreadsheet = viewToggle.checked;
      listView.classList.toggle('hidden', showSpreadsheet);
      spreadsheetView.classList.toggle('hidden', !showSpreadsheet);
      listLabel.classList.toggle('inactive', showSpreadsheet);
      spreadsheetLabel.classList.toggle('inactive', !showSpreadsheet);
    };
  
    viewToggle.addEventListener('change', applyView);
    applyView();
  });