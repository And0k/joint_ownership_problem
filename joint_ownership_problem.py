#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Purpose: test for job
# Copyright (C) 2018 Andrey Korzh <ao.korzh@gmail.com>
"""
Joint ownership problem solution using EOCA algorithm (see README.MD)

Abbreviations:
o - objects
p - persons (same as possible owners)
"""

from collections import deque
from operator import itemgetter

# General functions
def bfs_paths(fun_graph, start, fun_goal):
    """
    Generation of paths to goal using Breadth First Search

    :param fun_graph: function(node) returning iterator to joint graph nodes
    :param start: node to start
    :param fun_goal: function(node) returning True if node is goal node
    :return:

    >>> graph = {'A': {'B', 'C'}, 'B': {'A', 'D', 'E'}, 'C': {'A', 'F'}, 'D': {'B'}, 'E': {'B', 'F'}, 'F': {'C', 'E'}}
    >>> list(bfs_paths(lambda x: (x for x in graph[x]), 'A', lambda x: x == 'F'))
    [['A', 'C', 'F'], ['A', 'B', 'E', 'F']]
    """
    queue = deque([(start, [start])])
    while queue:
        (node, path) = queue.popleft()

        for next_node in fun_graph(node):
            if next_node in path:
                continue  # path2next = path + [next_node]

            path2next = path.copy()
            path2next.append(next_node)
            if fun_goal(next_node):
                yield path2next
            else:
                queue.append((next_node, path2next))


def shortest_path(fun_graph, start, fun_goal):
    """
    Return first occurrence of target node using Breadth First Search

    :param fun_graph: iterator, returns joint nodes on each call
    :param start: start node argument for fun_graph
    :param fun_goal: bool function(node) returning True if node is target
    :return: list, shortest path through the nodes returned by fun_graph

    >>> graph = {'A': {'B', 'C'}, 'B': {'A', 'D', 'E'}, 'C': {'A', 'F'}, 'D': {'B'}, 'E': {'B', 'F'}, 'F': {'C', 'E'}}
    >>> shortest_path(lambda x: (x for x in graph[x]), 'A', lambda x: x == 'F')
    ['A', 'C', 'F']
    """
    try:
        return next(bfs_paths(fun_graph, start, fun_goal))
    except StopIteration:
        return []


def argsort(dictionary):
    """
    Sort dictionary values. Returns key and value pairs sorted by values

    :param dictionary: dict
    :return sorted by values list of tuples (names, values):

    >>> argsort({'a': 7, 'b': 2, 'c': 5})
    [('b': 2), ('c': 5), ('a': 7)]
    """
    name_value = sorted(dictionary.items(), key=itemgetter(1))
    return name_value


# Task specific functions

class PersonRobbingError(Exception):
   def __init__(self, msg= "Trying to reassign somebody's object. Use Group.take_away_o method!"):
       self.message = msg


