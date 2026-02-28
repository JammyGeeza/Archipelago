window.addEventListener('load', () => {
    document.getElementById('host-game-button').addEventListener('click', () => {
        document.getElementById('file-input').click();
    });

    document.getElementById('file-input').addEventListener('change', () => {
        document.getElementById('host-game-form').submit();
    });

    // Add event listener, only if found (as it will not be rendered if no password required)
    document.getElementById('host-password-input')?.addEventListener('change', (evt) => {
        document.getElementById('host-password').value = evt.target.value;
    });
});
