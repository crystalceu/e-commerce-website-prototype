document.addEventListener('DOMContentLoaded', function() {

    var cart = [];
    // Use mousemove to make dropdown menu visible
    document.querySelector('#food').addEventListener('mousemove', () => show_dropdown('food-dropdown'));
    document.querySelector('#care').addEventListener('mousemove', () => show_dropdown('care-dropdown'));
    document.querySelector('#accessories').addEventListener('mousemove', () => show_dropdown('accessories-dropdown'));
    document.querySelector('#food').addEventListener('mouseout', () => close_dropdown('food-dropdown'));
    document.querySelector('#care').addEventListener('mouseout', () => close_dropdown('care-dropdown'));
    document.querySelector('#accessories').addEventListener('mouseout', () => close_dropdown('accessories-dropdown'));

});

function show_dropdown(dropdown_block) {
    console.log(dropdown_block);
    document.querySelector(`#${dropdown_block}`).style.display = 'block';
}

function close_dropdown(dropdown_block) {
    document.querySelector(`#${dropdown_block}`).style.display = 'none';
}