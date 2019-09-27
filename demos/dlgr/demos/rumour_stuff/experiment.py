"""Bartlett's transmission chain experiment from Remembering (1932)."""

import logging
#import pysnooper
import ast
import random

from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from sqlalchemy import and_, func
from sqlalchemy.sql.expression import cast
from dallinger.bots import BotBase
from dallinger.config import get_config
from dallinger.networks import Chain
from dallinger.experiment import Experiment
from dallinger import db

logger = logging.getLogger(__file__)

# attention check not working (just changed to true)
# bonus calculation not working correctly ... I think these may be related


class Bartlett1932(Experiment):
    @property
    def public_properties(self):
        return {
        'generation_size':3, # the width of the networks
        'read_multiple_versions':0 # 0/1 for T/F of whether the initial generation should read multiple version of the same thing
        }

    """Define the structure of the experiment."""
    def __init__(self, session=None):
        """Call the same function in the super (see experiments.py in dallinger).

        A few properties are then overwritten.

        Finally, setup() is called.
        """
        super(Bartlett1932, self).__init__(session)
        from . import models  # Import at runtime to avoid SQLAlchemy warnings

        self.num_replications = 2
        self.models = models
        self.generation_size = self.public_properties['generation_size']
        self.initial_recruitment_size = self.num_replications*self.generation_size
        self.generations = 5
        self.num_experimental_networks_per_experiment = 1
        self.num_fixed_order_experimental_networks_per_experiment = 1
        self.bonus_amount=1 # 1 for activating the extra bonus, 0 for deactivating it
        self.max_bonus_amount=5
        self.read_multiple_versions = self.public_properties['read_multiple_versions']
        if session:
            self.setup()


    def configure(self):
        config = get_config()

    #@pysnooper.snoop(prefix = "@snoop SETUP: ")
    def setup(self):
        """Setup the networks"""

        """Create the networks if they don't already exist."""
        if not self.networks():
                
            # make an outer loop for number of replications
            #for replication_i in range(self.num_replications):
            #    for decision_index in range(self.num_fixed_order_experimental_networks_per_experiment,replication_i):
            #        network = self.create_network(role = 'experiment', decision_index = decision_index)
            #        print('NETWORK HERE:',network)
            #        self.models.WarOfTheGhostsSource(network=network)

            for replication_i in range(self.num_replications):
                for decision_i in range(self.num_fixed_order_experimental_networks_per_experiment):
                    network = self.create_network(role='experiment',decision_index=decision_i,replication=replication_i)
                    self.models.WarOfTheGhostsSource(network=network)

            self.session.commit()

    def create_node(self, network, participant):
        return self.models.Particle(network=network,participant=participant, replication=network.replication)

    def create_network(self, role, decision_index,replication):
        """Return a new network."""
        # add argument for replication to particle filter in models.py
        net = self.models.ParticleFilter(generations = self.generations, generation_size = self.generation_size,replication=replication)
        net.role = role
        net.decision_index = decision_index
        #net.replication = replication
        self.session.add(net)
        return net

    def add_node_to_network(self, node, network):
        """Add node to the chain and receive transmissions."""
        network.add_node(node)
        parents = node.neighbors(direction="from")
        #if len(parents):
        #    parent = parents[0]
        #    parent.transmit()
        node.receive()

    def get_submitted_text(self, participant):
        """The text a given participant submitted"""
        submitted_text = participant.nodes()[0].infos()[0].contents
        if submitted_text[0]=='{':
            submitted_dict = ast.literal_eval(submitted_text)
            submitted_text = submitted_dict['response']
        return submitted_text

    #@pysnooper.snoop()
    def get_read_text(self, participant):
        """The text that a given participant was shown to memorize"""
        node = participant.nodes()[0]
        node_length = len(node.all_incoming_vectors)
        contents_list = []
        for indexi in range(node_length):
            curr_incoming = node.all_incoming_vectors[indexi]
            curr_origin = curr_incoming.origin
            curr_text = curr_origin.infos()[0].contents
            if curr_text[0]=='{':
                curr_dict = ast.literal_eval(curr_text)
                curr_text = curr_dict['response']
            contents_list.append(curr_text)
        return contents_list

    #@pysnooper.snoop()
    def attention_check(self, participant):
        read_text = self.get_read_text(participant)
        num_read_text = len(read_text)
        total_performance = 0
        for readi in range(num_read_text):
            curr_performance = self.text_similarity(self.get_submitted_text(participant), read_text[readi])
            #print('SUBMITTED TEXT:', self.get_submitted_text(participant))
            #print('RECEIVED TEXT:', readi, read_text[readi])
            #print('TYPE OF TEXT:', type(self.get_submitted_text(participant)))
            total_performance += curr_performance
        average_performance = total_performance /  num_read_text
        #print("AVERAGE PERFORMANCE:",average_performance)  
        return ( 0.015 <= average_performance <= 0.8)
        

    def text_similarity(self, one, two):
        """Return a measure of the similarity between two texts"""
        try:
            from Levenshtein import ratio
            from Levenshtein import distance
        except ImportError:
            from difflib import SequenceMatcher
            ratio = lambda x, y: SequenceMatcher(None, x, y).ratio()
        #return (ratio(one, two)*len(one))/(2*len(two))
        return ratio(one, two)

    #@pysnooper.snoop()
    def bonus(self, participant):
        """The bonus to be awarded to the given participant.
        Return the value of the bonus to be paid to `participant`.
        """

        text_input=self.get_read_text(participant)
        total_performance = 0
        len_text = 0
        for storyi in range(len(text_input)):
            len_text += len(str(text_input[storyi]).split(' '))
            curr_performance = self.text_similarity(
            self.get_submitted_text(participant),
            text_input[storyi])
            total_performance += curr_performance
        average_performance = total_performance/len(text_input)
        if participant.nodes()[0].generation == 0 and self.read_multiple_versions==1:
            text_reward = (0.002 * len_text)*self.generation_size # read multiple versions of the same thing
        else:
            text_reward = (0.002 * len_text)
        payout = round(text_reward , 2)
        if average_performance <= 0.015:
            return min(round(payout/4,2),self.max_bonus_amount)
        else:
            return min(payout, self.max_bonus_amount)


    # #@pysnooper.snoop()
    def get_network_for_existing_participant(self, participant, participant_nodes):
        """Obtain a netwokr for a participant who has already been assigned to a condition by completeing earlier rounds"""

        # which networks has this participant already completed?
        networks_participated_in = [node.network_id for node in participant_nodes]
        
        # How many decisions has the particiapnt already made?
        completed_decisions = len(networks_participated_in)

        # When the participant has completed all networks in their condition, their experiment is over
        # returning None throws an error to the fronted which directs to questionnaire and completion
        if completed_decisions == self.num_experimental_networks_per_experiment:
            return None

        nfixed = self.num_fixed_order_experimental_networks_per_experiment

        # If the participant must still follow the fixed network order
        if completed_decisions < nfixed:
            # find the network that is next in the participant's schedule
            # match on completed decsions b/c decision_index counts from zero but completed_decisions count from one
            return self.models.Network.query.filter(self.models.Network.property4 == repr(completed_decisions)).filter_by(full = False).one()

        # If it is time to sample a network at random
        else:
            # find networks which match the participant's condition and werent' fixed order nets
            matched_condition_experimental_networks = self.models.Network.query.filter(cast(self.models.Network.property4, Integer) >= nfixed).filter_by(full = False).all()
            
            # subset further to networks not already participated in (because here decision index doesnt guide use)
            availible_options = [net for net in matched_condition_experimental_networks if net.id not in networks_participated_in]
            
            # choose randomly among this set
            chosen_network = random.choice(availible_options)

        return chosen_network

    #@pysnooper.snoop(prefix = "@snoop: ")
    def get_network_for_new_participant(self, participant):
        #key = "experiment.py >> get_network_for_new_participant ({}); ".format(participant.id)

        available_networks = self.models.ParticleFilter.query.filter_by(full = False).filter(self.models.ParticleFilter.property4 == repr(0)).all()

        #first_network = available_networks[0].property5
        #second_network = available_networks[1].property5


        #occupancy_counts = (
        #    db.session.query(
        #    func.count(self.models.Particle.participant_id.distinct()).label('count'), self.models.ParticleFilter.property5)
        #    .join(self.models.ParticleFilter)
        #    .join(self.models.Participant)
        #    .group_by(self.models.ParticleFilter.property5)  
        #    .filter_by(failed = False)
        #    .filter(self.models.ParticleFilter.property4 == repr(0))
        #     .filter(self.models.Participant.status == "approved")
        #).all()

        #second_thing = (
        #    db.session.query(
        #        func.count(self.models.Particle.participant_id.distinct()).label('count'), self.models.ParticleFilter.property5, self.models.Participant.status)
        #        .join(self.models.ParticleFilter)
        #        .group_by(self.models.ParticleFilter.property5, self.models.Participant.status)  
        #        .filter_by(failed = False)
        #        .filter(self.models.ParticleFilter.property4 == repr(0))
        #).all()

        #third_thing =   (
        #    db.session.query(
        #    func.count(self.models.Particle.participant_id.distinct()).label('count'), self.models.ParticleFilter.property5, self.models.Participant.status)
        #    .join(self.models.ParticleFilter)
        #    .join(self.models.Participant)
        #    .group_by(self.models.ParticleFilter.property5, self.models.Participant.status)  
        #    .filter_by(failed = False)
        #    .filter(self.models.ParticleFilter.property4 == repr(0))
        #).all()

        occupancy_counts = (
            db.session.query(
            func.count(self.models.Particle.participant_id.distinct()).label('count'), self.models.ParticleFilter.property5)
            .join(self.models.ParticleFilter)
            .join(self.models.Participant)
            .group_by(self.models.ParticleFilter.property5)  
            .filter_by(failed = False)
            .filter(self.models.ParticleFilter.property4 == repr(0))
             .filter(self.models.Participant.status.in_(["approved", "working", "submitted"]))
        ).all()

        if len(occupancy_counts)>=1:
            if len(occupancy_counts)==self.num_replications:
                min_val = 10000 # whole thing is hacky, but can make cleaner later
                min_val_list = []
                for replication_i in range(len(occupancy_counts)):
                    curr_val = occupancy_counts[replication_i][0]
                    if curr_val<min_val:
                        min_val_list = [int(occupancy_counts[replication_i][1])] # append with the replication int
                        min_val=curr_val
                    elif curr_val==min_val:
                        min_val_list.append(int(occupancy_counts[replication_i][1]))
            elif len(occupancy_counts)<self.num_replications: # in initial generation here,
                curr_generation_list = list(range(0,self.num_replications))
                for replication_i in range(len(occupancy_counts)):
                    curr_replication = int(occupancy_counts[replication_i][1])
                    curr_generation_list.remove(curr_replication)
                min_val_list = curr_generation_list
        else:
            min_val_list = list(range(0,self.num_replications))

        current_replication = random.choice(min_val_list)


        #random_choice_list = []
        #for replication_i in range(len(occupancy_counts)):
        #    curr_in_replication = occupancy_counts[replication_i][0]
        #    curr_remaining = num_allowed-curr_in_replication
        #    curr_list = [replication_i]*curr_remaining
        #    random_choice_list = random_choice_list+curr_list

        #print('OCCUPANCY COUNTS:',occupancy_counts)
        #print("RANDOM CHOICE LIST",random_choice_list)
        #print("RANDOM CHOICE",random.choice(random_choice_list))
        # nothing to stop this giving them both replication 0
        return available_networks[current_replication]

    #@pysnooper.snoop()
    def get_network_for_participant(self, participant):
        """Find a network for a participant."""
        key = "experiment.py >> get_network_for_participant ({}); ".format(participant.id)
        participant_nodes = participant.nodes()
        if not participant_nodes:
            chosen_network = self.get_network_for_new_participant(participant)
        else:
            chosen_network = self.get_network_for_existing_participant(participant, participant_nodes)

        if chosen_network is not None:
            self.log("Assigned to network: {}; Decsion Index: {};".format(chosen_network.id, chosen_network.decision_index), key)

        else:
            self.log("Requested a network but was assigned None.".format(len(participant_nodes)), key)

        return chosen_network

    # @pysnooper.snoop()
    def get_current_generation(self):
        network = self.models.ParticleFilter.query.first()
        return repr(int(network.property3))

    def rollover_generation(self):
        for network in self.models.ParticleFilter.query.all():
            network.current_generation = int(network.current_generation) + 1
        self.log("Rolled over all network to generation {}".format(network.current_generation), "experiment.py >> rollover_generation: ")

    # @pysnooper.snoop()
    def recruit(self):
        """Recruit one participant at a time until all networks are full."""
        if self.networks(full=False):
            current_generation = self.get_current_generation()

            completed_participant_ids = [p.id for p in self.models.Participant.query.filter_by(failed = False, status = "approved")]
            
            # particle.property3 = generation
            completed_nodes_this_generation = self.models.Particle.query.filter(
                                                                            self.models.Particle.property3 == current_generation, \
                                                                            self.models.Particle.participant_id.in_(completed_participant_ids)) \
                                                                        .count() 

            if completed_nodes_this_generation == self.generation_size*self.num_replications:
                self.rollover_generation()
                self.recruiter.recruit(n=self.generation_size*self.num_replications)

        else:
            self.recruiter.close_recruitment()