class Group:
    """
    Class for persons of normal priority group

    Attributes
    ----------
    owner_of_o: list of str or ints
        list of person_names who owns objects. Class variable i.e. shared between groups.
        Note: Target is to even out this distribution.
    domains: dict of sets
        {person_name: {possible objects}} - all person's domains of group
            person_name: str or int, name/ID of person
            {possible objects}: set of ints, possible objects to own
    capitals: dict of ints
        {person_name: capital} - all person's capitals in group
        person_name: str or int, name/ID of person
        capital: sum of owned objects
    need_even_out: bool
        Call to even_out method is needed to distribute ownership evenly
    domain_union: set
        Overall group domain
    """

    owner_of_o = []                 # target property

    def __init__(self):
        """
        Initialisation of empty group's properties
        """
        self.lowprio = False
        self.domains = {}  # :
        self.capitals = {}  #
        self.need_even_out = False  # ownership equality is not was broken
        self.domain_union = set()

    def free_objects_to_person(self, person):
        """
        Utility to add free objects to person
        :param person: int or str, person's name
        :return: set, assigned objects
        """

        o_assigned = set()
        for o in self.domains[person]:
            if self.owner_of_o[o] is None:
                self.assign_o_to(o, person)
                o_assigned.add(o)
        return o_assigned

    def add_person(self, person, domain):
        """
        Adding person

        Updates domains, domain_union and capitals.
        Calls notify_dependent_group() function, which can be extended at dependent group initialisation
        Assign's free objects to person.
        Sets flag that capitals are need to even out

        :param person: string or number - Name of person. Must not be in domains
        :param domain: set, possible objects to own
        :return: set, previously free objects assigned to person

        """
        self.domains.update({person: domain})
        self.domain_union.update(domain)
        self.capitals.update({person: 0})
        self.notify_dependent_group()
        self.need_even_out = True
        return self.free_objects_to_person(person)

    def remove_person(self, person):
        """
        Removing person, free its owned objects

        :param person: person's name in dict of domains of group
        :return: set, objects become free
        """
        # free person's objects
        o_get_free = set()
        for o in self.domains[person]:
            if self.owner_of_o[o] == person:
                self.owner_of_o[o] = None
                o_get_free.add(o)

        del self.domains[person]
        del self.capitals[person]
        self.need_even_out = True

        # update domain_union
        self.domain_union = set()
        for domain in self.domains.values():
            self.domain_union.update(domain)
        self.notify_dependent_group()
        return o_get_free

    def notify_dependent_group(self):
        """
        For reassigning on initialisation of dependent group. Called when list of persons of this group changed
        """
        pass

    def assign_o_to(self, o, person):
        """
        Assigns object to person

        Updates capitals and need_even_out because this action brakes ownership equality

        :param o: object
        :param person: acceptor
        :return: None

        Note: object must be free before assignment. Else call take_away_o first.
        This ensures update capital of previous owner
        """
        # Prohibit direct assign of other person's objects
        if self.owner_of_o[o] is not None:
            raise(PersonRobbingError())

        self.owner_of_o[o] = person
        self.capitals[person] += 1
        self.need_even_out = True  # mark that this action may brake ownership equality

    def take_away_o(self, o):
        """
        Take away object from current owner and set it free.

        Updates capitals and need_even_out because this action brakes ownership equality

        :param o: object
        """
        person = self.owner_of_o[o]
        self.capitals[person] -= 1
        self.owner_of_o[o] = None
        self.need_even_out = True
        return person

    def even_out(self):
        """
        Evenly distribute objects between persons of group

        This function implements of Even Out Capitals Algorithm based on following idea.
        If possible acceptor and donor is not joint through their object rights it is not means that
        donor can not deliver object to acceptor because it can exchange objects with its neighbours
        that can deliver its other object to acceptor (see example in readme).
        So we try to find path through persons (who can exchange) from possible acceptor to donor.

        As result owner_of_o must have lower variance or nothing must be done

        Note: All objects must have been assigned already some way because free objects are not considered
        """
        if not self.need_even_out:
            return
        while True:  # in each cycle assign 1 object
            # 1. Create list of persons sorted by their capital
            person_capital_sorted = argsort(self.capitals)

            # 2. For each person in list order (possible acceptor) try to assign any object from possible donors
            for acceptor, c in person_capital_sorted:
                # Possible donors capital must be bigger on 2 or more objects than acceptor:
                if c + 1 >= person_capital_sorted[-1][-1]:
                    return  # can not even out better

                # Same rule to identify target objects. But as we will construct graph from tuple
                # nodes (o, owner of o) (see o_can_exchange) to identify target nodes we need function:
                def o_of_possible_donors(node):
                    return self.capitals[node[1]] > c + 1

                # path of objects of different persons who can exchange to some target object:
                path = shortest_path(self.o_can_exchange, (None, acceptor), o_of_possible_donors)

                # 3. If path found then assign objects in accordance with it and go to step 1.
                if len(path) <= 1:
                    continue  # try other acceptor or return
                for o, o_owner in path[1:]:
                    previous_owner = self.take_away_o(o)
                    assert previous_owner == o_owner
                    self.assign_o_to(o, acceptor)
                    acceptor = previous_owner
                break  # need resort capital so restart outer cycle
            else:
                break  # distribution found

    def o_can_exchange(self, requested_o_and_requester):
        """
        Generates objects and owners which can be accessed by requester person

        :param requested_o_and_requester: tuple, (requested_o, requester):
            requested_o: not used here - kept as part of data structure
            requester: person
        :yields tuple, (o, o_owner):
            o: object of other owner in domain of requester
            o_owner: current owner of o

        Used here to obtain graph of objects connected by owner rights.
        The graph used to propagate the exchange of objects from richest to poorest owner.
        """
        requested_o, requester = requested_o_and_requester
        for o in self.domains[requester]:
            current_owner = self.owner_of_o[o]
            if current_owner == requester:
                continue
            else:
                yield (o, current_owner)

    def poorest_acceptor(self, o):
        """
        Poorest possible owner of o
        :param o: object
        :return: poorest possible owner of o if any else None

        Giving to poorest is initial approximation of equality
        """
        poorest = None
        min_capital = float('inf')
        for person, domain in self.domains.items():
            if o in domain:
                capital_of_p = self.capitals[person]
                if min_capital > capital_of_p:
                    min_capital = capital_of_p
                    poorest = person
        return poorest


