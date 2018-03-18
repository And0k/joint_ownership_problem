#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
# Unit tests of joint_ownership_problem module (elements of the "redistribution fairness")
# Purpose: test for job
# Copyright (C) 2018 Andrey Korzh <ao.korzh@gmail.com>

import unittest
from random import choice
from statistics import variance
from joint_ownership_problem import *


class GeneralFunctionsTest(unittest.TestCase):
    def test_bfs(self):
        dd = {'A': {'B', 'C'}, 'B': {'A', 'D', 'E'}, 'C': {'A', 'F'}, 'D': {'B'}, 'E': {'B', 'F'}, 'F': {'C', 'E'}}
        self.assertEqual(
            list(bfs_paths(lambda x: (x for x in dd[x]), 'A', lambda x: x == 'F')),
            [['A', 'C', 'F'], ['A', 'B', 'E', 'F']])
    #
    # dd = self.cfg['domains']
    # p = bfs_paths(self.World.groups['normal'].o_can_exchange, 2, lambda x: x == 0)
    # self.assertEqual(
    #     list(p),
    #     [[2,0],[2,1,0]])


def assign_o_to_p(group, objects, person, test_fun=None):
    """
    Assign objects to person one by one running test_fun each time after

    Objects are assigned using group.assign_o_to method and take away first if they are not free
    See also: Group.take_away_o, Group.assign_o_to

    :param group: instance of joint_ownership_problem Group class
    :param objects: iterable object, objects person will own
    :param person: str or int, name of person, must be in group.domain
    :param test_fun: run this function after each assignment

    """
    for i, o in enumerate(objects, start=1):
        if group.owner_of_o[o] is not None:
            group.take_away_o(o)
        group.assign_o_to(o, person)
        if test_fun is not None:
            test_fun(group, i, o)


def GroupSetUp(self, number_of_objects=10):
    """
    Specify test data of 2 persons needed for test. Create Group instance, assign properties of test data

    :param self: unittest.TestCase or whatever
    :param number_of_objects: number of objects to distribute
    """
    # Groups will have this number_of_objects to distribute between
    self.number_of_objects = number_of_objects
    Group.owner_of_o = [None] * number_of_objects  # initially free
    # self.owner_of_o = Group.owner_of_o  # copy to check expecting changes of Group.owner_of_o

    self.groups = {'normal': Group()}
    # person's data:
    self.domains = {'Vasia': {1, 2, 3, 4, 5},
                    'Pasha': {3, 4, 5, 6}}
    # Assign person's data:
    self.groups['normal'].domains = self.domains
    self.groups['normal'].capitals = {}.fromkeys(self.domains, 0)


class GroupObjectsAssignmentsTest(unittest.TestCase):
    """ Objects assignment/take away in group test"""
    def setUp(self):
        GroupSetUp(self)

    def test_group_assign(self, test=True):
        """ Assign to person all objects from its domain one by one """

        person = 'Vasia'

        def test_fun(group, i, o):
            msg = f'Assigned object {o} to person {person}'
            self.assertEqual(Group.owner_of_o[o], person, msg=msg)
            self.assertEqual(group.capitals[person], i, msg=msg + '. Capital updated')
            self.assertTrue(group.need_even_out, msg=msg +
                            'This must set flag of need to even out the capitals')

        assign_o_to_p(self.groups['normal'], self.domains[person], person, test_fun=test_fun)

    def test_group_take_away_o(self):
        """ Take away from person N its first objects one by one """

        N = 2
        person = 'Vasia'
        assign_o_to_p(self.groups['normal'], self.domains[person], person)
        o_added = self.groups['normal'].capitals[person]
        for i, o in enumerate(self.domains[person]):
            if i == N:
                break
            person_return = self.groups['normal'].take_away_o(o)

            self.assertEqual(person_return, person)
            msg = f'Removed object {o}'
            self.assertIsNone(Group.owner_of_o[o], msg=msg)
            o_added -= 1
            self.assertEqual(self.groups['normal'].capitals[person], o_added, msg=msg + '. Capital updated')
            self.assertTrue(self.groups['normal'].need_even_out, msg=msg +
                            'This cause the needs of even out the capitals')

    def test_group_assign_o_to_if_o_is_owned(self):
        """ Assigning of not free objects to person raises PersonRobbingError error """

        o = 1
        Group.owner_of_o[o] = 'Vasia'
        self.assertRaises(PersonRobbingError, self.groups['normal'].assign_o_to, o, 'Pasha')


