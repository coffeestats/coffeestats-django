$(document).ready(function(){var t={init:function(){t.equalHeightsBoxes(),t.showNavigation(),t.showMenuDropdown(),t.showLoginDropdown(),t.profilePage()},equalHeightsBoxes:function(){var t=$("body.explore").length;t||$(".white-box").not(".fullWidth").equalHeights()},showNavigation:function(){$(".menuIndicator").on("tapstart",function(){$(this).toggleClass("hover","inactive")})},showMenuDropdown:function(){$(".mainNav li span.settings").on("tapstart",function(){$(this).parent("li").toggleClass("hover","inactive")})},showLoginDropdown:function(){$(".login li span").on("tapstart",function(){$(this).parent("li").toggleClass("hover","inactive")})},isTouchDevice:function(){},profilePage:function(){$(".clockpicker").clockpicker({autoclose:!0,"default":"now"}),$(".datepicker").datepicker({format:"yyyy-mm-dd",todayBtn:"linked",calendarWeeks:!0,autoclose:!0,todayHighlight:!0}),$("img.toggle").click(function(t){$("#"+$(this).attr("data-toggle")).toggle()}),$("#coffeeform").submit(function(t){return sanitize_datetime("input#id_coffeedate","input#id_coffeetime")}),$("#mateform").submit(function(t){return sanitize_datetime("input#id_matedate","input#id_matetime")}),$(".clockpicker").focusout(function(){$(this).clockpicker("hide")}),$(".datepicker").focusout(function(){$(this).datepicker("hide")})}};t.init()});