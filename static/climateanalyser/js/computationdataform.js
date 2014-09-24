(function($){

   $(document).ready(function(){

      var $form = $("form");

      /**
       * Populate the variables multi-selectbox based on the selected datafile.
       *
       * Will make an ajax call to get list of variables to use.
       */
      function populateVariables(datafileSelect) {

         // get multi-selectbox for variables
         var $variablesSelect = $("#" + $(datafileSelect).attr("id")
               .replace("datafile", "variables"));

         // ignore "-----" option
         if (!$(datafileSelect).val()){
            $variablesSelect.html('');
            return;
         }

         $variablesSelect.html("");

         // Get datafile variables
         $.ajax({
            method : "POST",
            dataType : "json",
            url : "/load_datafile_variables",
            data : { 
               id : $(datafileSelect).val(),
               csrfmiddlewaretoken : $.cookie("csrftoken")
            }
         }).done(function(response){
            //load variables into multi-selectbox
            for (key in response) {
               $variablesSelect.append("<option value='" + key + "'>"
                  + response[key].name + " (" + response[key].dimensions
                  + "D)</option>");
            }
         });
      };

      function incrementFormsetCount(amount) {
         var counter = $("#id_computationdata_set-TOTAL_FORMS");
         counter.val(parseInt(counter.val()) + amount);
      }

      /**
       * Add a new DataFile formset.
       */
      function addDataFile() {

         // clone from existing new formset
         var formset = $(".datafile_formset").last();

         // find what set number we're on
         var setNo = formset.html().match(/set-(\d)+/)[1];
         setNo = parseInt(setNo);

         // clone formset with new set numbers
         var tmpFormset = $('<div></div>');
         tmpFormset.html(formset.html().replace(/set-(\d)+/g, "set-" + (setNo + 1)));

         // create new formset
         var newFormset = $("<div class='datafile_formset'></div>");
         newFormset.append(tmpFormset.find("p"));
         // empty variable selectbox
         newFormset.find("select[multiple]").html("");
         newFormset.append("<button class='red button remove_button'>"
               + "Remove</button>");

         // increment tally of formsets
         incrementFormsetCount(1);

         formset.after(newFormset);
      };

      $form.on("change", "select[id$=datafile]", function(e) {
         e.preventDefault();
         populateVariables(this);
      });

      $form.find("select[id$=datafile]").each(function(e) {
         populateVariables(this);
      });

      $form.find("#add_datafile").click(function(e){
         e.preventDefault();
         addDataFile();
      });

      $form.on("click", ".remove_button", function(e) {
         e.preventDefault();
         $(this).parent().remove();
         incrementFormsetCount(-1);
      });
   });

})(jQuery);