class GroupLowprio(Group):
    """
    Group with support for active domains and given domains.

    Attributes
    ----------
    domains_given: list of sets
        {'person name': {possible objects}}
            {possible objects} is domain of possible objects given to person
    domains: dict of sets:
        {'person name': {possible objects}}
        {possible objects} here is active domain of objects, which excludes
        objects of overall normal priority group domain. Active domains are
        automatically updated after adding/removing persons in normal priority group
    normal_domain_union: set
        domain_union of normal priority group
    domain_union: set
        Union of all active domains of this group

    Other public attributes are the same as for Group class
        
    """

    def __init__(self, normal_group):
        """
        :param normal_group: lowprio group persons depends on this normal group
        Attributes
        ----------

        """
        super().__init__()
        self.lowprio = True                 # ID of this group
        self.domains_given = {}             # not all objects given will be active domains
        self.domain_given_union = set()
        self._normal_group = normal_group   # to create normal_domain_union attribute
        normal_group.notify_dependent_group = self.calculate_active_domains

    @property
    def normal_domain_union(self):
        """
        Get reference to domain_union of normal group
        """
        return self._normal_group.domain_union

    def calculate_active_domains(self):
        """
        Calculate active domains and updates domain_union accordingly

        Domains and domain_union are calculated by excluding objects
        owned by normal priority group from given_domains
        """

        for name, domain_given in self.domains_given.items():
            self.domains[name] = domain_given.difference(self.normal_domain_union)
        self.domain_union = self.domain_given_union.difference(self.normal_domain_union)
        self.need_even_out = True

    def add_person(self, person, domain_given):
        """
        Adding person

        Updates domains_given, domain_given_union
        Calculate active domains
        Ather action same as

        :param person: string or number - Name of new person. Must not be in lowprio domains
        :param domain_given: set, possible objects to own for new person
        :return: set, previously free objects assigned to new person

        """
        # Update given domains
        self.domains_given.update({person: domain_given})
        self.domain_given_union.update(domain_given)

        # Calculate active domains
        # Instead cycle in self.calculate_active_domains() here we can use one difference:
        self.domains[person] = domain_given.difference(self.normal_domain_union)
        self.domain_union = self.domain_given_union.difference(self.normal_domain_union)

        self.need_even_out = True
        self.capitals.update({person: 0})
        return self.free_objects_to_person(person)

    def remove_person(self, person):
        """
        Removing person

        Updates domains_given, domain_given_union
        Updates active domains
        Assign's free objects to person.

        :param person: string or number - Name of person. Must not be in lowprio domains
        :return: set, previously free objects assigned to person

        """
        # Update given domains
        # To update given domains instead of active domains in super().remove_person body we assighn
        self.domains = self.domains_given
        self.domain_union = self.domain_given_union

        o_get_free = super().remove_person(person)

        # Assign obtained values back (if it is reference to new object now) or break referencing (else):
        self.domains_given = self.domains.copy()
        self.domain_given_union = self.domain_union.copy()

        # Calculate active domains
        self.calculate_active_domains()

        return o_get_free


