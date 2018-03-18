#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
# c of joint_ownership_problem module
# Purpose: test for job
# Copyright (C) 2018 Andrey Korzh <ao.korzh@gmail.com>

import unittest
from joint_ownership_problem import *


class MyTestCase(unittest.TestCase):

    def test_bitworks_demo(self):
        print("\nRun example from Bitworks's task statement")
        cfg = {
            'number_of_objects': 10,            # | Expected ownership
            'persons': [                        # | 0123456789
                 (set(),                           '----------'),
                 ({2, 3},                          '--11------'),
                 ({2, 4, 5},                       '--1122----'),
                 ({2},                             '--3122----'),
                 (-2,                              '--31------'),
                 ({2, 3, -1},                      '--31------')]}

        self.World = World(cfg['number_of_objects'])
        for (person, owners) in cfg['persons']:
            self.World.persons_flow_step(person)
            self.assertEqual(self.World.owner_of_o_str, owners)

    @staticmethod
    def get_capitals(owners):
        """
        Get sums of owned objects for each owner

        :param owners: list, owners distribution over objects
        :return: dict, {owner: capital}
        """
        capitals = {}
        for p in owners:
            if p in capitals:
                capitals[p] += 1
            else:
                capitals[p] = 1
        return capitals

    def test_readme_example(self):
        """
        Run example from README.MD

        This test shows chains of exchange (see how person #1 exchange between owners in last row)
        """
        print('\nRun example from README.MD')
        cfg = {
            'number_of_objects': 13,
            'persons': [                        # | 0123456789...        | capitals
                 ({0, 1, 2, 3, 4},                 '00000--------'),   # | {0:5                    }
                 ({2, 3, 4, 5, 6, 7},              '00100111-----'),   # | {0:4, 1:4               }
                 ({0, 1, 2, 3},                    '22000111-----'),   # | {0:3, 1:3, 2:2          }
                 (-2,                              '00100111-----'),   # | {0:4, 1:4               }
                 ({6, 7, 8, 9, 10, 11, 12, -1},    '0010011122222'),   # | {0:4, 1:4, 2:5          }
                 ({5, 6, 7, 8, 9, 10, -1},         '0010011133222'),   # | {0:4, 1:4, 2:3, 3:2     }
                 ({5, 6, 7, 8},                    '0011044143322')]}  # | {0:3, 1:3, 2:2, 3:2, 4:3}

        self.World = World(cfg['number_of_objects'])
        for person, owners in cfg['persons']:
            self.World.persons_flow_step(person)
            # The matter is only owner's capitals not their distribution over objects
            self.assertEqual(
                self.get_capitals(self.World.owner_of_o_str),
                self.get_capitals(owners))

    # todo: check for mutually exclusive persons (if more owners than their common domain union)
    # todo: add random users generator test, check by min possible variance(capitals)


if __name__ == '__main__':
    unittest.main()
