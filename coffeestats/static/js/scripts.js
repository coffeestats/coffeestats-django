$(document).ready(function(){
	var coffeestats = {
		init: function () {
	      coffeestats.equalHeightsBoxes();
	    },

		equalHeightsBoxes : function() {
			$('.white-box').not('.fullWidth').equalHeights();
		}
	}
	coffeestats.init();
});
