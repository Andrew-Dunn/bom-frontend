(function($){
   $(window).ready(function(){
   // First
   var wmsResource = resultPath.split('?')[0];
   var rangeURL = "/get_data_range?wms_resource="
                  + encodeURIComponent(wmsResource)
                  + "&layer=" + encodeURIComponent(calculation);

   var smallest = -50;
   var largest = 50;

   var WmsLegend = L.Control.extend({
      options: {
        position: 'topright'
      },
      onAdd: function (map) {
         // create the control container with a particular class name
         var container = L.DomUtil.create('div', 'wms-legend');
         container.className += " leaflet-bar";
         // Need to subtract 2 from img height to account for borders.
         var content = "<div class='content'><img src='" +
                       wmsResource +
                          "?REQUEST=GetLegendGraphic" +
                          "&COLORBARONLY=true" +
                          "&PALETTE=climate_analyser" +
                          "&WIDTH=20&HEIGHT=" + (this.height - 2) + "' />" +
                          "<table cellpadding='0' cellspacing='0' style='" + 
                             "height: " + this.height + "px'>" +
                          "<tr><td style='padding: 0;'>&nbsp;</td>";
         if (this.high <= 0 || this.low >= 0) {
            content += "<td style='padding: 0;'>" +
                       "<span class='value'>" + this.high + "</span>";
            content += "    <span class='value'>" + this.low + "</span></td>";
         } else {
            var posPC = this.high / (this.high - this.low);
            content += "<td style='height: " + (100 * posPC) + "%; "+
                       "position: relative; padding: 0;" + "'>" +
                       "<span class='value'>" + this.high + "</span></td>";
            content += "</tr>" +
                          "<tr><td style='padding: 0;'>&nbsp;</td>" +
                          "<td style='" +
                          "position: relative; padding: 0;" + "'>" +
                          "<span class='value'>0</span>" +
                          "<span class='value' >" + this.low + "</span></td>";
         }
         content += "</tr></table></div>";
         container.innerHTML = content;
         return container;
      },
      initialize: function (height, low, high, options) {
         this.height = height;
         this.low = Math.round(low * 10) / 10;
         this.high = Math.round(high * 10) / 10;
         L.Util.setOptions(this, options);
      }
   });

   $.ajax({
     url: rangeURL
   })
   .done(function( data ) {
      smallest = data.min;
      largest = data.max;

      var map = L.map('map').setView([-37.81, 144.96], 2);
      var popup = L.popup().setContent("<p>Hi</p>");
      var displayMarker = false;
      var layer = L.tileLayer.wms(wmsResource, {
               layers: calculation,
               format: 'image/png',   
               transparent: true,
               attribution: "Climate Analyser",
               COLORSCALERANGE: smallest + "%2C" + largest
               }).addTo(map);

      L.tileLayer(tilemillServerAddress + '/v2/CountryOutlines/{z}/{x}/{y}.png',{
               maxZoom: 8,
               detectRetina: true
               }).addTo(map);
      map.addControl(new WmsLegend(400, smallest, largest));

      map.on('click', function(e) {
         popup.setLatLng(e.latlng);

         var lon = e.latlng.lng;
         if (lon <= -180.0) {
            lon = 180.0 - ((-(lon + 180.0)) % 360.0);
         }
         if (lon > 180.0) {
            lon = ((lon + 180.0) % 360.0) - 180.0;
         }
         var valueURL = "/get_data_value?wms_resource="
                        + encodeURIComponent(wmsResource)
                        + "&layer=" + encodeURIComponent(calculation)
                        + "&lat=" + e.latlng.lat
                        + "&lon=" + lon;

         $.ajax({
            url: valueURL
         })
         .done(function( data ) {
            popup.setContent("<p><strong>Value: </strong>"+data.value+"</p>");
            if (!displayMarker) {
               popup.addTo(map);
            }
         });
      });
   });});
})(jQuery);
