var selected_seg_id = 0;
var selected_seg_name = "";

jQuery(document).ready(function($) {
      $(".delete-segment").click(function(e){
          $("#modal-box-delete-segment").css("display","block");
          selected_seg_name = $(this).parent().parent().children("#column-seg-name").text();
          // alert(selected_seg_name);
          selected_seg_id = $(this).parent().parent().children("#column-seg-id").text();
          // alert(selected_seg_id);
          $("#modal-box-delete-text").html('Are you Sure you want to <span class="strong-danger">DELETE</span> segment <strong>"'+selected_seg_name+'"</strong> from this Tour ?');
          action_attr = $("#form-delete-segment").attr("action");
          // alert(action_attr);
          $("#form-delete-segment").attr("action",action_attr+selected_seg_id);
          // alert($("#form-delete-segment").attr("action"));
          e.stopPropagation();
    });
});

jQuery(document).ready(function($) {
        $("#btn-cancel-delete-segment").click(function(e) {
          $("#modal-box-delete-segment").css("display","none");
          e.stopPropagation();
    });
});

jQuery(document).ready(function($) {
    var alert_visible = localStorage.getItem('alert_visible');
    var has_notification = localStorage.getItem('has_notification');
    // $(".sc-feed").css("margin-top","60px");
    if (alert_visible == 'YES' & has_notification == 'YES')
    {
        $("#notification-div").css("display","block");
        $(".sc-feed").css("margin-top","0px")
    }
});

jQuery(document).ready(function($) {
    $("#notification-button").click(function() {
        localStorage.setItem('alert_visible','NO');
    });
});

jQuery(document).ready(function($) {
    $("#logout-option").click(function() {
      localStorage.setItem('alert_visible','YES');
  });
});

jQuery(document).ready(function($) {
    $(".btn-strava-login").click(function() {
      localStorage.setItem('alert_visible','YES');
  });
});

// Routine for clickable-row
jQuery(document).ready(function($) {
        $(".clickable-row").click(function() {
            window.location = $(this).data("href");
    });
});

jQuery(document).ready(function($) {
        $(".cancel-button").click(function() {
            window.location = $(this).data("href");
    });
});

jQuery(document).ready(function($) {
        $(".confirm-button").click(function() {
            window.location = $(this).data("href");
    });
});

jQuery(document).ready(function($) {
        $("#inactivate-league").click(function(e) {
            e.stopPropagation();
    });
});

jQuery(document).ready(function($) {
        $(".action-in-tour-row").click(function(e) {
            e.stopPropagation();
    });
});

jQuery(document).ready(function($) {
    $('.page-alert .close').click(function(e) {
        e.preventDefault();
        $(this).closest('.page-alert').slideUp();
        $(".sc-feed").css("margin-top","60px")
    });
});

jQuery(document).ready(function($) {
        $(".collapsable-table-row").click(function() {
            next = $(this).next();
            next.toggleClass('tr-uncollapsed');
    });
});

// Routines on fly alert box (this is not the modal box)
jQuery(document).ready(function($) {
        $(".closebtn").click(function() {
            next = $(this).parent.css("display","none");
    });
});




// Routines for dropdown selection
// Routine for dropdown selection at Tour Segment Details

jQuery(document).ready(function($) {
      $("#feed-filter-select-id li a").click(function(){
        // alert("WoW");
        $(this).parents(".dropdown").find('.btn').html($(this).text() + '  <span class="glyphicon glyphicon-menu-down" aria-hidden="true"></span>');
        $(this).parents(".dropdown").find('.btn').val($(this).data('value'));
        selected_index = $(this).closest('li').index();
        if (selected_index == 1)
        {
          $("#modal-box-search-segment").css("display","block");
        }
    });
});

jQuery(document).ready(function($) {
      $("#btn_dismiss_league_prev").click(function(e){
        $("#modal-box").css("display","block");
    });
});

jQuery(document).ready(function($) {
      $("#cancel-dont-join-button").click(function(e){
        $("#modal-box").css("display","none");
    });
});

jQuery(document).ready(function($) {
      $("#btn_react_athlete_league_prev").click(function(e){
        $("#modal-box").css("display","block");
    });
});

jQuery(document).ready(function($) {
      $("#btn_inact_athlete_league_prev").click(function(e){
        $("#modal-box").css("display","block");
    });
});

jQuery(document).ready(function($) {
      $("#btn_inact_league_prev").click(function(e){
        $("#modal-box").css("display","block");
    });
});

jQuery(document).ready(function($) {
      $("#btn_inact_self_league_prev").click(function(e){
        $("#modal-box").css("display","block");
    });
});

