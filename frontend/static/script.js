// frontend/static/scripts.js

document.addEventListener('DOMContentLoaded', function() {

    console.log(structured_json)
    const structured_json_cleared = structured_json.replaceAll('&#34;', '"').replaceAll('{"', '\n\n {"').replaceAll(', "', '\n  "').replaceAll('[', '').replaceAll(']', '')
    document.getElementById('jsonOutput').innerText  = structured_json_cleared;

});