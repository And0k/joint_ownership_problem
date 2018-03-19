
The collective ownership problem
================================

The program requires Python 3.6 or higher.
To run program unit and integration tests go to _joint_ownership_problem.py_ program directory and execute in command line:
    
    python -m unittest tests/test_units.py
    python -m unittest tests/test_app.py
On Windows with multiple versions of Python and _Python Launcher for Windows_ [(PEP-0397)](https://www.python.org/dev/peps/pep-0397/ ) installed I run:

    py -3.6 -m unittest tests/test_units.py
    py -3.6 -m unittest tests/test_app.py
    
This should output that tests are passed.  
Integration test performs two tests:

1. from Bitworks's integration task statement (see tests/test task demo.pdf)
2. from this document below (it cover more complex cases)

Integration tests (test_app) outputs table of persons flow with columns: _step number, action code, person's name, owners distribution, domain of added person (if action is to add person)_  
_Action code_ consist of

1. "+" sign if adding person of normal priority or "L" letter if low priority
2. person counter (equals to _persons number_ - 1) for who operation is performed

Person's name in tests are generated automatically and it is equal to person counter. To number persons as in integration task statement (starting from 1) person 0 with empty domain is added first. This is not influence on domain distribution.

Task statement
--------------

There are N objects and M persons, M can be greater than, equal to, or less than N. Each person may be able to own some subset of N (for example, N1, N2, N3) - SN. Each person at some point in time may own certain objects from its subset of SN.

At any one time, only one person can own a single object.

The task is to distribute the ownership of objects between entities in accordance with the following restrictions:

1. Persons can be added and removed from the system one by one for a solution to the distribution problem (that is, it is guaranteed that agents will not be deleted and added during the solution of the task)
2. A person can be the owner of only those objects that are in a subset of its admissible objects
3. The distribution should be fair and converge to uniform distribution among the persons
4. The distribution must be stable, that is, when the person is added or removed, there should be no state reset and full recalculation, and ownership cancellation and assignment in accordance with the new disposition must be effected.
5. It should be possible for some person (at initialization) to specify a parameter LOWPRIO. If the person has the priority of LOWPRIO, then it becomes the owner, only if there is no owner of the normal priority and transfers possession when the owner of the normal priority appears.
6. An object can be without someone's possession only if there is no person having it in its permissible objects domain.


Solution
--------

This problem is a Dynamic Constraint Satisfaction Problem (CSP), and it is better to implement it using some of CSP libraries or calling to program in specialized language (for example to leverage force of Aspect Oriented Programming), but my requirements is to use standard Python libraries.
I did not found ready to use Dynamic CSP code but I developed algorithm which is simpler to implement by myself than some of Dynamic CSP algorithm.
This algorithm (EOCA) will be applied for objects owned either by LOWPRIO or by normal persons separately to accomplish overall problem.

Even Out Capital Algorithm (EOCA)
---------------------------------
Even out owners in each cycle assigning 1 object
1. Sort persons by their capital.
2. For each possible acceptor try to take out (assign) any object from richer* persons (possible** donors).
Possible acceptors take in increase order of their capital, possible donors take in reverse order.
> *Capital of donor must be > Capital of acceptor + 1. For example for distribution `00111222` - not try to redistribute ownership, but for `001112222` - try to take out from person 2 to person 0.

> **If possible acceptor and donor is not joint through their object rights it is not means that donor can not deliver object to acceptor
because it can exchange objects with its neighbours that can deliver its other object to acceptor (see example below).
So we try to find path through persons (who can exchange) from possible acceptor to donor.
3. If path found then assign objects in accordance with it and go to step 1. Else return distribution.

Denote:
> EOCA(LOWPRIO) - EOCA for LOWPRIO persons and currently assigned to them objects only

> EOCA(normal)  - EOCA for normal persons and currently assigned to them objects only
domain - rights to objects

Adding person
-------------
1. Assign objects to new person from its domain that are have no owner.
2. If new person has normal priority then give to it possible objects which are assigned to LOWPRIO persons and then update distribution using EOCA(normal).
3. If any of LOWPRIO persons was affected in step 2 or if new person has LOWPRIO priority then update distribution using EOCA(LOWPRIO).


Removing person
---------------
1. Assign objects owned by removing person (if still any) to any persons of same priority with intersected domain. 
2. If priority of removed person is normal then assign its remaining objects to LOWPRIO possible owners or if no such persons then set them free.
3. If person had normal priority then update distribution using EOCA(normal)
4. If any of LOWPRIO persons was affected in steps 1-2 then update distribution using EOCA(LOWPRIO).




Example
-------
Legend:
>"+" - person's domain of normal priority,
>"L" - of low priority

`Given                    `|`Domains/Owners`|`Changing owners steps`
---------------------------|----------------|------------------          
` Objects position:       `|`0123456789... `|`                `
||                      
  `Domain of person 0   `  |`+++++_________`|`                ` 
  `Domain of person 1   `  |`__++++++______`|`                `
  `                     `  |`00001111______`|`                `
**`Add person 2         `**|`+++___________`|`Adding person:  `
**`                     `**|`20001111______`|`- step 3: EOCA(normal)`
**`                     `**|`22001111______`|`- step 3: EOCA(normal) cycle 2`
**`Result               `**|`22000111______`|`- step 3: EOCA(normal) cycle 3`  
**`Remove person 2      `**|`              `|`Removing person:`
**`                     `**|`00000111______`|`- step 1        `
**`Result               `**|`00100111______`|`- step 3: EOCA(normal)`
**`Add LOWPRIO person 2 `**|`______LLLLLLL_`|`Adding person:  `
**`Result               `**|`0010011122222_`|`- step 1        `
**`Add LOWPRIO person 3 `**|`_____LLLLLL___`|`Adding person:  ` 
**`                     `**|`0010011132222_`|`- step 4: EOCA(LOWPRIO)`
**`Result               `**|`0010011133222_`|`- step 4: EOCA(LOWPRIO) cycle 2`
**`Add person 4         `**|`_____++++_____`|`Adding person:  `
**`                     `**|`0010011143222_`|`- step 2               `
**`                     `**|`0010041143222_`|`- step 3: EOCA(normal) `
**`                     `**|`0011044143222_`|`- step 3: EOCA(normal) cycle 2`
**`Result               `**|`0011044143322_`|`- step 4: EOCA(LOWPRIO)` 