jQuery(document).ready(function($) {
      $("#feed-filter-view-tours-feed-id li a").click(function(){

        selected_index = $(this).closest('li').index();
        if (selected_index == 0) {
            $(".tours-feed-block-active").css("display","block")
            $(".tours-feed-block-to-be-started").css("display","none")
            $(".tours-feed-block-finished").css("display","none")
        } else if (selected_index == 1) {
            $(".tours-feed-block-active").css("display","none")
            $(".tours-feed-block-to-be-started").css("display","block")
            $(".tours-feed-block-finished").css("display","none")
        } else if (selected_index == 2) {
            $(".tours-feed-block-active").css("display","none")
            $(".tours-feed-block-to-be-started").css("display","none")
            $(".tours-feed-block-finished").css("display","block")
        }

        $(this).parents(".dropdown").find('.btn').html($(this).text() + '  <span class="glyphicon glyphicon-menu-down" aria-hidden="true"></span>');
        $(this).parents(".dropdown").find('.btn').val($(this).data('value'));
    });
});

jQuery(document).ready(function($) {
      $("#summary-active-id").click(function(){
          $(".tours-feed-block-active").css("display","block")
          $(".tours-feed-block-to-be-started").css("display","none")
          $(".tours-feed-block-finished").css("display","none")

          text = $("#feed-filter-view-tours-feed-id").find("li").eq(0).find("a").html();
          $("#feed-filter-view-btn").html(text+'  <span class="glyphicon glyphicon-menu-down" aria-hidden="true"></span>');
    });
});

jQuery(document).ready(function($) {
      $("#summary-tobestarted-id").click(function(){
          $(".tours-feed-block-active").css("display","none")
          $(".tours-feed-block-to-be-started").css("display","block")
          $(".tours-feed-block-finished").css("display","none")

          text = $("#feed-filter-view-tours-feed-id").find("li").eq(1).find("a").html();
          $("#feed-filter-view-btn").html(text+'  <span class="glyphicon glyphicon-menu-down" aria-hidden="true"></span>');
    });
});

jQuery(document).ready(function($) {
      $("#summary-finished-id").click(function(){
          $(".tours-feed-block-active").css("display","none")
          $(".tours-feed-block-to-be-started").css("display","none")
          $(".tours-feed-block-finished").css("display","block")

          text = $("#feed-filter-view-tours-feed-id").find("li").eq(2).find("a").html();
          $("#feed-filter-view-btn").html(text+'  <span class="glyphicon glyphicon-menu-down" aria-hidden="true"></span>');
    });
});


jQuery(document).ready(function($) {
      $("#feed-filter-view-leagues-feed-id li a").click(function(){

        selected_index = $(this).closest('li').index();
        if (selected_index == 0)
        {
          $(".leagues-feed-block-current").css("display","block")
          $(".leagues-feed-block-invited").css("display","none")
          $(".leagues-feed-block-former").css("display","none")
        } else if (selected_index == 1) {
          $(".leagues-feed-block-current").css("display","none")
          $(".leagues-feed-block-invited").css("display","block")
          $(".leagues-feed-block-former").css("display","none")
        } else if (selected_index == 2) {
          $(".leagues-feed-block-current").css("display","none")
          $(".leagues-feed-block-invited").css("display","none")
          $(".leagues-feed-block-former").css("display","block")
        }

        $(this).parents(".dropdown").find('.btn').html($(this).text() + '  <span class="glyphicon glyphicon-menu-down" aria-hidden="true"></span>');
        $(this).parents(".dropdown").find('.btn').val($(this).data('value'));
    });
});

jQuery(document).ready(function($) {
      $("#summary-current-id").click(function(){
          $(".leagues-feed-block-current").css("display","block");
          $(".leagues-feed-block-invited").css("display","none");
          $(".leagues-feed-block-former").css("display","none");

          text = $("#feed-filter-view-leagues-feed-id").find("li").eq(0).find("a").html();
          $("#feed-filter-view-btn").html(text+'  <span class="glyphicon glyphicon-menu-down" aria-hidden="true"></span>');
    });
});

jQuery(document).ready(function($) {
      $("#summary-pending-id").click(function(){
          $(".leagues-feed-block-current").css("display","none");
          $(".leagues-feed-block-invited").css("display","block");
          $(".leagues-feed-block-former").css("display","none");

          text = $("#feed-filter-view-leagues-feed-id").find("li").eq(1).find("a").html();
          $("#feed-filter-view-btn").html(text+'  <span class="glyphicon glyphicon-menu-down" aria-hidden="true"></span>');
    });
});

jQuery(document).ready(function($) {
      $("#summary-former-id").click(function(){
          $(".leagues-feed-block-current").css("display","none");
          $(".leagues-feed-block-invited").css("display","none");
          $(".leagues-feed-block-former").css("display","block");

          text = $("#feed-filter-view-leagues-feed-id").find("li").eq(2).find("a").html();
          $("#feed-filter-view-btn").html(text+'  <span class="glyphicon glyphicon-menu-down" aria-hidden="true"></span>');
    });
});

jQuery(document).ready(function($) {
      $("#feed-filter-view-id li a").click(function(){
        $(this).parents(".dropdown").find('.btn').html($(this).text() + '  <span class="glyphicon glyphicon-menu-down" aria-hidden="true"></span>');
        $(this).parents(".dropdown").find('.btn').val($(this).data('value'));
    });
});

