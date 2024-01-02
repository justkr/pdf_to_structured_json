// frontend/static/scripts.js

document.addEventListener('DOMContentLoaded', function() {

    const structured_json_cleared = structured_json
        .replaceAll('&#34;', '"')
        .replaceAll('&gt;', '>')
        .replaceAll('{"', '\n\n {"')
        .replaceAll(', "', '\n  "')
        .replaceAll('[', '')
        .replaceAll(']', '');

    document.getElementById('jsonOutput').textContent  = structured_json_cleared;

});