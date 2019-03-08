
from operator import attrgetter

from sqlalchemy import Float, Integer
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql.expression import cast

from dallinger.nodes import Source, Agent
from dallinger.networks import Network
import random


# TODO: if we want to show different stories across networks, we have to make fancier changes 
class WarOfTheGhostsSource(Source):
    """A Source that reads in a random story from a file and transmits it."""

    __mapper_args__ = {
        "polymorphic_identity": "war_of_the_ghosts_source"
    }

    def _contents(self):
        """Define the contents of new Infos.

        transmit() -> _what() -> create_information() -> _contents().
        """
        stories = [
            "ghosts.md",
            "cricket.md",
            "moochi.md",
            "outwit.md",
            "raid.md",
            "species.md",
            "tennis.md",
            "vagabond.md"
        ]
        story = random.choice(stories)
        with open("static/stimuli/{}".format(story), "r") as f:
            return f.read()

class RogersAgent(Agent):
    """The Rogers Agent."""

    __mapper_args__ = {"polymorphic_identity": "rogers_agent"}

    @hybrid_property
    def generation(self):
        """Convert property2 to genertion."""
        return int(self.property2)

    @generation.setter
    def generation(self, generation):
        """Make generation settable."""
        self.property2 = repr(generation)

    @generation.expression
    def generation(self):
        """Make generation queryable."""
        return cast(self.property2, Integer)


class MultiChain(Network):
    """A multi-chained network
    """

    __mapper_args__ = {"polymorphic_identity": "multi-chain"}

    def __init__(self, generations, generation_size, initial_source):
        """Endow the network with some persistent properties."""
        self.property1 = repr(generations)
        self.property2 = repr(generation_size)
        self.property3 = repr(initial_source)
        if self.initial_source:
            self.max_size = generations * generation_size + 1
        else:
            self.max_size = generations * generation_size

    @property
    def generations(self):
        """The length of the network: the number of generations."""
        return int(self.property1)

    @property
    def generation_size(self):
        """The width of the network: the size of a single generation."""
        return int(self.property2)

    @property
    def initial_source(self):
        """The source that seeds the first generation."""
        return self.property3.lower() != 'false'

    def add_node(self, node):
        """Link to the agent from a parent based on the parent's fitness"""
        num_agents = len(self.nodes(type=Agent))
        curr_generation = int((num_agents - 1) / float(self.generation_size))
        node.generation = curr_generation

        parents = []
        if curr_generation == 0 and self.initial_source:
            parents = [self._select_oldest_source()]
        else:
            parents = self._get_nodes_from_generation(
                node_type=type(node),
                generation=curr_generation - 1
            )

        if len(parents) > 0:

            for p in parents:
                p.connect(whom=node)
                p.transmit(to_whom=node)

    def _select_oldest_source(self):
        return min(self.nodes(type=Source), key=attrgetter('creation_time'))

    def _get_nodes_from_generation(self, node_type, generation):
        prev_agents = node_type.query\
            .filter_by(failed=False,
                       network_id=self.id,
                       generation=(generation))\
            .all()

        return prev_agents
