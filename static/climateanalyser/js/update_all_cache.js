/**
 * This is used by 'Update Cache' button in the admin backend.
 *
 * It updates every datafile's cache via ajax.
 *
 */
(function($){

   $(document).ready(function() {

      $("#update_datafile_cache").click(function(e) {
         e.preventDefault();

         $blanket = $("#update_cache_blanket");

         // show loading blanket
         $blanket.show();

         // do update
         $.ajax({
            url: "/update_datafile_cache"
         }).done(function(response){
            //hide blanket on success
            if (response == "success") {
               $blanket.hide();
            };
         });

         return false;
      });

   });

})(django.jQuery);
