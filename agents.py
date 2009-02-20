"""
Part of Chitwan Valley agent-based model.

Class for person, household, neighborhood, and region agents.

Alex Zvoleff, azvoleff@mail.sdsu.edu
"""

import numpy as np

from chitwanABM import rcParams, IDGenerator, boolean_choice
from chitwanABM.landuse import LandUse

#######################################################################3
#######################################################################3
#######################################################################3
#TODO: code these. It would simplify matters

class agent(object):
    "Superclass for agent objects"
    def __init__(self, birthdate, PID=None, mother_PID=None, father_PID=None,
            age=0, initial_agent=False):
        # self._PID is unique ID number used to track each person agent.
        if PID == None:
            self._ID = IDGen.next()
        else:
            PIDGen.use_ID(ID) # Update the generator so PID will not be reused
            self._ID = ID

        # self._initial_agent is set to "True" for agents that were used to 
        # initialize the model.
        self._initial_agent = initial_agent

    def get_ID(self):
        return self._ID

class agent_set(agent):
    def get_persons(self):
        return self._members.values()

    def add_person(self, person):
        "Adds a new person to the household, either from birth or marriage"
        if self._members.has_key(person.get_PID()):
            raise KeyError("person %s is already a member of household %s"%(person.get_PID(), self._HID))
        self._members[person.get_PID()] = person

    def remove_person(self, person):
        """Removes a person from household, either from death, migration, or 
        marriage to a member of another household."""
        try:
            self._members.pop(person.get_PID())
        except KeyError:
            raise KeyError("person %s is not a member of household %s"%(person.get_PID(), self._HID))

#######################################################################3
#######################################################################3
#######################################################################3

PIDGen = IDGenerator()

class Person(object):
    "Represents a single person agent"
    def __init__(self, birthdate, PID=None, mother_PID=None, father_PID=None,
            age=0, initial_agent=False):
        # self._PID is unique ID number used to track each person agent.
        if PID == None:
            self._PID = PIDGen.next()
        else:
            PIDGen.use_ID(PID) # Update the generator so PID will not be reused
            self._PID = PID

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

        # self._age is used as a convenience to avoid the need to calculate 
        # the agent's age from self._birthdate each time it is needed. It is         
        # important to remember though that all agent's ages must be 
        # incremented with each model timestep. The age starts at 0 (it is 
        # zero for the entire first timestep of the model).
        self._age = age

        # Also need to store information on the agent's parents. For agents 
        # used to initialize the model both parent fields are set to "None"
        if father_PID == None:
            self._father_PID = None
        else:
            self._father_PID = father.get_PID()

        if mother_PID == None:
            self._mother_PID = None
        else:
            self._mother_PID = mother.get_PID()

        # Person agents are randomly assigned a sex
        if boolean_choice(.5):
            self._sex = 'female'
        else:
            self._sex = 'male'

        self._spousePID = None

        self._children = []

    def get_PID(self):
        return self._PID

    def get_sex(self):
        return self._sex

    def get_spouse_PID(self):
        return self._spousePID

    def marry(self, other):
        "Marries this agent to another Person instance."
        self._spousePID = other.get_PID()
        other._spousePID = self.get_PID()

    def give_birth(self, time, dad):
        "Agent gives birth. New agent inherits characterists of parents."
        assert self.get_sex() == 'female', "Men can't give birth"
        assert self.get_PID() != dad.get_PID(), "No immaculate conception"
        assert self.get_spouse_PID() == dad.get_PID(), "In Chitwan, all births are in marriages"
        baby = Person(birthdate=time, mother=self, father=dad)
        for parent in [self, dad]:
            parent._children.append(baby)
        return baby

    def is_married(self):
        "Returns a boolean indicating if person is married or not."
        if self._spousePID == None:
            return False
        else:
            return True

HIDGen = IDGenerator()

class Household(object):
    "Represents a single household agent"
    def __init__(self):
        self._HID = HIDGen.next()
        self._anyNonWoodFuel = boolean_choice()
        self._OwnHousePlot = boolean_choice()
        self._OwnLand = boolean_choice()
        self._RentedOutLand = boolean_choice()

        # _members stores household members in a dictionary keyed by PID
        self._members = {}

    def get_HID(self):
        "Returns the ID of this household"
        return self._HID

    def get_persons(self):
        return self._members.values()

    def add_person(self, person):
        "Adds a new person to the household, either from birth or marriage"
        if self._members.has_key(person.get_PID()):
            raise KeyError("person %s is already a member of household %s"%(person.get_PID(), self._HID))
        self._members[person.get_PID()] = person

    def remove_person(self, person):
        """Removes a person from household, either from death, migration, or 
        marriage to a member of another household."""
        try:
            self._members.pop(person.get_PID())
        except KeyError:
            raise KeyError("person %s is not a member of household %s"%(person.get_PID(), self._HID))

    def num_members(self):
        return len(self._members)

    def any_non_wood_fuel(self):
        "Boolean for whether household uses any non-wood fuel"
        return self._anyNonWoodFuel

    def own_house_plot(self):
        "Boolean for whether household owns the plot of land on which it resides"
        return self._OwnHousePlot

    def own_any_land(self):
        "Boolean for whether household owns any land"
        return self._OwnLand

    def rented_out_land(self):
        "Boolean for whether household rented out any of its land"
        return self._RentedOutLand

