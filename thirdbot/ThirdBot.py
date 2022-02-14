#!/usr/bin/env python
from os import pathsep
from ants import *
from random import Random
from random import shuffle

try:
    from sys import maxint
except ImportError:
    from sys import maxsize as maxint

import copy

AIM = {'n': (-1, 0),
       'e': (0, 1),
       's': (1, 0),
       'w': (0, -1)}
RIGHT = {'n': 'e',
         'e': 's',
         's': 'w',
         'w': 'n'}
LEFT = {'n': 'w',
        'e': 'n',
        's': 'e',
        'w': 's'}
BEHIND = {'n': 's',
          's': 'n',
          'e': 'w',
          'w': 'e'}

MY_ANT = 0
ANTS = 0
DEAD = -1
LAND = -2
FOOD = -3
WATER = -4
UNSEEN = -5
HILL = -6

PLAYER_ANT = 'abcdefghij'
HILL_ANT = string = 'ABCDEFGHIJ'
PLAYER_HILL = string = '0123456789'
MAP_OBJECT = '?%*.!'
MAP_RENDER = PLAYER_ANT + HILL_ANT + PLAYER_HILL + MAP_OBJECT

# define a class with a do_turn method
# the Ants.run method will parse and update bot input
# it will also run the do_turn method for us
class MyBot:
    def __init__(self):
        self.width = None
        self.height = None
        self.map = None
        self.ant_list = {}
        self.food_list = []
        self.dead_list = []
        self.hill_list = {}
        # define class level variables, will be remembered between turns
        pass
    
    # do_setup is run once at the start of the game
    # after the bot has received the game settings
    # the ants class is created and setup by the Ants.run method
    

    ### setup code starts here

    def do_setup(self, ants):
        # initialize data structures after learning the game settings
        self.my_hills = ants.my_hills()
        self.hills = []

        self.unseen = []
        for row in range(ants.rows):
            for col in range(ants.cols):
                self.unseen.append((row, col))

        pass
    
    def do_move(self, ants, ant_to_move, target_square):
        #new_loc = ants.destination(ant_to_move, target_square)
        pf = open('3route.txt','a')
        pf.write("\nGiving cmd for ant " + str(ant_to_move) + " to move to " + str(target_square))
        pf.flush()
        directions = ants.direction(ant_to_move, target_square)
        if ant_to_move not in ants.my_ants():
            return False
        for d in directions:
            pf.write("\nDirection for " + str(ant_to_move) + " is " + str(d))
            pf.flush()
            ts = ants.destination(ant_to_move, d)
            pf.write("\nNew destination for " + str(ant_to_move) + " is " + str(ts))
            pf.flush()
            if ants.passable(ts) and ts not in self.my_hills and ts not in self.orders and ants.unoccupied(ts):
                ants.issue_order((ant_to_move, d))
                # try:
                self.orders.append(ts)
                self.available_ants.remove(ant_to_move)
            #    except (ValueError, KeyError) as e:
             #       pass
                pf.write("\nSuccess!")
                pf.flush()
                return True
            
        # this ant has to stay still?
        pf.write("\nFailure!")
        pf.flush()

        cant_move = True
        for d in ('n','e','s','w'):
            check_loc = ants.destination(ant_to_move, d)
            if not ants.passable(check_loc) or check_loc in self.my_hills or check_loc in self.orders or not ants.unoccupied(check_loc):
                continue
            else:
                cant_move = False
        if cant_move and ant_to_move in self.available_ants:
            self.available_ants.remove(ant_to_move)

        return False

    
    # breadth first search, visited needs to be initiated with first cell
    num_searches_turn = 0
    def bfs(self, ants, visited, paths, target):
        if ants.time_remaining() < 200:
            return None
        bf = open('bfs.txt','a')
        bf.write("\n***New round: Searching for " + str(target))
        """
        bf.write("\nPaths: " + str(paths))
        bf.write("\nLen: " + str(len(paths)))
        bf.flush()
        """
        # check if any targets are in any paths
        for p in paths:
            for t in target:
                if t in p: 
                    bf.write("\nFound! " + str(t) + " in path " + str(p))
                    bf.flush()
                    bf.close()
                    return p
        # find shortest list from paths
        min_path_length = 999
        min_path_index = None
        for i in range(0, len(paths)):
            p = paths[i]
            if len(p) < min_path_length:
                min_path_length = len(p)
                min_path_index = i
        #bf.write("\nShortest path index " + str(min_path_index) + " and length " + str(min_path_length))
        #bf.flush()
        # if shortest is larger than max_depth 
        # return nothing
        if min_path_length > 18:
            return

        #bf.write("\nShortest path " + str(paths[min_path_index]))
        #bf.flush()
        # pop shortest path
        cur_path = paths.pop(min_path_index)
        #bf.write("\nCurrent path " + str(cur_path))
        #bf.flush()
        # search all suitable neighbor cells for last element in the path
        # that are passable, and not in visited
        
        for direction in ('n','e','s','w'):
            new_loc = ants.destination(cur_path[len(cur_path)-1], direction)
            if ants.passable(new_loc) and new_loc not in visited:
                # make a new path for each passable/non-visited
                # add each independently to the search list
                visited.append(new_loc)
                p2 = copy.deepcopy(cur_path)
                p2.append(new_loc)
                paths.append(p2)
        bf.close()

        return self.bfs(ants, visited, paths, target)

    # start loc is first element of path[]
    # target is a list of possible targets
    def dfs(self, ants, visited, target, path, iteration):
        # if the new location is in target, stop here
        if any(x in target for x in path):
            #pf.write("\nFound target? " + str(new_loc))
            #pf.flush()  
            return True, path
        
        pf = open ('3route.txt', 'a')
        
        #pf.write("\niteration " + str(iteration))
        #pf.write("\npath " + str(path))
        #pf.write("\nTargets " + str(target))
        #pf.write("\nVisited " + str(visited))
        #pf.flush()
        if iteration > 10:
            return False, path
        
        new_paths = []
        
        """
        new_locs = []
        dists = {}
        for direction in ('n','e','s','w'):
            new_loc = ants.destination(path[iteration], direction)
            closest_d = 999
            
            for ant in ants.my_ants():
                d = ants.distance(new_loc, ant)
                if d < closest_d: closest_d = d
            dists[]
        """

        for direction in ('n','e','s','w'):
            new_loc = ants.destination(path[iteration], direction)
            pf.write("\nCheck location " + str(new_loc) + " if in targets " + str(target))
            pf.flush()
            # check if new square can be moved to and is not visited yet
            if ants.passable(new_loc) and new_loc not in visited:
                # if neighbor can be moved into, create new paths for each neighbor and
                # append them to a list to be iterated
                p2 = copy.deepcopy(path)
                p2.append(new_loc)
                new_paths.append(p2)
                #pf.write("\ncreated new path: " + str(p2))
                pf.flush()
            
       # visited.append(new_loc)

        # neighbor search over, do dfs for each new path
        iteration = iteration + 1
        for p in new_paths:
            found, path = self.dfs(ants, visited, target, p, iteration)
            if found: return True, path

        return False, path

    # do turn is run once per turn
    # the ants class has the game state and is updated by the Ants.run method
    # it also has several helper methods to use
    available_ants = []
    my_hills = []
    orders = []
    ant_targets = {}
    hills = []
    paths_to_hills = {}

    def do_turn(self, ants):
        self.my_hills = ants.my_hills()
        self.orders = []
        

        pf = open ('3route.txt', 'a')
        pf.flush()
        pf.write("\n--- NEW TURN")
        pf.flush()
        
        self.available_ants = ants.my_ants()
        
        # clear incorrect targets
        for target in self.ant_targets.keys():
            if target not in ants.my_ants():
                self.ant_targets.pop(target)

        # continue following targets
        for ant in self.ant_targets.keys():
            pf.write("\nAnt in target keys: " + str(ant) + " in " + str(self.available_ants))
            pf.flush()

            if ant in self.available_ants:
                target, route = self.ant_targets.pop(ant)
                if not target in ants.food() or target in self.unseen or target in self.hills:
                    continue
                cur_loc = route.pop()
                pf.write("\nContinuing travel from loc " + str(cur_loc) + " on path " + str(route))
                pf.flush()
                if cur_loc not in ants.my_ants():
                    continue
                if self.do_move(ants, ant, route[len(route)-1]):
                    self.ant_targets[cur_loc] = (target, route)
                else:
                    try:
                        self.ant_targets.pop(ant)
                    except KeyError:
                        pass
            else:
                try: 
                    self.ant_targets.pop(ant) 
                except KeyError:
                    pass



        # search closest ant for each food
        pf.write("\n***Food " + str(ants.time_remaining()))
        pf.write("\nAvailable ants: " + str(self.available_ants))
        pf.flush()
        for food_loc in ants.food():
            
            if len(self.available_ants) < 1:
                return
            
            # dont chase food which is closer to enemies
            min_d = 999
            for ant in self.available_ants:
                min_d = min(min_d, ants.distance(food_loc, ant))

            if len(ants.enemy_ants()) > 0:
                pf.write("\nEnemy ants: " + str(ants.enemy_ants()))
                pf.write("\n# of enemies " + str(len(ants.enemy_ants())))
                pf.write("\nFood loc " + str(food_loc))
                #pf.write("\nClosest enemy" + str(ants.closest_enemy_ant(food_loc[0],food_loc[1])))
                pf.flush()
                closest = ants.closest_enemy_ant(food_loc)
                
                if closest != None and ants.distance(food_loc, ants.closest_enemy_ant(food_loc)) < min_d:
                    break
            

            food_route = self.bfs(ants, [[food_loc]], [[food_loc]], self.available_ants)
            if food_route != None and len(food_route) > 2:
                pf.write("\nFood path: " + str(food_route))
                pf.flush()
                next_step = food_route[len(food_route)-2]
                ant_to_move = food_route[len(food_route)-1]
                self.do_move(ants, ant_to_move, next_step)
                food_route.pop()
                # always put next step as targets so we can find the ant next turn
                self.ant_targets[next_step] = (food_loc, food_route)

            """
            # this works but is really bad
            found, food_route = self.dfs(ants, [food_loc], self.available_ants, [food_loc], 0)
            if found:
                # ant_to_move is the last step in route
                # next step in route is the second to last in route
                self.do_move(ants, food_route[len(food_route)-1], food_route[len(food_route)-2])
            """
        
        #  move all ants from hill
        pf.write("\n***Hill "  + str(ants.time_remaining()))
        pf.write("\nAvailable ants: " + str(self.available_ants))
        pf.flush()
        for hill_loc in ants.my_hills():
            if hill_loc in self.available_ants:
                for direction in ('s','e','w','n'):
                    d = ants.destination(hill_loc, direction)
                    if not d in self.orders and self.do_move(ants, hill_loc, ants.destination(hill_loc, direction)):
                        break
        
        # if can intercept enemy before it reaches food



        # closest enemy
        pf.write("\n***Enemy " + str(ants.time_remaining()))
        pf.write("\nAvailable ants: " + str(self.available_ants))
        pf.flush()
        if len(ants.enemy_ants()) > 0:
            enemy_d = 999
            closest_ant_to_enemy = None
            for a in self.available_ants:
                enemy = ants.closest_enemy_ant(a)
                if enemy != None:
                    ed = ants.distance(a, enemy)
                    if ed < enemy_d:
                        enemy_d = ed
                        closest_ant_to_enemy = a
            

        # closest enemy hill
        pf.write("\n***Enemy hills " + str(ants.time_remaining()))
        pf.write("\nAvailable ants: " + str(self.available_ants))
        pf.write("\nMy ants: " + str(ants.my_ants()))
        pf.write("\nEnemy ants: " + str(ants.enemy_ants()))
        pf.flush()
        for hill_loc, hill_owner in ants.enemy_hills():
            if hill_loc not in self.hills:
                self.hills.append(hill_loc)
        ant_dist = []
        for hill_loc in self.hills:
            for ant_loc in self.available_ants:                
                dist = ants.distance(ant_loc, hill_loc)
                ant_dist.append((dist, ant_loc, hill_loc))
        ant_dist.sort()
                
        i = 0
        for dist, ant_loc, hill_loc in ant_dist:
            i = i + 1
            if i % 2 == 0:
                continue
            pf.write("\nSending ant in " + str(ant_loc) + " to attack hill at " + str(hill_loc))
            hill_route = self.bfs(ants, [[ant_loc]], [[ant_loc]], [hill_loc])
            pf.write("\nRoute to hill is: " + str(hill_route))
            pf.flush()
        
            if hill_route == None:
                cur_loc = ant_loc
                d = ants.direction(ant_loc, hill_loc)
                first_step = ants.destination(ant_loc, d[0])
                self.do_move(ants, cur_loc, first_step)
                continue
            else:
                cur_loc = hill_route.pop(0)
                #first_step = hill_route.pop(0)
                self.do_move(ants, cur_loc, hill_route[0])
                self.ant_targets[hill_route[0]] = (hill_loc, hill_route)


        # closest unseen
        # explore unseen areas
        pf.write("\n***Unseen " + str(ants.time_remaining()))
        pf.write("\nAvailable ants: " + str(self.available_ants))
        #pf.write("\nAnts: " + str(ants.my_ants()))
        pf.flush()
        for loc in self.unseen[:]:
            if ants.visible(loc):
                self.unseen.remove(loc)
        
        timeout = False
        for ant_loc in self.available_ants:
            if ant_loc not in ants.my_ants():
                continue
            if timeout: break
            
            unseen_dist = []
            for unseen_loc in self.unseen:
                if timeout: break
                dist = ants.distance(ant_loc, unseen_loc)
                unseen_dist.append((dist, unseen_loc))
            unseen_dist.sort()
            for dist, unseen_loc in unseen_dist:
                if ants.time_remaining() < 50:
                    break
                if ant_loc not in self.available_ants:
                    continue
                    
                self.do_move(ants, ant_loc, unseen_loc)
                """
                pf.write("\nPathing to unseen: " + str(unseen_loc))
                pf.flush()
                unseen_route = self.bfs(ants, [[ant_loc]], [[ant_loc]], [unseen_loc])
                if unseen_route == None: 
                    timeout = True
                    continue
                
                pf.write("\nFound route to unseen: " + str(unseen_route))
                pf.flush()
                cur_loc = unseen_route.pop(0)
                first_step = unseen_route.pop(0)
                self.ant_targets[first_step] = (unseen_loc, unseen_route)
                self.do_move(ants, ant_loc, first_step)
                """    
                    
        # random move
        pf.write("\nRandom Move " + str(ants.time_remaining()))
        pf.write("\nAvailable ants: " + str(self.available_ants))
        pf.flush()
        for ant in self.available_ants:
            if ants.time_remaining() < 50:
                ants.finish_turn()
                return
            directions = list(AIM.keys())
            shuffle(directions)
            pf.write("\nClosest own hill for " + str(ant))
            pf.flush()
            self_hill = ants.closest_own_hill(ant)
            d_to_hill = ants.distance(ant, self_hill)
            best_d = directions[0]
            best_d_distance = d_to_hill
            for d in directions:
                if best_d_distance > 10:
                    break
                new_loc = ants.destination(ant, d)
                new_d = ants.distance(new_loc, self_hill)
                if new_d > best_d_distance:
                    best_d = d
            # random move always away from hill
            new_loc = ants.destination(ant, best_d)
            pf.write("\nGiving random move to " + str(ant) + " to go to " + str(new_loc))
            pf.flush()
        
            self.do_move(ants, ant, new_loc)

            
        
            
if __name__ == '__main__':
    # psyco will speed up python a little, but is not needed
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    
    try:
        # if run is passed a class with a do_turn method, it will do the work
        # this is not needed, in which case you will need to write your own
        # parsing function and your own game state class
        Ants.run(MyBot())
    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
