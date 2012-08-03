# Copyright 2011 Alex Zvoleff
#
# This file is part of the PyABM agent-based modeling toolkit.
# 
# PyABM is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
# 
# PyABM is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along with
# PyABM.  If not, see <http://www.gnu.org/licenses/>.
#
# Contact Alex Zvoleff in the Department of Geography at San Diego State 
# University with any comments or questions. See the README.txt file for 
# contact information.

"""
Contains classes to assist in making agents. 'Person' agents, for example, 
would be subclasses of the Agent class, while Household, Neighborhood, and 
Region agents would be represented as subclasses of the Agent_set object (as 
households, neighborhoods, and regions all contain lower-level agents).

Alex Zvoleff, azvoleff@mail.sdsu.edu
"""

from PyABM import rcParams

class Agent(object):
    "Superclass for agent objects."
    def __init__(self, world, ID, initial_agent=False):
        # Keep a reference to the agent's world so that ID generators and other 
        # world properties can be easily referenced
        self._world = world

        # self._ID is unique ID number used to track each person agent.
        self._ID = ID

        # self._initial_agent is set to "True" for agents that were used to 
        # initialize the model.
        self._initial_agent = initial_agent

        # _parent_agent stores the parent agent if this agent is a member of an 
        # Agent_set class instance. For example, for a person agent that is a 
        # member of a household, the _parent_agent for that person agent would 
        # be that household.
        self._parent_agent = None

    def get_ID(self):
        return self._ID

    def set_parent_agent(self, agent):
        self._parent_agent = agent

    def get_parent_agent(self):
        return self._parent_agent

class Agent_set(Agent):
    """Superclass for agents that contain a "set" of agents from a lower 
    hierarchical  level."""
    def __init__(self, world, ID, initial_agent):
        Agent.__init__(self, world, ID, initial_agent)

        # _members stores agent set members in a dictionary keyed by ID
        self._members = {}

    def get_agents(self):
        return self._members.values()

    def get_agent(self, ID):
        "Returns an agent given the agent's ID"
        return self._members[ID]

    def is_member(self, ID):
        "Returns true if agent is a member of this set"
        return self._members.has_key(ID)

    def add_agent(self, agent):
        "Adds a new agent to the set."
        if self._members.has_key(agent.get_ID()):
            raise KeyError("agent %s is already a member of agent set %s"%(agent.get_ID(), self._ID))
        self._members[agent.get_ID()] = agent
        # Set the agent's _parent_agent to reflect the parent of this Agent_set 
        # instance (self)
        agent.set_parent_agent(self)

    def remove_agent(self, agent):
        "Removes agent from agent set."
        try:
            self._members.pop(agent.get_ID())
        except KeyError:
            raise KeyError("agent %s is not a member of agent set %s"%(agent.get_ID(), self.get_ID()))
        # Reset the agent's _parent_agent
        assert agent.get_parent_agent().get_ID() == self.get_ID(), "Removing agent from an Agent_set it does not appear to be assigned to."
        agent.set_parent_agent(None)

    def iter_agents(self):
        for agent in self.get_agents():
            yield agent

    def num_members(self):
        return len(self._members)

class Agent_Store(object):
    """
    Agent_Store is a class used to store agents who have left for various 
    reasongs (such as migration) or are in school. It allows triggering their 
    return or graduation during a later timestep of the model.
    """
    def __init__(self):
        # self._releases is a dictionary, keyed by timestep, that stores the 
        # time at which each agent will be released back to their original 
        # parent agent (when they return from school, or from their temporary 
        # migration, for example.
        self._releases = {}
        self._parent_dict = {}
        self._stored_agents = []

    def add_agent(self, agent, release_time):
        """
        Adds a new agent to the agent store. Also remove the agent from it's 
        parent Agent_set instance.
        """
        if self._releases.has_key(release_time):
            self._releases[release_time].append(agent)
        else:
            self._releases[release_time] = [agent]
        self._parent_dict[agent] = agent.get_parent_agent()
        # Store a reference to the agent store with the class instance that is 
        # being stored, for easy retrieval later
        agent._store_list.append(self)
        agent.get_parent_agent().remove_agent(agent)
        # Keep a list of the agents stored in this agent_set instance in 
        # _stored_agents so that we can easily check whether or now an agent is 
        # in an agent store instance, without having to iterate through all the 
        # release times.
        self._stored_agents.append(agent)

    def release_agents(self, time):
        # TODO: Make this more general, so it works for households or person 
        # agents. Right now it only works for persons since to get the 
        # neighborhood ID for tracking we have to call .get_parent_agent twice.
        released_agents = []
        released_agents_dict = {}
        if self._releases.has_key(time):
            for agent in self._releases[time]:
                parent_agent = self._parent_dict.pop(agent)
                parent_agent.add_agent(agent)
                agent._store_list.remove(self)
                self._stored_agents.remove(agent)
                neighborhood = parent_agent.get_parent_agent()
                if not released_agents_dict.has_key(neighborhood.get_ID()):
                    released_agents_dict[neighborhood.get_ID()] = 0
                released_agents_dict[neighborhood.get_ID()] += 1
                released_agents.append(agent)
            # Remove the now unused releases list for this timestep.
            self._releases.pop(time)
        return released_agents_dict, released_agents

    def in_store(self, agent):
        if agent in self._stored_agents: return True
        else: return False

    def remove_agent(self, agent):
        """
        Remove an agent from the store without releasing it to its original 
        location (useful for handling agents who die while away from home).
        """
        self._releases[agent._return_timestep].remove(agent)
        self._parent_dict.pop(agent)
        self._stored_agents.remove(agent)
        agent._store_list.remove(self)

    def __str__(self):
        return 'Agent_Store(%s)'%self._releases
