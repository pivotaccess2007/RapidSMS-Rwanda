/*  TODO: onSelect for date pickers.    */
$(function()
{
    $('#pickstartdate').datepick({dateFormat:'dd.mm.yyyy'});
    $('#pickenddate').datepick({dateFormat:'dd.mm.yyyy'});

    $('#provchoose').change(function(evt)
    {	
        if ($(this).attr('value') != ''){window.location = (window.location.pathname + '?province=' +
        $(this).attr('value') + '&start_date=' +
        $('#pickstartdate').attr('value') + '&end_date=' + $('#pickenddate').attr('value'));
	} else {
			window.location = window.location.pathname;			
			}
    });

    condDisableDistricts();
    $('#distchoose').change(function()
    {
        if ($(this).attr('value') != ''){ window.location = (window.location.pathname + '?district=' +
        $(this).attr('value') + '&province=' + $('#provchoose').attr('value')
        + '&start_date=' + $('#pickstartdate').attr('value') + '&end_date=' +
        $('#pickenddate').attr('value'));
	}
		else {
			window.location = (window.location.pathname + '?'+ '&province=' + $('#provchoose').attr('value')
        + '&start_date=' + $('#pickstartdate').attr('value') + '&end_date=' +
        $('#pickenddate').attr('value'));			
			}
    });

    condDisableLocations();
    $('#locchoose').change(function()
    {
       if ($(this).attr('value') != '') { window.location = (window.location.pathname + '?location=' +
        $(this).attr('value') + '&province=' + $('#provchoose').attr('value') +
        '&district=' + $('#distchoose').attr('value') + '&start_date=' +
        $('#pickstartdate').attr('value') + '&end_date=' + $('#pickenddate').attr('value'));
	} 
		else{
			window.location = (window.location.pathname + '?' + '&province=' + $('#provchoose').attr('value') +
        '&district=' + $('#distchoose').attr('value') + '&start_date=' +
        $('#pickstartdate').attr('value') + '&end_date=' + $('#pickenddate').attr('value'));
			}
    });
});

function condDisableDistricts()
{
    var loc = window.location.toString();
    if(loc.search(/province/) != -1) return;
    $('#distchoose').hide();
}

function condDisableLocations()
{
    var loc = window.location.toString();
    if(loc.search(/district/) != -1) return;
    $('#locchoose').hide();
}
