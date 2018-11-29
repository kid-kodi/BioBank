$(function() {

    $('#addSampleBtn').on('click', function(){
        var target = $('#list');

        var oldrow = target.find('.item:last');
        var row = oldrow.clone(true, true);

        console.log(row.find(":input")[0]);
        var elem_id = row.find(":input")[0].id;
        var elem_num = parseInt(elem_id.replace(/.*-(\d{1,4})-.*/m, '$1')) + 1;
        row.attr('data-id', elem_num);
        row.find(":input").each(function() {
            console.log(this);
            var id = $(this).attr('id').replace('-' + (elem_num - 1) + '-', '-' + (elem_num) + '-');
            $(this).attr('name', id).attr('id', id).val('').removeAttr("checked");
        });
        oldrow.after(row);

        return false;
    });

    $('.removeSampleBtn').on('click', function(){
        var target = $('#list');
        if(target.find('.item').length > 1) {
            var thisRow = $(this).closest('.item');
            thisRow.remove();
        }
        return false;
    });

    var setProject = function( projects ) {
      $('#project').find('option').remove();
      // Add new items
      $.each(projects, function(key, val) {
        option_item = '<option value="' + val.id + '">' + val.title + '</option>'
        $('#project').append(option_item);
      });
      $('#project').append('<option value="0">Aucuns</option>');
    };

    // Cascading programming
    $('#customer').change(function() {
      var _URL_ = '/api/v1.0/customers',
          customer_id = $('#customer').val();
          value = $("#customer :selected").text();
          $('#scustomer').html( value );
      if (customer_id != 0) {
        _URL_ = '/api/v1.0/customers/' + customer_id + '/projects';
      }
      $.getJSON(
        _URL_,
        function(data) {
          setProject( data );
        }
      );
    });


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
    }

    var printDiv = function() {
         var divName = 'printableArea';
         var printContents = document.getElementById(divName).innerHTML;
         var originalContents = document.body.innerHTML;

         document.body.innerHTML = printContents;

         window.print();

         document.body.innerHTML = originalContents;
    };

    $('body').on('click', '.printBtn', onDataPrint);

    $( ".datepicker" ).datepicker( $.datepicker.regional[ "fr" ] );

});