NIDGen = IDGenerator()

class Neighborhood(object):
    "Represents a single neighborhood agent"
    def __init__(self):
        self._NID = NIDGen.next()
        self._NumYearsNonFamilyServices = 15 #TODO
        self._ElecAvailable = boolean_choice()
        self._members = {}

    def get_NID(self):
        "Returns the ID of this neighborhood."
        return self._NID

    def get_households(self):
        return self._members.values()

    def add_household(self, household):
        "Adds a new household to the neighborhood."
        if self._members.has_key(household.get_HID()):
            raise KeyError("household %s is already a member of neighborhood %s"%(household.get_HID(), self._NID))
        self._members[household.get_HID()] = household

    def remove_household(self, household):
        "Removes a household from the neighborhood."
        try:
            self._members.pop(household.get_HID())
        except KeyError:
            raise KeyError("household %s is not a member of neighborhood %s"%(household.get_HID(), self._NID))

    def years_non_family_services(self):
        "Number of years non-family services have been available."
        return self._NumYearsNonFamilyServices

    def elec_available(self):
        "Boolean for whether neighborhood has electricity."
        return self._ElecAvailable

RIDGen = IDGenerator()

class Region(object):
    """Represents a set of neighborhoods sharing a spatial area (and therefore 
    land use data), and demographic characteristics."""
    def __init__(self):
        self._RID = RIDGen.next()

        self._landuse = landuse.LandUse()
        
        # This will store a dictionary of all persons in the population, keyed 
        # by PID
        self._members = {}

        # Now setup the demographic variables for this population, based on the 
        # values given in the model rc file
        self._hazard_birth = rcParams['hazard_birth']
        self._hazard_death = rcParams['hazard_death']
        self._hazard_marriage = rcParams['hazard_marriage']

    def __repr__(self):
        #TODO: Finish this
        return "__repr__ UNDEFINED"

    def __str__(self):
        return "Region(RID: %s. %s neighborhood(s), %s household(s), %s person(s))" %(self.get_RID(), len(self._members), self.get_num_households(), self.census())

    def get_RID(self):
        return self._RID
    def get_neighborhoods(self):
        return self._members.values()

    def add_neighborhood(self, neighborhood):
        "Adds a new neighborhood to the region."
        if self._members.has_key(neighborhood.get_NID()):
            raise KeyError("neighborhood %s is already a member of region %s"%(neighborhood.get_NID(), self._RID))
        self._members[neighborhood.get_NID()] = neighborhood

    def remove_neighborhood(self, neighborhood):
        "Removes a neighborhood from the region."
        try:
            self._members.pop(neighborhood.get_NID())
        except KeyError:
            raise KeyError("neighborhood %s is not a member of region %s"
                    %(neighborhood.get_NID(), self._RID))

    def births(self, time):
        """Runs through the population and agents give birth probabilistically 
        based on their sex, age and the hazard_birth for this population"""
        # TODO: This should take account of the last time the agent gave birth 
        # and adjust the hazard accordingly
        for neighborhood in self._members:
            for household in neighborhood.get_households():
                for person in household.get_persons():
                    if (person.get_sex() == 'female') and (np.random.random()
                            < self._hazard_birth[person.get_age()]):
                                # Agent gives birth. First find the father 
                                # (assumed to be the spouse of the person 
                                # giving birth).
                                dad = household.get_person(
                                        person.get_spousePID())
                                # Now have the mother give birth, and add the 
                                # new person to the mother's household.
                                household.add_person(person.give_birth(time, 
                                    father=dad))
                        
    def deaths(self, time):
        """Runs through the population and kills agents probabilistically based 
        on their age and the hazard_death for this population"""
        for neighborhood in self._members:
            for household in neighborhood.get_households():
                for person in household.get_persons():
                    if (person.get_sex() == 'female') and (np.random.random()
                            < self._hazard_death[person.get_age()]):
                                # Agent dies:
                                person.kill()
                                household.remove_person(person.give_birth(time))
                        
    def marriages(self, time):
        """Runs through the population and marries agents probabilistically 
        based on their age and the hazard_marriage for this population"""
        for neighborhood in self._members:
            for household in neighborhood.get_households():
                for person in household.get_persons():
                    if (person.get_sex() == 'female') and (np.random.random()
                            < self._hazard_marriage[person.get_age()]):
                                # Agent gets married:
                                person.marry(person.get_PID())
                        
    def increment_age(self):
        """Adds one to the age of each agent. The units of age are dependent on 
        the units of the input rc parameters."""
        for neighborhood in self._members:
            for household in neighborhood.get_households():
                for person in household.get_persons():
                    person._age += 1

    def update_landuse(self):
        """Using the attributes of the neighborhoods in the region, update the 
        landuse proportions using OLS"""

    def kill_agent(self):
        "Kills an agent, removing it from its household, and its marriage."

    def census(self):
        "Returns the number of persons in the population."
        total = 0
        for neighborhood in self.get_neighborhoods():
            for household in neighborhood.get_households():
                total += household.num_members()
        return total

    def get_num_households(self):
        total = 0
        for neighborhood in self.get_neighborhoods():
            total += len(neighborhood.get_households())
        return total
