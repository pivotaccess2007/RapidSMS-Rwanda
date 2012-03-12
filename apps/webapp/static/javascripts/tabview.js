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
