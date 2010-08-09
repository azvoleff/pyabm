# Copyright 2009 Alex Zvoleff
#
# This file is part of the ChitwanABM agent-based model.
# 
# ChitwanABM is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
# 
# ChitwanABM is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along with
# ChitwanABM.  If not, see <http://www.gnu.org/licenses/>.
#
# Contact Alex Zvoleff in the Department of Geography at San Diego State 
# University with any comments or questions. See the README.txt file for 
# contact information.

"""
Contains the classes for Person, Household, Neighborhood, and Region agents. 
Person agents are subclasses of the Agent class, while Household, Neighborhood, 
and Region agents are all subclasses of the Agent_set object.

Alex Zvoleff, azvoleff@mail.sdsu.edu
"""

import numpy as np

from ChitwanABM import rcParams, IDGenerator, boolean_choice, random_state
from ChitwanABM.statistical_models import calc_hazard_birth, calc_hazard_death, calc_hazard_migration, calc_hazard_marriage, calc_first_birth_time, calc_hh_area, calc_des_num_children

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

        # If not defined at birth, self._des_num_children will be defined at 
        # marriage in the "marry" function.
        self._des_num_children = None

        if self._sex=="female":
            self._last_birth_time = None

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
        # Also assign first birth timing and desired number of children to the 
        # female (if not already defined, which it will be for initial agents).
        if self.get_sex()=="female":
            female=self
        else:
            female=spouse
        female._first_birth_timing = calc_first_birth_time()
        if female._des_num_children == None:
            female._des_num_children = calc_des_num_children()


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
        self._last_birth_time = time
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

    def fw_usage(self):
        # Load coefficients from rcParams
        intercept = rcParams['fw_demand.coef.intercept']
        coef_hh_size = rcParams['fw_demand.coef.hh_size']
        coef_ethnic = rcParams['fw_demand.coef.ethnic']
        coef_own_nw_stove = rcParams['fw_demand.coef.own_nw_stove']

        hh_size = self.num_members()
        fw_usage = intercept + hh_size * coef_hh_size
        # Convert daily fw_usage to monthly
        fw_usage = fw_usage * 30
        return fw_usage

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

    def add_agent(self, agent):
        """
        Subclass the Agent_set.add_agent function in order to account for LULC 
        change with new household addition.
        """
        Agent_set.add_agent(self, agent)
        hh_area = calc_hh_area()
        self._land_agveg -= hh_area
        self._land_privbldg += hh_area

    def avg_years_nonfamily_services(self):
        "Average number of years non-family services have been available."
        return self._avg_years_nonfamily_services

    def elec_available(self):
        "Boolean for whether neighborhood has electricity."
        return self._elec_available

    def get_num_psn(self):
        "Returns the number of people in the neighborhood."
        num_psn = 0
        for household in self.iter_agents():
            num_psn += household.num_members()
        return num_psn

    def get_num_marriages(self):
        "Returns the total number of marriages in this neighborhood."
        num_marr = 0
        spouses = []
        for household in self.iter_agents():
            for person in household.iter_agents():
                if person.is_married() and (person.get_spouse() not in spouses):
                    num_marr += 1
                    spouses.append(person)
        return num_marr

    def get_hh_sizes(self):
        hh_sizes = {}
        for household in self.iter_agents():
            hh_sizes[household.get_ID()] = household.num_members()
        return hh_sizes

    def __str__(self):
        return "Neighborhood(NID: %s. %s household(s))" %(self.get_ID(), self.num_members())

def Agent_Store(Agent_set):
    """
    Agent_Store is a type of agent set used to store agents who have either left 
    Chitwan to return later (migration) or are in school. It allows triggering 
    their return or graduation during a later timestep of the model.
    """
    def __init__(self, world, ID=None, initial_agent=False):
        Agent_set.__init__(self, world, ID, initial_agent)
        # self._releases is a dictionary, keyed by timestep, that stores the 
        # time at which each agent will be released back to their original 
        # parent agent (when they return from school, or from their temporary 
        # migration, for example.
        self._releases = {}

    def add_agent(self, agent):
        """
        Subclass the Agent_set.add_agent function in order to account for LULC 
        change with new household addition.
        """
        Agent_set.add_agent(self, agent)

    def release_agents(self, time):
        pass

