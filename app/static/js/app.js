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
});