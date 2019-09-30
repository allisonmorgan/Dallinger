var my_node_id,curr_generation, replication, read_multiple_versions

var running_total_pay = 0;
var button_timeout = 15000 // 20000//20000 // milliseconds before participant can move on after reading story
var loading_timeout = 500 // miliseconds next story is loaded (including the timeout smooths the loading process) 

// Consent to the experiment.
$(document).ready(function() {

    //-e git://github.com/Dallinger/Dallinger.git@rest-to-sns#egg=dallinger

  /*
  $("#task-completed").click(function() {
    $("#intermediary_task").hide();
    $("#response-form").show();
    $("#submit-response").removeClass('disabled');
    $("#submit-response").html('Submit');
  });*/

  $("#submit-response").click(function() {
    $("#reproduction").prop('disabled', true);
    $("#submit-response").addClass('disabled');
    $("#submit-response").html('Sending...');

    var response = $("#reproduction").val();

    $("#reproduction").val("");

    var contents = {
      response: response,
      generation: curr_generation,
      replication: replication,
      participant_id: dallinger.identity.participantId,
      read_multiple_versions: read_multiple_versions,
      generation_size:generation_size
    }
    dallinger.createInfo(my_node_id, {
      contents: JSON.stringify(contents),
      info_type: 'Info'
    }).done(function (resp) {
      create_agent();
    });
  });

});

function get_word_count(input_str){
  return input_str.split(' ').length
}

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
  } else if (curr_story==1){
    var h1_addition = ':'
    var curr_story_text = story_html[0].contents
  } else{
    var h1_addition = ' (even if similar to the previous text):'
    var curr_story_text = story_html[curr_story-1].contents
  }
  $('#header-text').html('Read the ' +story_str+ ' text' + h1_addition)


  var storyHTML = curr_story_text

  if (curr_generation==0){
    storyHTML = markdown.toHTML(curr_story_text)
  } else{
    storyHTML = markdown.toHTML(JSON.parse(curr_story_text)['response'])
  }

  $('#trial_info_1').html('Story page: <span>' + String(curr_story) + ' of ' + String(total_stories) + '</span>')
  var word_count = get_word_count(storyHTML)
  var curr_pay = roundTo(0.002*word_count,2)
  running_total_pay = running_total_pay+curr_pay
  $('#trial_info_2').html('Potential bonus earned from reading this story: <span>$' + curr_pay.toFixed(2) + '</span>')
  $('#trial_info_3').html('Total potential bonus: <span>$' + running_total_pay.toFixed(2) + '</span>')

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
        $("#finish-reading").addClass('disabled')
        $('#trial_by_trial').css('margin-bottom','30px')
        $('#trial_info_1').html('Response page: <span>1 of 1</span>')
        $('#trial_info_2').css('display','none')
        $("#stimulus").hide();
        $("#response-form").show();
        $("#submit-response").removeClass('disabled');
        $("#submit-response").html('Submit');
      })
    } else {
      $("#finish-reading").click(function(){
        $("#finish-reading").addClass('disabled')
        $("#finish-reading").html("Please read for at least 20 seconds");
        $(window).scrollTop(0);
        $("#story").html('<b>Loading story ...</b>')
        $("#finish-reading").hide()
        $('#header-text').hide()
        $('#finish-reading').off('click');
        setTimeout(function(){
          update_story_html(story_html,curr_story+1,total_stories)
        },loading_timeout)
      })
    }
  },button_timeout)
}

// Create the agent.
var create_agent = function() {
  $('#finish-reading').prop('disabled', true);
  dallinger.createAgent()
    .done(function (resp) {
      $('#finish-reading').prop('disabled', false);
      //a = resp;
      my_node_id = resp.node.id;
      curr_generation = parseInt(resp.node.property3);
      replication = parseInt(resp.node.property5);
      //console.log(replication)
    
      dallinger.getExperimentProperty('generation_size')
        .done(function (propertiesResp) {
          generation_size = propertiesResp.generation_size
          dallinger.getExperimentProperty('read_multiple_versions')
          .done(function(propertiesResp){

            read_multiple_versions = propertiesResp.read_multiple_versions
            if (curr_generation==0 && read_multiple_versions==0){
              var num_stories_to_read = 1
            } else{
              var num_stories_to_read = generation_size
            }      


            if (num_stories_to_read==1){
              $('#response-header').html('Using the information you read in the text, reproduce the passage to the best of your ability.')
            } else if (num_stories_to_read==2){
              $('#response-header').html("<p id ='more-info'>These stories were two different MTurk workers' attempts to reproduce the same passage.</p><p>Using the information you read in the two texts, please reproduce this passage to the best of your ability.</p>")
            } else if (num_stories_to_read==3){
              $('#response-header').html("<p id ='more-info'>These stories were three different MTurk workers'' attempts to reproduce the same passage.</p><p>Using the information you read in the three texts, please reproduce this passage to the best of your ability.</p>")
            } else{
              $('#response-header').html("<p id ='more-info'>These stories were four different MTurk workers'' attempts to reproduce the same passage.</p><p>Using the information you read in the four texts, please reproduce this passage to the best of your ability.</p>")
            }
            if (curr_generation==0){
              $('#more-info').css('display','none')
            }
            get_info(num_stories_to_read);
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

var get_info = function(num_of_stories) {
  // Get info for node
  dallinger.getReceivedInfos(my_node_id)
    .done(function (resp) {
      var stories = resp.infos;
      //var num_stories = stories.length
      //console.log(num_stories)

      $("#finish-reading").addClass('disabled')
      update_story_html(stories, 1, num_of_stories)

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

function roundTo(n, digits) {
  if (digits === undefined) {
    digits = 0;
  }

  var multiplicator = Math.pow(10, digits);
  n = parseFloat((n * multiplicator).toFixed(11));
  var test =(Math.round(n) / multiplicator);
  return +(test.toFixed(digits));
}