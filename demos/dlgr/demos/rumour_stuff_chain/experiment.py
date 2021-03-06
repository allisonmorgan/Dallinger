"""Bartlett's transmission chain experiment from Remembering (1932)."""

import logging

from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from models import RogersAgent, MultiChain
from dallinger.bots import BotBase
from dallinger.experiment import Experiment


logger = logging.getLogger(__file__)


class Bartlett1932(Experiment):
    """Define the structure of the experiment."""

    def __init__(self, session=None):
        """Call the same function in the super (see experiments.py in dallinger).

        A few properties are then overwritten.

        Finally, setup() is called.
        """
        super(Bartlett1932, self).__init__(session)
        from . import models  # Import at runtime to avoid SQLAlchemy warnings
        self.models = models
        self.experiment_repeats = 1
        self.initial_recruitment_size = 1
        self.generation_size = 1
        self.generations = 3
        if session:
            self.setup()

    def setup(self):
        """Setup the networks.

        Setup only does stuff if there are no networks, this is so it only
        runs once at the start of the experiment. It first calls the same
        function in the super (see experiments.py in dallinger). Then it adds a
        source to each network.
        """
        if not self.networks():
            super(Bartlett1932, self).setup()
            for net in self.networks():
                self.models.WarOfTheGhostsSource(network=net)

    def create_network(self):
        """Create a new network."""
        return MultiChain(
            generations=self.generations,
            generation_size=self.generation_size,
            initial_source=True
        )

    def create_node(self, network, participant):
        """Make a new node for participants."""
        return self.models.RogersAgent(network=network,participant=participant)

    #def add_node_to_network(self, node, network):
    #    """Add participant's node to a network."""
    #    network.add_node(node)
    #    node.receive()

        #environment = network.nodes(type=Environment)[0]
        #environment.connect(whom=node)
        #environment.transmit(to_whom=node)

        #if node.generation > 0:
        #    agent_model = self.models.RogersAgent
        #    prev_agents = agent_model.query\
        #        .filter_by(failed=False,
        #                   network_id=network.id,
        #                   generation=node.generation - 1)\
        #        .all()
        #    parent = random.choice(prev_agents)
        #    parent.connect(whom=node) # TODO: DiscreteGenerational network also connects nodes. why doesn't this line create a second vector in the database?
        #    parent.transmit(what=Meme, to_whom=node)

        #node.receive()



    def add_node_to_network(self, node, network):
        """Add node to the chain and receive transmissions."""
        network.add_node(node)
        parents = node.neighbors(direction="from")
        if len(parents):
            parent = parents[0]
            parent.transmit()
        node.receive()

    def recruit(self):
        """Recruit one participant at a time until all networks are full."""
        if self.networks(full=False):
            self.recruiter.recruit(n=1)
        else:
            self.recruiter.close_recruitment()


class Bot(BotBase):
    """Bot tasks for experiment participation"""

    def participate(self):
        """Finish reading and send text"""
        try:
            logger.info("Entering participate method")
            ready = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'finish-reading')))
            stimulus = self.driver.find_element_by_id('stimulus')
            story = stimulus.find_element_by_id('story')
            story_text = story.text
            logger.info("Stimulus text:")
            logger.info(story_text)
            ready.click()
            submit = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'submit-response')))
            textarea = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'reproduction')))
            textarea.clear()
            text = self.transform_text(story_text)
            logger.info("Transformed text:")
            logger.info(text)
            textarea.send_keys(text)
            submit.click()
            return True
        except TimeoutException:
            return False

    def transform_text(self, text):
        """Experimenter decides how to simulate participant response"""
        return "Some transformation...and %s" % text
