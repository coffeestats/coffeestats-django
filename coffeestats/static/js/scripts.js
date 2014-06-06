$(document).ready(function(){
	var coffeestats = {
		init: function () {
	      coffeestats.equalHeightsBoxes();
	      coffeestats.showNavigation();
	      coffeestats.showMenuDropdown();
	      coffeestats.showLoginDropdown();
	    },

		equalHeightsBoxes : function() {
			var explore = $('body.explore').length;
			if(!explore) {
				$('.white-box').not('.fullWidth').equalHeights();
			}
		},

		showNavigation : function() {
			$('.menuIndicator').on( 'tapstart',function(){
				$(this).toggleClass('hover');
			});
		},

		showMenuDropdown : function() {
			$('.mainNav li span.settings').on( 'tapstart', function(){
				$(this).parent('li').toggleClass('hover');
			});
		},
		showLoginDropdown : function() {
			$('.login li span').on( 'tapstart',function(){
				$(this).parent('li').toggleClass('hover');
			});
		},

		isTouchDevice : function() {

		}
	}
	coffeestats.init();
});
