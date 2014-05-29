$(document).ready(function(){
	var coffeestats = {
		init: function () {
	      coffeestats.equalHeightsBoxes();
	    },

		equalHeightsBoxes : function() {
			$('.white-box').equalHeights();
		}
	}
	coffeestats.init();
});