// The code bellow is from Double List Box
// https://bootsnipp.com/snippets/z8d4r

jQuery(document).ready(function($) {

    // Variables which add the + and - glyhicons to the texts itens in the list
    var glyph_remove = '<span class="glyphicon glyphicon-minus pull-left  glyph-move-to-unselected" title="Remove Selected"></span>';
    var glyph_add  = '<span class="glyphicon glyphicon-plus  pull-right glyph-move-to-selected " title="Add Selected"></span>';

    $(".dual-list.top-list-selected .list-group").sortable({
        stop: function( event, ui ) {
            updateSelectedOptions();
        }
    });

    // When click a list-group-item in a list-group, change the class of it to active
    $(document).on('touchstart click', '.list-group .list-group-item', function (e) {
        $(this).toggleClass('active');
        e.preventDefault();
    });

    // When click the - signal in the list on the right side
    $(document).on('touchstart click', '.glyph-move-to-unselected', function (e) {

        // Prevent to call the default click function of this event which
        // will be (? the item in the list ?)
        e.preventDefault();

        // get the parent list item
        actives = $(this).parent();

        // remove the span with the - glyphicon
        $(this).parent().find("span").remove();

        // make a clone of the span with the + glyphicon and put it at the end of the list item
        $(glyph_add).clone().appendTo(actives);

        // make a clone
        // take out the class of a selected item of it
        actives.clone().appendTo('.top-list-unselected ul').removeClass("active");

        // remove the selected item from the right list
        actives.remove();

        // sort the right list
        sortUnorderedList("list-selected");

        // Update the selected itens based on the
        updateSelectedOptions();
    });


    $(document).on('touchstart click', '.glyph-move-to-selected', function (e) {
        e.preventDefault();

        actives = $(this).parent();
        $(this).parent().find("span").remove();
        $(glyph_remove).clone().appendTo(actives);
        actives.clone().appendTo('.top-list-selected ul').removeClass("active");
        actives.remove();

        updateSelectedOptions();
    });


    $('.move-right, .move-left').click(function () {
        var $button = $(this), actives = '';
        if ($button.hasClass('move-left')) {
            actives = $('.top-list-unselected ul li.active');
            actives.find(".glyph-move-to-selected").remove();
            actives.append($(glyph_remove).clone());
            actives.clone().appendTo('.top-list-selected ul').removeClass("active");
            actives.remove();

        } else if ($button.hasClass('move-right')) {
            actives = $('.top-list-selected ul li.active');
            actives.find(".glyph-move-to-unselected").remove();
            actives.append($(glyph_add).clone());
            actives.clone().appendTo('.top-list-unselected ul').removeClass("active");
            actives.remove();
        }

        updateSelectedOptions();
    });


    function updateSelectedOptions() {
        // from the hidden reference list which contains all the elements which are selected
        // remove all the elements tagged with option (it means remove all)
        $('#dual-list-options').find('option').remove();

        // for each element in the selected list
        $('.top-list-selected ul li').each(function(idx, opt) {

            // add a line in the list like that "<option value="5" selected="selected">Item Text</option>
            $('#dual-list-options').append($("<option></option>")
                .attr("value", $(opt).data("value"))
                .text( $(opt).text())
                .prop("selected", "selected")
            );
        });
    }


    $('.dual-list .selector').click(function () {
        var $checkBox = $(this);
        if (!$checkBox.hasClass('selected')) {
            $checkBox.addClass('selected').closest('.well').find('ul li:not(.active)').addClass('active');
            $checkBox.children('i').removeClass('glyphicon-unchecked').addClass('glyphicon-check');
        } else {
            $checkBox.removeClass('selected').closest('.well').find('ul li.active').removeClass('active');
            $checkBox.children('i').removeClass('glyphicon-check').addClass('glyphicon-unchecked');
        }
    });


    $('[name="SearchDualList"]').keyup(function (e) {
        var code = e.keyCode || e.which;
        if (code == '9') return;
        if (code == '27') $(this).val(null);
        var $rows = $(this).closest('.dual-list').find('.list-group li');
        var val = $.trim($(this).val()).replace(/ +/g, ' ').toLowerCase();
        $rows.show().filter(function () {
            var text = $(this).text().replace(/\s+/g, ' ').toLowerCase();
            return !~text.indexOf(val);
        }).hide();
    });


    $(".glyphicon-search").on("click", function() {
        $(this).next("input").focus();
    });


    function sortUnorderedList(ul, sortDescending) {
        $("#" + ul + " li").sort(sort_li).appendTo("#" + ul);

        function sort_li(a, b){
            return ($(b).data('value')) < ($(a).data('value')) ? 1 : -1;
        }
    }


    $("#list-selected li").append(glyph_remove);
    $("#list-unselected li").append(glyph_add);

});
