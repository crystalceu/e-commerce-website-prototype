document.addEventListener('DOMContentLoaded', function() {
    if (device_type() == 'pc') {
        // Dropdown account menu
        document.querySelector('#_account_button').addEventListener('mousemove', () => show_dropdown('account'));
        document.querySelector('#_account_button').addEventListener('mouseout', () => close_dropdown('account'));
        // Dropdown menu on small screen
        document.querySelector('#brand').addEventListener('mousemove', () => show_dropdown('all'));
        document.querySelector('#brand').addEventListener('mouseout', () => close_dropdown('all'));

        /*document.querySelector('#star1').addEventListener('mousemove', () => show_rating(1));
        document.querySelector('#star1').addEventListener('mouseout', () => hide_rating());

        document.querySelector('#star2').addEventListener('mousemove', () => show_rating(2));
        document.querySelector('#star2').addEventListener('mouseout', () => hide_rating());

        document.querySelector('#star3').addEventListener('mousemove', () => show_rating(3));
        document.querySelector('#star3').addEventListener('mouseout', () => hide_rating());

        document.querySelector('#star4').addEventListener('mousemove', () => show_rating(4));
        document.querySelector('#star4').addEventListener('mouseout', () => hide_rating());

        document.querySelector('#star5').addEventListener('mousemove', () => show_rating(5));
        document.querySelector('#star5').addEventListener('mouseout', () => hide_rating());*/
    }
    else {
        // Dropdown for mobile
        document.querySelector('#dropdown-button').addEventListener('click', () => show_dropdown('mobile'));
    }

    document.querySelector('#star1').addEventListener('click', () => set_rating(1));
    document.querySelector('#star2').addEventListener('click', () => set_rating(2));
    document.querySelector('#star3').addEventListener('click', () => set_rating(3));
    document.querySelector('#star4').addEventListener('click', () => set_rating(4));
    document.querySelector('#star5').addEventListener('click', () => set_rating(5));
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

function show_rating(count) {
    for (i = 1; i < count + 1; i++) {
        document.querySelector(`#star${i}`).src = '/static/shop/star.png';
    }
    for (let i = count + 1; i < 6; i++) {
        document.querySelector(`#star${i}`).src = '/static/shop/star-empty.png';
    }
}

function hide_rating() {
    for (i = 1; i < 6; i++) {
        document.querySelector(`#star${i}`).src = '/static/shop/star-empty.png';
    }
}

function set_rating(count) {
    for (let i = 1; i < count + 1; i++) {
        document.querySelector(`#star${i}`).src = '/static/shop/star.png';
    }
    for (let i = count + 1; i < 6; i++) {
        document.querySelector(`#star${i}`).src = '/static/shop/star-empty.png';
    }

    var rating_input = document.getElementById("rating-id");
    rating_input.value = count;
}