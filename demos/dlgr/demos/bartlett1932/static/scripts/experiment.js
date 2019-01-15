var my_node_id;

// Consent to the experiment.
$(document).ready(function() {

  $("#finish-reading").click(function() {
    $("#stimulus").hide();
    $("#response-form").show();
    $("#submit-response").removeClass('disabled');
    $("#submit-response").html('Submit');
  });

  $("#submit-response").click(function() {
    $("#submit-response").addClass('disabled');
    $("#submit-response").html('Sending...');

    var response = $("#reproduction").val();

    $("#reproduction").val("");

    dallinger.createInfo(my_node_id, {
      contents: response,
      info_type: 'Info'
    }).done(function (resp) {
      create_agent();
    });
  });

});

// Create the agent.
var create_agent = function() {
  $('#finish-reading').prop('disabled', true);
  dallinger.createAgent()
    .done(function (resp) {
      $('#finish-reading').prop('disabled', false);
      my_node_id = resp.node.id;
      get_info();
    })
    .fail(function (rejection) {
      // A 403 is our signal that it's time to go to the questionnaire
      if (rejection.status === 403) {
        dallinger.allowExit();
        dallinger.goToPage('questionnaire');
      } else {
        dallinger.error(rejection);
      }
    });
};

// var get_info = function() {
//   // Get info for node
//   dallinger.getReceivedInfos(my_node_id)
//     .done(function (resp) {
//       var story = resp.infos[0].contents;
//       var storyHTML = markdown.toHTML(story);
//       $("#story").html(storyHTML);
//       $("#stimulus").show();
//       $("#response-form").hide();
//       $("#finish-reading").show();
//     })
//     .fail(function (rejection) {
//       console.log(rejection);
//       $('body').html(rejection.html);
//     });
// };

var get_info = function() {
  // Get info for node
  dallinger.getReceivedInfos(my_node_id)
    .done(function (resp) {
      var story = resp.infos;
      var story_one = story[0].contents;
      var story_two = story[1].contents;
      console.log(resp);

      var storyHTML = markdown.toHTML(story_one);
      $("#story").html(storyHTML); // Story #1
      $("#stimulus_one").show();
      $("#response-form").hide();

      var storyHTML = markdown.toHTML(story_two);
      $("#story").html(storyHTML); // Story #2
      $("#stimulus_two").show();
      $("#response-form").hide();

      $("#finish-reading").show();
    })
    .fail(function (rejection) {
      console.log(rejection);
      $('body').html(rejection.html);
    });
};