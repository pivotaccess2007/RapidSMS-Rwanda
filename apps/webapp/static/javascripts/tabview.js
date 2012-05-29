function tabview_aux(TabViewId, id)
{
  var TabView = document.getElementById(TabViewId);

  // ----- Tabs -----

  var Tabs = TabView.firstChild;
  while (Tabs.className != "Tabs" ) Tabs = Tabs.nextSibling;

  var Tab = Tabs.firstChild;
  var i   = 0;

  do
  {
    if (Tab.tagName == "A")
    {
      i++;
      Tab.href      = "javascript:tabview_switch('"+TabViewId+"', "+i+");";
      Tab.className = (i == id) ? "Active" : "";
      Tab.blur();
    }
  }
  while (Tab = Tab.nextSibling);

  // ----- Pages -----

  var Pages = TabView.firstChild;
  while (Pages.className != 'Pages') Pages = Pages.nextSibling;

  var Page = Pages.firstChild;
  var i    = 0;

  do
  {
    if (Page.className == 'Page')
    {
      i++;
      if (Pages.offsetHeight) Page.style.height = (Pages.offsetHeight-2)+"px";
      Page.style.overflow = "auto";
      Page.style.display  = (i == id) ? 'block' : 'none';
    }
  }
  while (Page = Page.nextSibling);
}

// ----- Functions -------------------------------------------------------------

function tabview_switch(TabViewId, id) { tabview_aux(TabViewId, id); }

function tabview_initialize(TabViewId) { tabview_aux(TabViewId,  1); }

String.prototype.trim = function() {
	return this.replace(/^\s+|\s+$/g,"");
}
String.prototype.ltrim = function() {
	return this.replace(/^\s+/,"");
}
String.prototype.rtrim = function() {
	return this.replace(/\s+$/,"");
}

function trim(stringToTrim) {
	return stringToTrim.replace(/^\s+|\s+$/g,"");
}
function ltrim(stringToTrim) {
	return stringToTrim.replace(/^\s+/,"");
}
function rtrim(stringToTrim) {
	return stringToTrim.replace(/\s+$/,"");
}



// ........Table....Graph.....Map....

$(document).ready(function() {
	var hrefs = $('#nav li a');
	for (var i=0; i< hrefs.length; i++) $('#'+$(hrefs[i]).attr("title")).hide();
	$('#nav li a').click(function(){
		
	for (var i=0; i< hrefs.length; i++) $('#'+$(hrefs[i]).attr("title")).hide();
		var myDiv="#"+$(this).attr('title');
		var toLoad = $(this).attr('href')+' #placeholder';
				
		$('#placeholder').hide('fast',loadContent());
		
		$('#nav').append('<span id="load">LOADING...</span>');
		$('#load').fadeOut('normal');
		
		
		function loadContent() {
			
			$('#placeholder').load(toLoad,'',showNewContent());
			
		}
		function showNewContent() {
			$(myDiv).show('normal',hideLoader());
			
		}
		function hideLoader() {
			
			$('#load').fadeIn('normal');
		}
		return false;
		
	});

		

	

});



function gup( name, url )
{
  var regexS = "[\\?&]"+name+"=([^&#]*)";
  var regex = new RegExp( regexS );
  var tmpURL = url;
  var results = regex.exec( tmpURL );
  if( results == null )
    return "";
  else
    return results[1];
}
