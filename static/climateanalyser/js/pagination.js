/**
 * For pagination; go to page i.
 * Will append the page to the URL and reload.
 *
 * @param i The page number to go to.
 */
function goToPage(i) {

   var params = getUrlParams();
   params["page"] = i;

   var l = window.location.href;

   l = l.replace(/\?.*/, '');

   l += "?" + $.param(params);

   window.location.href = l;

}

/**
 * If show is true, show just the current user's Computations.
 * Will append show_mine=true to the URL and reload.
 *
 * @param show Whether or not to show the user's Computations
 */
function showMine(show) {

   var l = window.location.href;
   var params = getUrlParams();

   l = l.replace(/\?.*/, '');
   
   if (show) {
      params['show_mine'] = true;
   }
   else {
      delete params['show_mine'];
   }

   l += "?" + $.param(params);

   window.location.href = l;

}

/**
 * Get all parameters in address as an associative object.
 * @return Parameters object
 */
function getUrlParams() {

   var l = window.location.href;
   var urlSplit = l.split(/\?|\&/);
   var i;

   var paramList = {};

   //skip the first one - it's the url
   for (i = 1; i < urlSplit.length; i++) {

      var param = urlSplit[i].split("=");

      if (param[0] != "" && param[1] != "") {
         paramList[param[0]] = param[1];
      }
   }

   console.log(paramList);

   return paramList;
}
