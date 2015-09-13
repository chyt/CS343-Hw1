from OpenNero import *
from common import *

import sys

import Maze
from Maze.constants import *
import Maze.agent
from Maze.agent import *

class IdaStarSearchAgent(SearchAgent):
    """
    IDA* algorithm
    """

    global depth_guess
    global number_moves
    global current_depth
    def __init__(self):
        """
        A new Agent
        """
        # this line is crucial, otherwise the class is not recognized as an AgentBrainPtr by C++
        SearchAgent.__init__(self)
        self.visited = set([])
        self.adjlist = {}
        self.parents = {}
        self.number_moves = 0
        self.current_depth = 0
        self.depth_guess = manhattan_heuristic(0,0)
        print self.depth_guess

        #self.guess = ROWS + COLS - 2
        #print "guess: %i" % guess
        print "---------------------- IDA* ----------------------"

    def idas_action(self, observations):
        r = observations[0]
        c = observations[1]
        current_cell = (r, c)
        # if we have not been here before, build a list of other places we can go
        if current_cell not in self.visited:
            tovisit = []
            for m, (dr, dc) in enumerate(MAZE_MOVES):
                r2, c2 = r + dr, c + dc
                if not observations[2 + m]: # can we go that way?
                    if (r2, c2) not in self.visited:
                        tovisit.append((r2, c2))
                        self.parents[(r2 , c2)] = current_cell
            # remember the cells that are adjacent to this one
            self.adjlist[current_cell] = tovisit
        # if we have been here before, check if we have other places to visit
        adjlist = self.adjlist[current_cell]
        k = 0
        while k < len(adjlist) and adjlist[k] in self.visited:
            k += 1

        # we have arrived at the beginning again
        if current_cell == self.starting_pos and k == len(adjlist):
            print "* * * * * * *\ndepth guess of %i failed, returned to begininng\ncurrent depth is %i\nnumber of visited nodes was %i" % (self.depth_guess, self.current_depth, len(self.visited))

            self.visited = set([])
            #self.parents = {}
            #self.backpointers = {}
            #self.number_moves = 0

            self.depth_guess += 1
            self.current_depth = 0
            next_cell = self.lowest_cost_adj_list(adjlist, k)
            self.parents[next_cell] = current_cell
            self.current_depth += 1
        else:
            # if we don't have other neighbors to visit, back up
            if k == len(adjlist) or self.current_depth >= self.depth_guess:
                next_cell = self.parents[current_cell]
                self.current_depth -= 1
            else: # otherwise visit the next place
                next_cell = self.lowest_cost_adj_list(adjlist, k)
                self.current_depth += 1

        self.visited.add(current_cell) # add this location to visited list
        if current_cell != self.starting_pos:
            get_environment().mark_maze_yellow(r, c) # mark it as yellow on the maze
        v = self.constraints.get_instance() # make the action vector to return
        dr, dc = next_cell[0] - r, next_cell[1] - c # the move we want to make
        v[0] = get_action_index((dr, dc))
        # remember how to get back
        if next_cell not in self.backpointers:
            self.backpointers[next_cell] = current_cell
        self.number_moves += 1
        return v

    def lowest_cost_adj_list(self, adjlist, k):
        lowest_cost = sys.maxint
        lowest_cell = 0
        for cell in adjlist:
            if cell not in self.visited:
                r,c = cell
                if manhattan_heuristic(r,c) < lowest_cost:
                    lowest_cost = manhattan_heuristic(r,c)
                    lowest_cell = cell
                    #print "lowest cost: %i, lowest cell: %s" % (lowest_cost, lowest_cell)
        return lowest_cell

    def initialize(self, init_info):
        self.constraints = init_info.actions
        return True

    def start(self, time, observations):
        # return action
        r = observations[0]
        c = observations[1]
        self.starting_pos = (r, c)
        get_environment().mark_maze_white(r, c)
        return self.idas_action(observations)

    def reset(self):
        self.visited = set([])
        self.parents = {}
        self.backpointers = {}
        self.starting_pos = None
        self.number_moves = 0

    def act(self, time, observations, reward):
        # return action
        return self.idas_action(observations)

    def end(self, time, reward):
        print "Total number of moves: %i" % self.number_moves
        print "Final reward: %f, cumulative: %f" % (reward[0], self.fitness[0])
        print "resetting"
        self.reset()
        return True

    def mark_path(self, r, c):
        get_environment().mark_maze_white(r,c)