"""
Demo of Gale-Shapley stable marriage algorithm.

Usage is:
   python marriage.py  [menfile]  [womenfile]

or   

   python marriage.py  [menfile]  [womenfile]  V

for verbose mode.   

For simplicity, the file format is assumed (without checking) to match
the following format:

  bob:     alice,carol
  david:   carol,alice

and likewise for the womenfile, where there should be precisely same
number of men as with women, and the identifiers should be
self-consistent between the two files.
"""
import sys

from sets import Set
class Person:
    """
    Represent a generic person
    """
    def __init__(self,name,priorities):
        """
        name is a string which uniquely identifies this person

        priorities is a list of strings which specifies a ranking of all
          potential partners, from best to worst
        """
        self.name = name
        self.priorities = priorities
        self.partner = None

    def __repr__(self):
        return 'Name is ' + self.name + '\n' + \
               'Partner is currently ' + str(self.partner) + '\n' + \
               'priority list is ' + str(self.priorities)


class Man(Person):
    """
    Represents a man
    """
    def __init__(self,name,priorities):
        """
        name is a string which uniquely identifies this person

        priorities is a list of strings which specifies a ranking of all
          potential partners, from best to worst
        """
        Person.__init__(self,name,priorities)
        self.proposalIndex = 0                   # next person in our list to whom we might propose

    def nextProposal(self):
        goal = self.priorities[self.proposalIndex]
        self.proposalIndex += 1
        return goal

    def __repr__(self):
        return Person.__repr__(self) + '\n' + \
               'next proposal would be to ' + self.priorities[self.proposalIndex]
            

class Woman(Person):
    """
    Represents a woman
    """
    def __init__(self,name,priorities):
        """
        name is a string which uniquely identifies this person

        priorities is a list of strings which specifies a ranking of all
          potential partners, from best to worst
        """
        Person.__init__(self,name,priorities)

        # now compute a reverse lookup for efficient candidate rating
        self.ranking = {}
        for rank in range(len(priorities)):
            self.ranking[priorities[rank]] = rank

    def evaluateProposal(self,suitor):
        """
        Evaluates a proposal, though does not enact it.

        suitor is the string identifier for the man who is proposing

        returns True if proposal should be accepted, False otherwise
        """
        return self.partner==None or self.ranking[suitor]<self.ranking[self.partner]



def parseFile(filename):
    """
    Returns a list of (name,priority) pairs.
    """
    people = []
    f = file(filename)
    for line in f:
        pieces = line.split(':')
        name = pieces[0].strip()
        if name:
            priorities = pieces[1].strip().split(',')
            for i in range(len(priorities)):
                priorities[i] = priorities[i].strip()
            people.append((name,priorities))
    f.close()
    return people


def getPercentPaired(man, woman):
    man_pairs = pairings[man]
    total = len(man_pairs)
    return float(man_pairs.count(woman))/float(total)
def printPairings(men):
    for man in men.values():
        percentage = getPercentPaired(man.name, str(man.partner))
        print man.name,'is paired with',str(man.partner),' with percentage ',str(percentage)
        if percentage < 1:
            for woman in set(pairings[man.name]):
                percentage = getPercentPaired(man.name, woman)
                print '\t',woman,str(percentage)


def printShortPairings(men):
    for man in men.values():
        percentage = getPercentPaired(man.name, str(man.partner))
        print man.name,'is paired with',str(man.partner),' with percentage ',str(percentage)
    
def savePairings(men):
    for m in men.values():
        man = m.name
        if man not in pair_keys:
            pair_keys.add(man)
            pairings[man] = []
        pairings[man].append(str(m.partner))
pairings = {}
pair_keys = Set()

if __name__=="__main__":
    max_trials = 1000
    for i in range(0, max_trials):
        execfile('match.py')
        verbose = len(sys.argv)>3
        # initialize dictionary of men
        menlist = parseFile(sys.argv[1])
        men = dict()
        for person in menlist:
            men[person[0]] = Man(person[0],person[1])
        unwedMen = men.keys()
        
        # initialize dictionary of women
        womenlist = parseFile(sys.argv[2])
        women = dict()
        for person in womenlist:
            women[person[0]] = Woman(person[0],person[1])


        ############################### the real algorithm ##################################
        while unwedMen:
            m = men[unwedMen[0]]             # pick arbitrary unwed man
            w = women[m.nextProposal()]      # identify highest-rank woman to which
                                             #    m has not yet proposed
            if verbose:  print m.name,'proposes to',w.name

            if w.evaluateProposal(m.name):
                if verbose: print '  ',w.name,'accepts the proposal'
                
                if w.partner:
                    # previous partner is getting dumped
                    mOld = men[w.partner]
                    mOld.partner = None
                    unwedMen.append(mOld.name)

                unwedMen.remove(m.name)
                w.partner = m.name
                m.partner = w.name
            else:
                if verbose: print '  ',w.name,'rejects the proposal'

            if verbose:
                print "Tentative Pairings are as follows:"
                printPairings(men)
                print
        ####################################################################################
        # we should be done
        # print 'saving pairings for trial '+str(i)
        savePairings(men)
        # printPairings(men)
        if i==max_trials-1:
            printPairings(men)
            print '\n\n'
            printShortPairings(men)
