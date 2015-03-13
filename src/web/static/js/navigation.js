$(document).ready(function() {

	// Menu Dropdown
	$('.main-navigation li:not(.current) ul').hide(); //Hide all sub menus
	$('.main-navigation li a:not(.current )').not('.main-navigation li a.no-submenu, .main-navigation li li a').click(
		function () {
			$(this).parent().siblings().find('ul').slideUp('normal'); // Slide up all menus except the one clicked
			$(this).parent().find('ul').slideToggle('normal'); // Slide down the clicked sub menu
			return false;
		}
	);
    $('.main-navigation li a.no-submenu, .main-navigation li li a').click(
		function () {
            $('.main-navigation li.current').removeClass("current");
            $(this.parentNode.parentNode.parentNode).addClass("current");
            return true;
		}
	);
});