class GroupNormalTest(unittest.TestCase):
    """ Person adding/removing and automatic objects assignments in group test"""
    def setUp(self):
        GroupSetUp(self)
        assign_o_to_p(self.groups['normal'], {1,2,3,4}, 'Vasia')
        assign_o_to_p(self.groups['normal'], {5,6}, 'Pasha')
        assert(Group.owner_of_o == [None, 'Vasia', 'Vasia', 'Vasia', 'Vasia', 'Pasha', 'Pasha', None, None, None])

    def test1_group_add_person(self):
        """ Adding 2 persons"""

        # No persons initially
        self.groups['normal'].domains = {}
        self.groups['normal'].capitals = {}
        Group.owner_of_o = [None]*len(Group.owner_of_o)

        # Add person Vasia
        # ----------------
        person = 'Vasia'
        domain = self.domains[person]
        o_assigned_return = self.groups['normal'].add_person(person, domain)

        #Tests
        msg = f'Adding person {person}. Test that '
        self.assertEqual(o_assigned_return, domain, msg +
                         'all free possible objects assigned to person')
        owner_of_o = [person if o in domain else None for o in range(self.number_of_objects)]
        self.assertEqual(Group.owner_of_o, owner_of_o, msg +
                         'distribution updated')
        self.assertEqual(self.groups['normal'].domains[person], domain, msg +
                         'group have entry for person domain')
        self.assertEqual(self.groups['normal'].capitals[person], len(domain), msg +
                         'group have entry for person capital')
        self.assertEqual(self.groups['normal'].domain_union, domain, msg +
                         'union of group domains is correct')

        # Add person Pasha
        # ----------------
        person = 'Pasha'
        domain = self.domains[person]
        o_assigned_return = self.groups['normal'].add_person(person, domain)

        # Tests
        msg = f'Adding person {person}. Test that '
        o_free = {i for i, p in enumerate(owner_of_o) if p != 'Vasia'}
        o_assigned = domain.intersection(o_free)
        self.assertEqual(o_assigned_return, o_assigned, msg +
                         'all free possible objects assigned to person')
        owner_of_o = ['Vasia' if o in self.domains['Vasia'] else
                      person if o in domain else
                      None for o in range(self.number_of_objects)]
        self.assertEqual(Group.owner_of_o, owner_of_o, msg +
                         'distribution updated')
        self.assertEqual(self.groups['normal'].domains, self.domains, msg +
                         'group have entry for person domain')
        self.assertEqual(self.groups['normal'].capitals.keys(), self.domains.keys(), msg +
                         'group have entry for person capital')
        self.assertEqual(self.groups['normal'].capitals[person], len(o_assigned), msg +
                         'capital calculated')
        self.assertEqual(self.groups['normal'].domain_union,
                         domain.union(self.domains['Vasia']), msg +
                         'union of group domains is correct')

    def test2_group_remove_person(self):
        """ Remove person """

        person = 'Vasia'
        o_of_person = {i for i, p in enumerate(Group.owner_of_o) if p==person}
        o_of_other_person = {i for i, p in enumerate(Group.owner_of_o) if p=='Pasha'}
        assert(o_of_person == {1,2,3,4})
        assert(o_of_other_person == {5, 6})

        o_free_return = self.groups['normal'].remove_person(person)

        # Tests
        msg = f'Remove person {person}. Test that '
        self.assertEqual(o_free_return, o_of_person, msg +
                         "remove_person method returns all person's former owned objects")
        owner_of_o = [None if (o in o_of_person) or (o not in o_of_other_person) else
                      'Pasha' for o in range(self.number_of_objects)]
        self.assertEqual(Group.owner_of_o, owner_of_o, msg +
                         'distribution updated')
        self.assertNotIn(person, self.groups['normal'].domains, msg +
                         'group have no entry for person domain')
        self.assertNotIn(person, self.groups['normal'].capitals, msg +
                         'group have no entry for person capital')
        self.assertEqual(self.groups['normal'].domain_union, self.domains['Pasha'], msg +
                         'union of group domains is correct')

    def test3_group_o_can_exchange(self):
        """ Which objects and owners can be accessed by requester person """

        person = 'Pasha'

        # Test we get all owned by other person objects from intersection of domains
        objects_return = set()
        persons_return = set()
        for o, p in self.groups['normal'].o_can_exchange((None, person)):
            objects_return.add(o)
            persons_return.add(p)
        self.assertEqual(objects_return, {3, 4})
        self.assertEqual(persons_return, {'Vasia'})

    def test4_group_even_out(self):
        """ How evenly even_out() distribute objects between persons of group """

        # Have all persons from setUp. Note: they can be equal out to have zero variance

        # 1. Even out specified distribution objects
        # ------------------------------------------
        assert(variance(self.groups['normal'].capitals.values()) > 0)
        # test
        self.groups['normal'].even_out()
        self.assertEqual(variance(self.groups['normal'].capitals.values()), 0)

        # 2. Randomly assign to persons all possible objects N times
        # ----------------------------------------------------------
        N = 10
        for i in range(N):
            Group.owner_of_o = [None] * self.number_of_objects
            self.groups['normal'].capitals = {}.fromkeys(self.domains, 0)
            for o in range(self.number_of_objects):
                try:
                    person = choice([p for p, d in self.domains.items() if o in d])
                except IndexError: # no possible owner
                    continue
                self.groups['normal'].assign_o_to(o, person)

            # variance_before = variance(self.groups['normal'].capitals.values())
            self.groups['normal'].need_even_out = True
            # test
            self.groups['normal'].even_out()
            variance_after = variance(self.groups['normal'].capitals.values())
            # todo: chek with random possible owners using this check:
            # self.assertGreaterEqual(variance_before, variance_after,
            #                         msg=f'{i}. evened out distribution: {Group.owner_of_o}')
            self.assertEqual(variance_after, 0)

    def test5_group_poorest_acceptor(self):
        """ Is output of poorest_acceptor(o) is poorest possible owner of o if any, else None """

        # Test for each object with following logic:
        # Pasha is poorest so if object in its domain return 'Pasha',
        # else if object in Vasia's domain return 'Vasia',
        # else return None
        for o in range(self.number_of_objects):
            msg = f'Testing object {o}'
            if o in self.groups['normal'].domains['Pasha']:
                self.assertEqual(self.groups['normal'].poorest_acceptor(o), 'Pasha', msg=msg)
            elif o in self.groups['normal'].domains['Vasia']:
                self.assertEqual(self.groups['normal'].poorest_acceptor(o), 'Vasia', msg=msg)
            else:
                self.assertIsNone(self.groups['normal'].poorest_acceptor(o), msg=msg)


