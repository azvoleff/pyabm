"""
Part of Chitwan Valley agent-based model.

Class for person, household, neighborhood, and region agents.

Alex Zvoleff, azvoleff@mail.sdsu.edu
"""

import numpy as np

from ChitwanABM import rcParams, IDGenerator, boolean_choice, random_state
from ChitwanABM.statistical_models import calc_hazard_birth, calc_hazard_death, calc_hazard_migration, calc_hazard_marriage

if rcParams['model.use_psyco'] == True:
    import psyco
    psyco.full()

timestep = rcParams['model.timestep']

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

class Person(Agent):
    "Represents a single person agent"
    def __init__(self, world, birthdate, PID=None, mother=None, father=None,
            age=0, sex=None, initial_agent=False):
        Agent.__init__(self, world, PID, initial_agent)

        # birthdate is the timestep of the birth of the agent. It is used to 
        # calculate the age of the agent. Agents have a birthdate of 0 if they 
        # were BORN in the first timestep of the model.  If they were used to 
        # initialize the model their birthdates will be negative.
        self._birthdate = birthdate

        # deathdate is used for tracking agent deaths in the results, mainly 
        # for debugging.
        self._deathdate = None

        # self._initial_agent is set to "True" for agents that were used to 
        # initialize the model.
        self._initial_agent = initial_agent

        # self._age is used as a convenience to avoid the need to calculate the 
        # agent's age from self._birthdate each time it is needed. It is         
        # important to remember though that all agent's ages must be 
        # incremented with each model timestep, and are expressed in months.
        # The age starts at 0 (it is zero for the entire first timestep of the 
        # model).
        self._age = age

        # Also need to store information on the agent's parents. For agents 
        # used to initialize the model both parent fields are set to "None"
        if father == None:
            self._father = None
        else:
            self._father = father

        if mother == None:
            self._mother = None
        else:
            self._mother = mother

        if sex==None:
            # Person agents are randomly assigned a sex
            if boolean_choice():
                self._sex = 'female'
            else:
                self._sex = 'male'
        elif sex in ['male', 'female']:
            self._sex = sex
        else:
            raise ValueError("%s is not a valid gender"%(sex))

        self._spouse = None

        self._children = []

    def get_sex(self):
        return self._sex

    def get_age(self):
        return self._age

    def get_spouse(self):
        return self._spouse

    def marry(self, spouse):
        "Marries this agent to another Person instance."
        self._spouse = spouse
        spouse._spouse = self

    def divorce(self):
        spouse = self._spouse
        spouse._spouse = None
        self._spouse = None

    def give_birth(self, time, father):
        "Agent gives birth. New agent inherits characterists of parents."
        assert self.get_sex() == 'female', "Men can't give birth"
        assert self.get_spouse().get_ID() == father.get_ID(), "All births must be in marriages"
        assert self.get_ID() != father.get_ID(), "No immaculate conception (agent: %s)"%(self.get_ID())
        baby = self._world.new_person(birthdate=time, mother=self, father=father)
        for parent in [self, father]:
            parent._children.append(baby)
        return baby

    def is_married(self):
        "Returns a boolean indicating if person is married or not."
        if self._spouse == None:
            return False
        else:
            return True

    def __str__(self):
        return "Person(PID: %s. %s household(s))" %(self.get_ID(), self.num_members())

class Household(Agent_set):
    "Represents a single household agent"
    def __init__(self, world, ID=None, initial_agent=False):
        Agent_set.__init__(self, world, ID, initial_agent)
        self._any_non_wood_fuel = boolean_choice(.93) # From DS0002$BAE15
        self._own_house_plot = boolean_choice(.829)  # From DS0002$BAA43
        self._own_land = boolean_choice(.61) # From Axinn, Ghimire (2007)
        self._rented_out_land = boolean_choice(.11) # From Axinn, Ghimire (2007)

    def any_non_wood_fuel(self):
        "Boolean for whether household uses any non-wood fuel"
        return self._any_non_wood_fuel

    def own_house_plot(self):
        "Boolean for whether household owns the plot of land on which it resides"
        return self._own_house_plot

    def own_any_land(self):
        "Boolean for whether household owns any land"
        return self._own_land

    def rented_out_land(self):
        "Boolean for whether household rented out any of its land"
        return self._rented_out_land

    def __str__(self):
        return "Household(HID: %s. %s household(s))" %(self.get_ID(), self.num_members())

