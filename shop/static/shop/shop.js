document.addEventListener('DOMContentLoaded', function() {
    if (device_type() == 'pc') {
        // Dropdown account menu
        document.querySelector('#_account_button').addEventListener('mousemove', () => show_dropdown('account'));
        document.querySelector('#_account_button').addEventListener('mouseout', () => close_dropdown('account'));
        // Dropdown menu on small screen
        document.querySelector('#brand').addEventListener('mousemove', () => show_dropdown('all'));
        document.querySelector('#brand').addEventListener('mouseout', () => close_dropdown('all'));
    }
    else {
        // Dropdown for mobile
        document.querySelector('#dropdown-button').addEventListener('click', () => show_dropdown('mobile'));
    }
});

function device_type() {
    let useragent = navigator.userAgent;
    if (useragent.includes('iPhone') || useragent.includes('Android') || useragent.includes('iPad')) {
        return ('mobile');
    }
    else {
        return('pc');
    }
}

function show_dropdown(dropdown_block) {
    if (dropdown_block == 'all') {
        document.querySelector(`#_dropdown_navbar`).style.display = 'block';
        if (window.location.href == 'http://127.0.0.1:8000/') {
            document.querySelector(`#_dropdown_navbar`).style.height = '0px';
        }
        else {
            document.querySelector(`#_dropdown_navbar`).style.height = '230px';
        }
    }
    if (dropdown_block == 'account') {
        document.querySelector(`#_account_dropdown`).style.display = 'block';
    }
    if (dropdown_block == 'mobile') {
        if (document.querySelector(`#dropdown-mobile`).style.display == 'block') {
            document.querySelector(`#dropdown-mobile`).style.display = 'none';
            document.querySelector(`#dropdown-mobile`).style.height = '0px';
            document.querySelector(`#dropdown-button`).style.backgroundImage = 'url(/static/shop/dropdown.svg)';
        }
        else {
            document.querySelector(`#dropdown-mobile`).style.display = 'block';
            document.querySelector(`#dropdown-mobile`).style.height = '1368px';
            document.querySelector(`#dropdown-button`).style.backgroundImage = 'url(/static/shop/dropup.svg)';
        }
    }
}

function close_dropdown(dropdown_block) {
    if (dropdown_block == 'all') {
        document.querySelector(`#_dropdown_navbar`).style.display = 'none';
        document.querySelector(`#_dropdown_navbar`).style.height = '0';
    }
    if (dropdown_block == 'account') {
        document.querySelector(`#_account_dropdown`).style.display = 'none';
    }
}