class GroupLowprioTest(unittest.TestCase):
    """
    Test GroupLowprio class: overloaded methods of Group class,
    how Lowprio group (GroupLowprio) members depends on actions in normal group (Group).
    """
    def setUp(self):
        """
        Test group dependence on persons addition and setup for other tests at same time

        To be more specific (fair?) we will add only females into lowprio group i.e. mountain sex discrimination.
        """
        # Normal persons initalisation: same as GroupNormalTest.setUp
        # but with care of Group.domain_union
        GroupSetUp(self, number_of_objects=10)
        # Add Lowprio group
        self.groups['lowprio'] = GroupLowprio(self.groups['normal'])
        self.assertFalse(self.groups['lowprio'].need_even_out, msg=
        'need_even_out flag must not set initially')
        for person in ('Pasha', 'Vasia'):  # use this order of the person addition
            self.groups['normal'].add_person(person, self.domains[person])
        self.assertTrue(self.groups['normal'].need_even_out, msg=
        'Adding persons to normal group must set flag of need to even out the capitals of normal')
        self.assertTrue(self.groups['lowprio'].need_even_out, msg=
        'Adding persons to normal group must set flag of need to even out the capitals of lowprio')
        self.assertEqual(Group.owner_of_o, [None, 'Vasia', 'Vasia', 'Pasha', 'Pasha', 'Pasha', 'Pasha', None, None, None], msg="free objects are "
        "assigned when they in domain of new normal person")  # last person gets last free object(s)

        # When add persons to lowpro group test that only lowpro will set
        #  need_even_out flag
        self.groups['normal'].need_even_out = False
        self.groups['lowprio'].need_even_out = False

        # Lowprio person's data:
        self.domains_lowprio = {'Taia': {4, 5, 6, 7, 8, 9},
                                'Maia': {0, 1, 4, 9}
                               }
        # Assign person's data:
        for person in ('Taia', 'Maia'):  # use this order of the person addition
            self.groups['lowprio'].add_person(person, self.domains_lowprio[person])

        msg = 'Test that when persons added to lowprio group '
        self.assertEqual(Group.owner_of_o, [
            'Maia', 'Vasia', 'Vasia', 'Pasha', 'Pasha',
            'Pasha', 'Pasha', 'Taia', 'Taia', 'Taia'], msg=msg +
            "free objects are assigned")  # last person gets last free object(s)
        self.assertFalse(self.groups['normal'].need_even_out, msg=msg +
            'flag of need to even out the capitals of normals is not set')
        self.assertTrue(self.groups['lowprio'].need_even_out, msg=msg +
            'flag of need to even out the capitals of lowprio is set')
        self.groups['lowprio'].need_even_out = False  # setup for test changes in other tests
        self.assertEqual(self.groups['lowprio'].domain_given_union, (
            self.domains_lowprio['Taia'] | self.domains_lowprio['Maia']), msg=msg +
            'union of their given domains is updated correctly')
        self.assertEqual(self.groups['lowprio'].domain_union, self.groups['lowprio'].domain_given_union - (
            self.domains['Pasha'] | self.domains['Vasia']), msg=msg +
            'lowprio active domain is calculated correctly')


    def test_group_remove_normal_person(self):
        """ Remove normal person. Test influence on the lowprio group
        """
        person = 'Vasia'
        o_of_person = {i for i, p in enumerate(Group.owner_of_o) if p == person}
        o_of_other_person = {i for i, p in enumerate(Group.owner_of_o) if p == 'Pasha'}
        assert(o_of_person == {1, 2})
        assert(o_of_other_person == {3, 4, 5, 6})

        o_free_return = self.groups['normal'].remove_person(person)

        # Tests
        msg = f'Remove normal person {person}. Test that '
        self.assertEqual(o_free_return, o_of_person, msg +
                         "remove_person method returns all person's former owned objects")
        self.assertEqual(Group.owner_of_o, [ 'Maia', None, None, 'Pasha', 'Pasha',
                         'Pasha', 'Pasha', 'Taia', 'Taia', 'Taia'], msg=msg +
                         "only former owned objects in distribution are set free")
        self.assertTrue(self.groups['lowprio'].need_even_out, msg=msg +
                        'flag of need to even out the capitals of lowprio is set')
        lowprio_domain_union = self.groups['lowprio'].domain_given_union - self.domains['Pasha']
        assert(lowprio_domain_union == {0, 1, 7, 8, 9})
        self.assertEqual(self.groups['lowprio'].domain_union, lowprio_domain_union, msg=msg +
                         'lowprio active domain is calculated correctly')

    def test_group_remove_lowprio_person(self):
        """ Remove lowprio person. Test that it is not influence normal priority group
            except set free objects in common owners distribution, but influence lowprio group
        """

        person = 'Taia'
        o_of_person = {i for i, p in enumerate(Group.owner_of_o) if p == person}
        o_of_Maia = {i for i, p in enumerate(Group.owner_of_o) if p == 'Maia'}
        assert(o_of_person == {7, 8, 9})
        assert(o_of_Maia == {0})

        o_free_return = self.groups['lowprio'].remove_person(person)

        normal_properties = {prop: getattr(self.groups['normal'], prop) for prop in
                             {'domains', 'capitals', 'need_even_out', 'domain_union'}}
        # Tests
        msg = f'Remove lowprio person {person}. Test that '
        self.assertEqual(o_free_return, o_of_person, msg +
                         "remove_person method returns all person's former owned objects")
        self.assertEqual(Group.owner_of_o,
                         ['Maia', 'Vasia', 'Vasia', 'Pasha', 'Pasha', 'Pasha', 'Pasha', None, None, None],
                         msg=msg + "only former owned objects in distribution are set free")
        self.assertTrue(self.groups['lowprio'].need_even_out, msg=msg +
            'flag of need to even out the capitals of lowprio is set')

        msgl = msg + 'this influence on lowprio group: '
        self.assertNotIn(person, self.groups['lowprio'].domains, msgl +
                         'group have no entry for person domain')
        self.assertNotIn(person, self.groups['lowprio'].capitals, msgl +
                         'group have no entry for person capital')
        self.assertEqual(self.groups['lowprio'].capitals, {'Maia': 1}, msg +
                         'other loprio capitals are not changed')
        self.assertEqual(self.groups['lowprio'].domain_union, self.domains_lowprio['Maia'] -
                         set.union(*self.domains.values()), msgl +
                         'union of group domains is correct')

        msg = msg + 'this not influence on normal group property: '
        for prop, data in normal_properties.items():
            self.assertEqual(getattr(self.groups['normal'], prop), data, msg + prop)


