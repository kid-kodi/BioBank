$(function() {

    $('.chkAllBtn').click(function() {
        var isChecked = $(this).prop("checked");
        $('table tr:has(td)').find('input[type="checkbox"]').prop('checked', isChecked);
    });

    $('table tr:has(td)').find('input[type="checkbox"]').click(function() {
        var isChecked = $(this).prop("checked");
        var isHeaderChecked = $(".chkAllBtn").prop("checked");
        if (isChecked == false && isHeaderChecked)
            $(".chkAllBtn").prop('checked', isChecked);
        else {
            $('table tr:has(td)').find('input[type="checkbox"]').each(function() {
                if ($(this).prop("checked") == false)
                    isChecked = false;
            });
            $(".chkAllBtn").prop('checked', isChecked);
        }
    });

    var onDataPrint = function (argument) {
      var items = [];
      $('input[name=items]:checked').map(function() {
          items.push($(this).val());
          console.log( items );
      });


      $.ajax({
          url: "/sample/print",
          type: "POST",
          data: JSON.stringify({"items":items}),
          contentType: "application/json; charset=utf-8",
          success: function(data) {
            console.log(data);
            console.log(data);
            var samples = data.samples;
            $('#printableArea').html('')
            for (i = 0; i < samples.length; i++) {
                $('#printableArea').append( addTemplateToList(samples[ i ]) );
            }
            printDiv();
          }
      });

      return false;
    };

    var addTemplateToList = function( data ){
        html = String()
        + '<div class="card-print">'
            +    '<div>' + data.bio_code + '</div>'
            +    '<div>' + data.patient_code + '</div>'
            +    '<div>' + data.code + '</div>'
        + '</div>'

        return html;
    };

    $("#accordian a").click(function() {
        var link = $(this);
        var closest_ul = link.closest("ul");
        var parallel_active_links = closest_ul.find(".active")
        var closest_li = link.closest("li");
        var link_status = closest_li.hasClass("active");
        var count = 0;

        closest_ul.find("ul").slideUp(function() {
                if (++count == closest_ul.find("ul").length)
                        parallel_active_links.removeClass("active");
        });

        if (!link_status) {
                closest_li.children("ul").slideDown();
                closest_li.addClass("active");
        }
    });

    var printDiv = function() {
         var divName = 'printableArea';
         var printContents = document.getElementById(divName).innerHTML;
         var originalContents = document.body.innerHTML;

         document.body.innerHTML = printContents;

         window.print();

         document.body.innerHTML = originalContents;
    };

    $( ".datepicker" ).datepicker( $.datepicker.regional[ "fr" ] );

    $('body').on('click', '.printBtn', onDataPrint);

});