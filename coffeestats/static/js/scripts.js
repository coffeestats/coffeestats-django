$(document).ready(function(){
	var coffeestats = {
		init: function () {
	      coffeestats.equalHeightsBoxes();
	      coffeestats.showNavigation();
	      coffeestats.showMenuDropdown();
	      coffeestats.showLoginDropdown();
	    },

		equalHeightsBoxes : function() {
			$('.white-box').not('.fullWidth').equalHeights();
		},

		showNavigation : function() {
			$('.menuIndicator').click(function(){
				$(this).toggleClass('hover');
			});
		},

		showMenuDropdown : function() {
			$('.mainNav li span.settings').click(function(){
				$(this).parent('li').toggleClass('hover');
			});
		},
		showLoginDropdown : function() {
			$('.login li span').click(function(){
				$(this).parent('li').toggleClass('hover');
			});
		}
	}
	coffeestats.init();
});