class Neighborhood(Agent_set):
    "Represents a single neighborhood agent"
    def __init__(self, world, ID=None, initial_agent=False):
        Agent_set.__init__(self, world, ID, initial_agent)
        self._avg_years_nonfamily_services = None
        self._elec_available = None
        self._land_agveg = None
        self._land_nonagveg = None
        self._land_privbldg = None
        self._land_pubbldg = None
        self._land_other = None

    def avg_years_nonfamily_services(self):
        "Average number of years non-family services have been available."
        return self._avg_years_nonfamily_services

    def elec_available(self):
        "Boolean for whether neighborhood has electricity."
        return self._elec_available

    def __str__(self):
        return "Neighborhood(NID: %s. %s household(s))" %(self.get_ID(), self.num_members())

class Region(Agent_set):
    """Represents a set of neighborhoods sharing a spatial area (and therefore 
    land use data), and demographic characteristics."""
    def __init__(self, world, ID=None, initial_agent=False):
        Agent_set.__init__(self, world, ID, initial_agent)

        # Now setup the demographic variables for this population, based on the 
        # values given in the model rc file
        self._hazard_birth = rcParams['hazard.birth']
        self._hazard_death = rcParams['hazard.death']
        self._hazard_marriage = rcParams['hazard.marriage']

    def __repr__(self):
        #TODO: Finish this
        return "__repr__ UNDEFINED"

    def __str__(self):
        return "Region(RID: %s. %s neighborhood(s), %s household(s), %s person(s))" %(self.get_ID(), len(self._members), self.num_households(), self.num_persons())

    def iter_households(self):
        "Returns an iterator over all the households in the region"
        for neighborhood in self.iter_agents():
            for household in neighborhood.iter_agents():
                yield household

    def iter_persons(self):
        "Returns an iterator over all the persons in the region"
        for household in self.iter_households():
            for person in household.iter_agents():
                yield person

    def births(self, time):
        """Runs through the population and agents give birth probabilistically 
        based on their sex, age and the hazard_birth for this population"""
        # TODO: This should take account of the last time the agent gave birth 
        # and adjust the hazard accordingly.
        num_births = 0
        for household in self.iter_households():
            for person in household.iter_agents():
                if (person.get_sex() == 'female') and person.is_married():
                    if random_state.rand() < calc_hazard_birth(person):
                        num_births += 1
                        # Agent gives birth. First find the father (assumed to 
                        # be the spouse of the person giving birth).
                        father = person.get_spouse()
                        # Now have the mother give birth, and add the 
                        # new person to the mother's household.
                        household.add_agent(person.give_birth(time,
                            father=father))
        return num_births
                        
    def deaths(self, time):
        """Runs through the population and kills agents probabilistically based 
        on their age and the hazard_death for this population"""
        num_deaths = 0
        for household in self.iter_households():
            for person in household.iter_agents():
                if random_state.rand() < calc_hazard_death(person):
                    num_deaths += 1
                    # Agent dies.
                    if person.is_married():
                        # For divorce, can take advantage of the fact that the 
                        # spouse will ALWAYS reside in the same household.
                        spouse = person.get_spouse()
                        person.divorce()
                    household.remove_agent(person)
        return num_deaths
                        
    def marriages(self, time):
        """Runs through the population and marries agents probabilistically 
        based on their age and the hazard_marriage for this population"""
        # First find the eligible agents
        eligible_males = []
        eligible_females = []
        for household in self.iter_households():
            for person in household.iter_agents():
                if (not person.is_married()) and (random_state.rand() < calc_hazard_marriage(person)):
                    # Agent is eligible to marry.
                    if person.get_sex() == "male":
                        eligible_males.append(person)
                    else:
                        eligible_females.append(person)

        # Now pair up the eligible agents. Any extra males/females will not 
        # marry this timestep.
        num_marriages = 0
        for male, female in zip(eligible_males, eligible_females):
            num_marriages += 1
             # First marry the agents.
            male.marry(female)
            # Now create a new household
            # TODO: need to figure out how the new household has 
            # characteristics assigned to it.
            new_home = self._world.new_household()
            neighborhoods = [] # Possible neighborhoods for the new_home
            for person in [male, female]:
                old_household = person.get_parent_agent() # this person's old household
                old_household.remove_agent(person)
                new_home.add_agent(person)
                neighborhoods.append(old_household.get_parent_agent()) # this persons old neighborhood

            # For now, randomly assign the new household to the male or females 
            # neighborhood.
            if boolean_choice():
                neighborhoods[0].add_agent(new_home)
            else:
                neighborhoods[1].add_agent(new_home)
        return num_marriages

    def get_num_marriages(self):
        "Returns the total number of marriages in this region."
        num_marr = 0
        spouses = []
        for person in self.iter_persons():
            if person.is_married() and (person.get_spouse() not in spouses):
                    num_marr += 1
                    spouses.append(person)
        return num_marr

    def migrations(self, time):
        """Runs through the population and marries agents probabilistically 
        based on their age and the hazard_marriage for this population"""
        num_migrations = 0
        for household in self.iter_households():
            for person in household.iter_agents():
                if random_state.rand() < calc_hazard_migration(person):
                    num_migrations += 1
                    # Agent migrates.
                    # TODO: write code to handle migrations
        return num_migrations

    def increment_age(self):
        """Adds one to the age of each agent. The units of age are dependent on 
        the units of the input rc parameters."""
        for person in self.iter_persons():
            person._age += timestep

    def update_landuse(self, time):
        """Using the attributes of the neighborhoods in the region, update the 
        landuse proportions using OLS"""
        landuse = {'agveg':None, 'nonagveg':None, 'privgldg':None, 
                'pubbldg':None, 'other':None}
        for neighborhood in self.iter_agents:
            landuse['agveg'] += neighborhood._land_agveg
            landuse['nonagveg'] += neighborhood._land_nonagveg
            landuse['privbldg'] += neighborhood._land_privbldg
            landuse['pubbldg'] += neighborhood._land_pubbldg
            landuse['other'] += neighborhood._land_other
        return landuse

    def num_persons(self):
        "Returns the number of persons in the population."
        total = 0
        for household in self.iter_households():
            total += household.num_members()
        return total

    def num_households(self):
        total = 0
        for neighborhood in self.iter_agents():
            total += len(neighborhood.get_agents())
        return total

    def num_neighborhoods(self):
        return len(self._members.values())

