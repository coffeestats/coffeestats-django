$(document).ready(function(){var t={init:function(){t.equalHeightsBoxes(),t.showNavigation(),t.showMenuDropdown(),t.showLoginDropdown(),t.profilePage()},equalHeightsBoxes:function(){window.matchMedia("(max-width: 873px)").matches||$(".white-box").not(".fullWidth").equalHeights()},showNavigation:function(){$(".menuIndicator").on("click",function(){$(this).toggleClass("hover","inactive")})},showMenuDropdown:function(){$(".mainNav li span.settings").on("tapstart",function(){$(this).parent("li").toggleClass("hover","inactive")})},showLoginDropdown:function(){$(".login li span").on("tapstart",function(){$(this).parent("li").toggleClass("hover","inactive")})},profilePage:function(){$(".clockpicker").length&&$(".datepicker").length&&($(".clockpicker").clockpicker({autoclose:!0,"default":"now"}),$(".datepicker").datepicker({format:"yyyy-mm-dd",todayBtn:"linked",calendarWeeks:!0,autoclose:!0,todayHighlight:!0}),$("img.toggle").click(function(t){$("#"+$(this).attr("data-toggle")).toggle()}),$("#coffeeform").submit(function(t){return sanitize_datetime("input#id_coffeedate","input#id_coffeetime")}),$("#mateform").submit(function(t){return sanitize_datetime("input#id_matedate","input#id_matetime")}),$(".clockpicker").focusout(function(){$(this).clockpicker("hide")}),$(".datepicker").focusout(function(){$(this).datepicker("hide")}))}};t.init()});