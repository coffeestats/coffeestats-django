/* global $, sanitize_datetime */
$(document).ready(function(){
<<<<<<< HEAD
	var coffeestats = {
		init: function () {
	      coffeestats.equalHeightsBoxes();
	      coffeestats.showNavigation();
	      coffeestats.showMenuDropdown();
	      coffeestats.showLoginDropdown();
	      coffeestats.profilePage();
	      coffeestats.preventMobileKeyboard();
	    },
=======
  "use strict";
>>>>>>> FETCH_HEAD

  var coffeestats = {
    init: function () {
        coffeestats.equalHeightsBoxes();
        coffeestats.showNavigation();
        coffeestats.showMenuDropdown();
        coffeestats.showLoginDropdown();
        coffeestats.profilePage();
      },

    equalHeightsBoxes : function() {
      if (!window.matchMedia('(max-width: 873px)').matches) {
        $('.white-box').not('.fullWidth').equalHeights();
        }
    },

    showNavigation : function() {
      $('.menuIndicator').on( 'click',function(){
        $(this).toggleClass('hover', 'inactive');
      });
    },

    showMenuDropdown : function() {
      $('.mainNav li span.settings').on( 'tapstart', function(){
        $(this).parent('li').toggleClass('hover', 'inactive');
      });
    },
    showLoginDropdown : function() {
      $('.login li span').on( 'tapstart',function(){
        $(this).parent('li').toggleClass('hover', 'inactive');
      });
    },

    profilePage : function() {
      if ($('.clockpicker').length && $('.datepicker').length) {
        $('.clockpicker').clockpicker({
            autoclose: true,
            default: 'now',
          });
          $('.datepicker').datepicker({
            format: 'yyyy-mm-dd',
            todayBtn: 'linked',
            calendarWeeks: true,
            autoclose: true,
            todayHighlight: true,
          });

          $('img.toggle').click(function(event) {
              $('#' + $(this).attr('data-toggle')).toggle();
          });
          $('#coffeeform').submit(function(event) {
              return sanitize_datetime('input#id_coffeedate', 'input#id_coffeetime');
          });
          $('#mateform').submit(function(event) {
              return sanitize_datetime('input#id_matedate', 'input#id_matetime');
          });

<<<<<<< HEAD
		}

		preventMobileKeyboard : function() {
			if($('.clockpicker').length && $('.datepicker').length) {
				$('.clockpicker').on('click' function() {
					$(this).blur();
				});

			    $('.datepicker').on('click' function() {
					$(this).blur();
				});
			}

		}
	}
	coffeestats.init();
=======
          $('.clockpicker').focusout(function(){
          $(this).clockpicker('hide');
        });
        $('.datepicker').focusout(function(){
          $(this).datepicker('hide');
        });
      }

    }
  };
  coffeestats.init();
>>>>>>> FETCH_HEAD
});