class WorldTest(unittest.TestCase):
    """
    Test of World class.

    As this class mainly combines other classes methods to get result
    to test that it get good results see integration tests too
    """
    def setUp(self):
        self.World = World(number_of_objects=10)
        self.assertIn('normal', self.World.groups, "normal group created")
        self.assertIn('lowprio', self.World.groups, "lowprio group created")
        self.assertEqual(self.World.n_persons, 0, "person's counter is zero")
        self.assertEqual(id(self.World.owner_of_o), id(self.World.groups['normal'].owner_of_o), "Owners distribution world.owner_of_o is reference to owner_of_o of groups contained in the world")

    def test1_world_add_person(self, test_only=False):
        """
        Test add_person method
        :param only_test: only test how operation is done before without perform operation
        :return:
        """
        if not test_only:
            self.World.add_person('Vasia', {1,2,3}, lowprio=False)

        msg = 'Test that when persons added to World '
        self.assertEqual(Group.owner_of_o, [
            None, 'Vasia', 'Vasia', 'Vasia', None,
            None, None, None, None, None], msg=msg +
            "objects are distributed evenly")
        self.assertEqual(self.World.n_persons, 1, msg=msg + "person's counter increases")
        self.assertEqual(self.World.step, 1, msg=msg + "steps counter increases")

    def test2_persons_flow_step_add_person(self):
        """ Test persons_flow_step of adding persons which uses person_data encoding """
        msg = 'Test of adding persons using persons_flow_step interface: '
        print(msg)

        self.World.persons_flow_step({1, 2, 3}, 'Vasia')  # tests are same as above:
        self.test1_world_add_person(test_only=True)
        self.World.persons_flow_step({1, 2, 3, 4, -1})
        self.assertEqual(Group.owner_of_o, [
            None, 'Vasia', 'Vasia', 'Vasia', 1,
            None, None, None, None, None], msg=msg +
            "adding loprio person gets correct owners distribution")
        self.assertEqual(self.World.n_persons, 2, msg=msg + "persons counter increases")
        self.assertEqual(self.World.step, 2, msg=msg + "steps counter increases")

    def test3_persons_flow_step_remove_person(self):
        """ Test persons_flow_step of removing persons which uses person_data encoding """
        print('Test of removing person using persons_flow_step interface: ')
        self.World.persons_flow_step({1, 2, 3}, 'Vasia')          # tested previously
        self.World.persons_flow_step({1, 2, 3, 4, -1})            # tested previously

        self.World.persons_flow_step(-1)
        msg = 'Test persons_flow_step: '
        self.assertEqual(Group.owner_of_o,
            [None, 'Vasia', 'Vasia', 'Vasia', None,
            None, None, None, None, None], msg=msg +
            "remove loprio person gets correct owners distribution")
        self.assertEqual(self.World.n_persons, 1, msg=msg + "persons counter increases")
        self.assertEqual(self.World.step, 3, msg=msg + "steps counter increases")

# Task statement requires no main!
# if __name__ == '__main__':
#     unittest.main(verbosity=2)