class World():
    """The world class generates new agents, while tracking ID numbers to 
    ensure that they are always unique across each agent type. It also contains 
    a dictionary with all the regions in the model."""
    def __init__(self):
        # _members stores member regions in a dictionary keyed by RID
        self._members = {}

        # These IDGenerator instances generate unique ID numbers that are never 
        # reused, and always unique (once used an ID number cannot be 
        # reassigned to another agent). All instances of the Person class, for  
        # example, will have a unique ID number generated by the PIDGen 
        # IDGenerator instance.
        self._PIDGen = IDGenerator()
        self._HIDGen = IDGenerator()
        self._NIDGen = IDGenerator()
        self._RIDGen = IDGenerator()

    def new_person(self, birthdate, PID=None, mother=None, father=None, age=0,
            sex=None, initial_agent=False):
        "Returns a new person agent."
        if PID == None:
            PID = self._PIDGen.next()
        else:
            # Update the generator so the PID will not be reused
            self._PIDGen.use_ID(PID)
        return Person(self, birthdate, PID, mother, father, age, sex, initial_agent)

    def new_household(self, HID=None, initial_agent=False):
        "Returns a new household agent."
        if HID == None:
            HID = self._HIDGen.next()
        else:
            # Update the generator so the HID will not be reused
            self._HIDGen.use_ID(HID)
        return Household(self, HID, initial_agent)

    def new_neighborhood(self, NID=None, initial_agent=False):
        "Returns a new neighborhood agent."
        if NID == None:
            NID = self._NIDGen.next()
        else:
            # Update the generator so the NID will not be reused
            self._NIDGen.use_ID(NID)
        return Neighborhood(self, NID, initial_agent)

    def new_region(self, RID=None, initial_agent=False):
        "Returns a new region agent, and adds it to the world member list."
        if RID == None:
            RID = self._RIDGen.next()
        else:
            # Update the generator so the RID will not be reused
            self._RIDGen.use_ID(RID)
        region = Region(self, RID, initial_agent)
        self._members[region.get_ID()] = region
        return region

    def get_regions(self):
        return self._members.values()

    def iter_regions(self):
        "Convenience function for iteration over all regions in the world."
        for region in self._members.values():
            yield region

    def iter_persons(self):
        "Convenience function used for things like incrementing agent ages."
        for region in self.iter_regions():
            for person in region.iter_persons():
                yield person
