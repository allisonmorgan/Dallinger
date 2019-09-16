var my_node_id,curr_generation
// Consent to the experiment.
$(document).ready(function() {

  /*
  $("#task-completed").click(function() {
    $("#intermediary_task").hide();
    $("#response-form").show();
    $("#submit-response").removeClass('disabled');
    $("#submit-response").html('Submit');
  });*/

  $("#submit-response").click(function() {
    $("#submit-response").addClass('disabled');
    $("#submit-response").html('Sending...');

    var response = $("#reproduction").val();

    $("#reproduction").val("");

    var contents = {
      response: response,
      generation: curr_generation,
      participant_id: dallinger.identity.participantId
    }

    dallinger.createInfo(my_node_id, {
      contents: JSON.stringify(contents),
      info_type: 'Info'
    }).done(function (resp) {
      create_agent();
    });
  });

});

function update_story_html(story_html,curr_story,total_stories){
  if (total_stories==1){
    var story_str = 'following'
  } else{
    if (curr_story==1){
      var story_str = 'first'
    } else if (curr_story==2){
      var story_str = 'second'
    } else if (curr_story==3){
      var story_str = 'third'
    } else {
      var story_str = 'fourth'
    }
  }
  if (curr_generation==0 && curr_story>1){
    var h1_addition = ' (even if the same as the previous text):'
    var curr_story_text = story_html[0].contents
  } else{
    var h1_addition = ':'
    var curr_story_text = story_html[curr_story-1].contents
  }
  $('#header-text').html('Read the ' +story_str+ ' text' + h1_addition)

  storyHTML = curr_story_text

  if (curr_generation==0){
    var storyHTML = markdown.toHTML(curr_story_text)
  } else{
    var storyHTML = markdown.toHTML(JSON.parse(curr_story_text)['response'])
  }
  $("#story").html(storyHTML);
  $("p").addClass("preventcopy");
  $("#stimulus").show();
  $("#finish-reading").show();
  $('#header-text').show()
  setTimeout(function(){
    $("#finish-reading").removeClass('disabled')
    $("#finish-reading").html("I'm done reading the story");
    if (curr_story==total_stories){
      $("#finish-reading").click(function(){
        $("#stimulus").hide();
        $("#response-form").show();
        $("#submit-response").removeClass('disabled');
        $("#submit-response").html('Submit');
      })
    } else {
      $("#finish-reading").click(function(){
        $("#finish-reading").html("Please read for at least 30 seconds");
        $(window).scrollTop(0);
        $("#story").html('&lt;&lt; loading &gt;&gt;')
        $("#finish-reading").addClass('disabled')
        $("#finish-reading").hide()
        $('#header-text').hide()
        $('#finish-reading').off('click');
        setTimeout(function(){
          update_story_html(story_html,curr_story+1,total_stories)
        },500)
      })
    }
  },30000)
}

// Create the agent.
var create_agent = function() {
  $('#finish-reading').prop('disabled', true);
  dallinger.createAgent()
    .done(function (resp) {
      $('#finish-reading').prop('disabled', false);
      a = resp;
      my_node_id = resp.node.id;
      curr_generation = parseInt(resp.node.property3);
    
      dallinger.getExperimentProperty('generation_size')
        .done(function (propertiesResp) {
          generation_size = propertiesResp.generation_size
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
      var stories = resp.infos;
      //var num_stories = stories.length
      //console.log(num_stories)

      $("#finish-reading").addClass('disabled')
      update_story_html(stories, 1, generation_size)

      $("#response-form").hide();

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
