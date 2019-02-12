var my_node_id;

// Consent to the experiment.
$(document).ready(function() {

  $("#finish-reading_one").click(function() {
    $("#stimulus_one").hide();
    $("#stimulus_two").show();
  });

  $("#finish-reading_two").click(function() {
    $("#stimulus_two").hide();
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


var get_info = function() {
  // Get info for node
  dallinger.getReceivedInfos(my_node_id)
    .done(function (resp) {
      var story = resp.infos;
      var story_one = story[0].contents;
      if(story.length > 1) {
        var story_two = story[1].contents; //TODO need to test this --- make sure right number of Infos being received
      } else{
        var story_two = story[0].contents
      }

      var storyHTML = markdown.toHTML(story_one);
      $("#story_one").html(storyHTML); // Story #1
      $("#stimulus_one").show();
      $("#finish-reading_one").show();

      var storyHTML = markdown.toHTML(story_two);
      $("#story_two").html(storyHTML); // Story #2
      $("#stimulus_two").hide();
      $("#finish-reading_two").show();

      $("#response-form").hide();

    })
    .fail(function (rejection) {
      console.log(rejection);
      $('body').html(rejection.html);
    });
};