class Region(Agent_set):
    """Represents a set of neighborhoods sharing a spatial area (and therefore 
    land use data), and demographic characteristics."""
    def __init__(self, world, ID=None, initial_agent=False):
        Agent_set.__init__(self, world, ID, initial_agent)

        # TODO: Here demographic variables could be setup specific for each 
        # population.

    def __repr__(self):
        #TODO: Finish this
        return "__repr__ UNDEFINED"

    def __str__(self):
        return "Region(RID: %s, %s neighborhood(s), %s household(s), %s person(s))" %(self.get_ID(), len(self._members), self.num_households(), self.num_persons())

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
        min_birth_interval = rcParams['birth.minimum_interval']
        births = {}
        for household in self.iter_households():
            for person in household.iter_agents():
                # Check that person is a married female
                if (person.get_sex() == 'female') and person.is_married():
                    # Check that person didn't already give birth more recently 
                    # than their minimum birth interval
                    if (person._last_birth_time == None) or (time -
                            person._last_birth_time) > min_birth_interval/12:
                        # Check that the person does not already have greater 
                        # than their desired family size. Note that 
                        # des_num_children=-1 means no preference.
                        if (person._des_num_children > len(person._children)
                                or person._des_num_children==-1):
                            if random_state.rand() < calc_hazard_birth(person):
                                # Agent gives birth. First find the father 
                                # (assumed to be the spouse of the person 
                                # giving birth).
                                father = person.get_spouse()
                                # Now have the mother give birth, and add the 
                                # new person to the mother's household.
                                household.add_agent(person.give_birth(time,
                                    father=father))
                                if rcParams['feedback.birth.nonagveg']:
                                    neighborhood = household.get_parent_agent()
                                    neighborhood._land_nonagveg -= rcParams['feedback.birth.nonagveg.area']
                                    neighborhood._land_other += rcParams['feedback.birth.nonagveg.area']
                                # Track the total number of births for each 
                                # timestep by neighborhood.
                                if not births.has_key(neighborhood.get_ID()):
                                    births[neighborhood.get_ID()] = 0
                                births[neighborhood.get_ID()] += 1
        return births
                        
    def deaths(self, time):
        """Runs through the population and kills agents probabilistically based 
        on their age and the hazard.death for this population"""
        deaths = {}
        for household in self.iter_households():
            for person in household.iter_agents():
                if random_state.rand() < calc_hazard_death(person):
                    # Agent dies.
                    if person.is_married():
                        person.divorce()
                    household.remove_agent(person)
                    neighborhood = household.get_parent_agent()
                    if not deaths.has_key(neighborhood.get_ID()):
                        deaths[neighborhood.get_ID()] = 0
                    deaths[neighborhood.get_ID()] += 1
        return deaths
                        
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
        # As a VERY crude model of in-migration, append to the list additional 
        # agents, according to a parameter specifying the proportion of persons 
        # who marry in-migrants.
        num_new_females = np.floor(rcParams['prob.marry.inmigrant'] * len(eligible_females))
        for n in xrange(1, num_new_females):
            # Choose the age randomly from the ages of the eligible males
            agent_age = eligible_females[np.random.randint(len(eligible_females))].get_age()
            eligible_females.append(self._world.new_person(time, sex="female", age=agent_age))

        num_new_males = np.floor(rcParams['prob.marry.inmigrant'] * len(eligible_males))
        for n in xrange(1, num_new_females):
            # Choose the age randomly from the ages of the eligible males
            agent_age = eligible_males[np.random.randint(len(eligible_males))].get_age()
            eligible_males.append(self._world.new_person(time, sex="male", age=agent_age))

        # Now pair up the eligible agents. Any extra males/females will not 
        # marry this timestep.
        marriages = {}
        for male, female in zip(eligible_males, eligible_females):
             # First marry the agents.
            male.marry(female)
            moveout_prob = rcParams['prob.marriage.moveout']
            # Create a new household according to the moveout probability
            if boolean_choice(moveout_prob) or male.get_parent_agent()==None:
                # Create a new household. male.get_parent_agent() is equal to 
                # None for in-migrants, as they are not a member of a 
                # household.
                # TODO: need to figure out how the new household has 
                # characteristics assigned to it.
                new_home = self._world.new_household()
                neighborhoods = [] # Possible neighborhoods for the new_home
                for person in [male, female]:
                    old_household = person.get_parent_agent() # this person's old household
                    if old_household == None:
                        # old_household will equal none for in-migrants, as 
                        # they are not tracked in the model until after this 
                        # timestep. This means they also will not have a 
                        # neighborhood.
                        continue
                    old_household.remove_agent(person)
                    new_home.add_agent(person)
                    neighborhoods.append(old_household.get_parent_agent()) # this persons old neighborhood
                # For now, randomly assign the new household to the male or 
                # females neighborhood. Or randomly pick new neighborhood if 
                # both members of the couple are in-migrants.
                if len(neighborhoods)>0:
                    neighborhood = neighborhoods[np.random.randint(len(neighborhoods))]
                else:
                    poss_neighborhoods = self.get_agents()
                    neighborhood = poss_neighborhoods[np.random.randint( \
                        len(poss_neighborhoods))]
                neighborhood.add_agent(new_home)
            else:
                # Otherwise they stay in the male's household. So have the 
                # female move in.
                old_household = female.get_parent_agent() # this person's old household
                # old_household will equal none for in-migrants, as they are 
                # not tracked in the model until after this timestep.
                if old_household != None: old_household.remove_agent(female)
                male_household = male.get_parent_agent()
                male_household.add_agent(female)
                neighborhood = male.get_parent_agent().get_parent_agent()
            if not marriages.has_key(neighborhood.get_ID()):
                marriages[neighborhood.get_ID()] = 0
            marriages[neighborhood.get_ID()] += 1
        return marriages

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
        """
        Runs through the population and makes agents probabilistically migrate
        based on their age and the hazard_marriage for this population.
        """
        # First handle out-migrations
        out_migr = {}
        for household in self.iter_households():
            for person in household.iter_agents():
                if random_state.rand() < calc_hazard_migration(person):
                    # Agent migrates.
                    neighborhood = household.get_parent_agent()
                    if not out_migr.has_key(neighborhood.get_ID()):
                        out_migr[neighborhood.get_ID()] = 0
                    out_migr[neighborhood.get_ID()] += 1

        in_migr = {}
        # Now handle in-migrations
        num_in_migr = int(np.random.normal(rcParams['migr.in.mean'],
            rcParams['migr.in.sd']))
        if num_in_migr < 0: num_in_migr = 0
        # TODO: Fix this in-migration code, or eliminate it in favor of 
        # in-migration through marriage.
        in_migr[1] = num_in_migr
        #if not in_migr.has_key(neighborhood.get_ID()):
        #    in_migr[neighborhood.get_ID()] = 0
        #in_migr[neighborhood.get_ID()] += 1
        return out_migr, in_migr

    def increment_age(self):
        """Adds one to the age of each agent. The units of age are dependent on 
        the units of the input rc parameters."""
        for person in self.iter_persons():
            person._age += timestep

    def get_neighborhood_fw_usage(self):
        fw_usage = {}
        for neighborhood in self.iter_agents():
            fw_usage[neighborhood.get_ID()] = 0
            for household in neighborhood.iter_agents():
                fw_usage[neighborhood.get_ID()] += household.fw_usage()
        return {'fw_usage': fw_usage}

    def get_neighborhood_landuse(self):
        landuse = {}
        for neighborhood in self.iter_agents():
            landuse[neighborhood.get_ID()] = {}
            landuse[neighborhood.get_ID()]['agveg'] = neighborhood._land_agveg
            landuse[neighborhood.get_ID()]['nonagveg'] = neighborhood._land_nonagveg
            landuse[neighborhood.get_ID()]['privbldg'] = neighborhood._land_privbldg
            landuse[neighborhood.get_ID()]['pubbldg'] = neighborhood._land_pubbldg
            landuse[neighborhood.get_ID()]['other'] = neighborhood._land_other
        return landuse

    def get_neighborhood_pop_stats(self):
        """
        Used each timestep to return a dictionary of neighborhood-level 
        population statistics.
        """
        pop_stats = {'num_psn':{}, 'num_hs':{}, 'num_marr':{}}
        for neighborhood in self.iter_agents():
            if not pop_stats.has_key(neighborhood.get_ID()):
                pop_stats[neighborhood.get_ID()] = {}
            pop_stats['num_psn'][neighborhood.get_ID()] = neighborhood.get_num_psn()
            pop_stats['num_hs'][neighborhood.get_ID()] = neighborhood.num_members()
            pop_stats['num_marr'][neighborhood.get_ID()] = neighborhood.get_num_marriages()
        return pop_stats

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