class World:
    """
    World of two groups of persons: 'lowprio' and 'normal'.

    Adding/removing persons will automatically even out persons's ownership within groups.

    Attributes
    ----------
    groups: dict of :obj:Group, {'normal': :Group, 'lowprio': :GroupLowprio}
    'normal' persons will always displace 'lowprio' persons from their objects
    n_persons: number of persons in the world
    step: person add/remove operations counter in the world

    """

    def __init__(self, number_of_objects, persons_flow=None):
        """
        Groups initialisation and optionally run series of adding/removing persons

        :param number_of_objects: number of objects. Determine length of result
        :param persons_flow: list of actions (see persons_flow_step())

        """

        # Groups of persons:
        Group.owner_of_o = [None] * number_of_objects
        self.groups = {'normal': Group()}
        self.groups['lowprio'] = GroupLowprio(self.groups['normal'])

        self.n_persons = 0          # number of persons in the world
        self.step = 0
        if persons_flow is None:
            print('')               # world created
            return
        print('Flow of persons in new world begins')
        print('{}. {}{}\t{}\t{}'.format('#', 'act.', 'name', 'owners', 'domain'))
        for person in persons_flow:
            self.persons_flow_step(person)

    @property
    def owner_of_o(self):
        return Group.owner_of_o

    @property
    def owner_of_o_str(self):
        """ Short string representing objects owners distribution by using first letter of names of owners

        Free objects are denotes by '-'
        """
        return ''.join('-' if o is None else str(o)[0] for o in self.owner_of_o)

    def __str__(self):
        return f"{type(self).__name__}:	{self.n_persons} persons. Ownership = {self.owner_of_o_str}"

    def persons_flow_step(self, person_data, person=None):
        """
        Add or remove person according to person_data

        :param person_data: action (adding o removing person) coded dependant of type.
            If it is a _set_ - add domain of normal persons, or lowprio persons if
                             set contains value = -1: this value only to mark lowprio
                             persons and will be deleted.
            a _negative int_ - absolute value of this numbers means persons to delete
        :param person: name of person, if None (default) then will be assigned unique int number
        :return:
        """

        if isinstance(person_data, int):  # remove person
            name = abs(person_data)
            self.remove_person(name)
            action = '-'
        else:  # add person
            try:
                person_data.remove(-1)
            except KeyError:
                lowprio = False
                action = '+'
            else:
                lowprio = True
                action = 'L'
            name = self.add_person(person, person_data, lowprio=lowprio)
        info_str = f'{self.step:02d}. {action}{name}\t{self.owner_of_o_str}\t{person_data}'
        print(info_str)

    # Actions
    # As of keeping state requirement we need implement only adding and removing 1 person
    def add_person(self, person=None, domain=set(), lowprio=False):
        """
        Add person to specified group and even out persons capitals

        :param person: name of person, if None then will be assigned unique int number
        :param domain: list of possible objects to hold
        :param lowprio: person will be assigned to low priority group
        :return: int or str, name of person (unique int name generated if person=None)
        """

        if person is None:
            # Auto-name
            person = self.n_persons
            while person in self.groups['normal'].domains or person in self.groups['lowprio'].domains:
                person -= 1

        group = self.groups['lowprio' if lowprio else 'normal']
        if not lowprio:
            # lowprio objects that we will need to redistribute between normal persons
            previous_lowprio = domain.intersection(self.groups['lowprio'].domain_union)

        # 1. This assigns objects that have no owner to new person
        o_assigned = group.add_person(person, domain)
        # 2. Assign objects of LOWPRIO persons if new person has normal priority
        if not lowprio:
            for o in previous_lowprio.difference(o_assigned):
                self.groups['lowprio'].take_away_o(o)
                group.assign_o_to(o, person)

        # 3. Update distributions in affected groups using EOCA
        for gr in self.groups.values():
            gr.even_out()

        self.n_persons += 1
        self.step += 1
        return person

    def remove_person(self, person):
        """
        Remove person and even out persons capitals

        :param person: node to remove from graph

        """
        # find person's group
        for gr in self.groups.values():
            if person in gr.domains:
                previous_group = gr
                break
        else:
            print('Person is not here!')
            return
        o_to_assign = previous_group.remove_person(person)

        for o in o_to_assign:
            # Assign objects of removed person to
            # 1. poorest person of same group with intersected domain, i.e. to:
            acceptor = previous_group.poorest_acceptor(o)
            if acceptor is None:
                # 2. - to any LOWPRIO persons with intersected domain if priority of removed person is normal.
                if not previous_group.lowprio:
                    acceptor = self.groups['lowprio'].poorest_acceptor(o)
                    if acceptor is not None:
                        self.groups['lowprio'].assign_o_to(o, acceptor)
            else:
                previous_group.assign_o_to(o, acceptor)

        # 3. Update distributions in affected groups using EOCA
        for gr in self.groups.values():
            gr.even_out()

        self.n_persons -= 1
        self.step += 1