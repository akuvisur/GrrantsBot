#!/usr/bin/env python
from ants import *
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
# define a class with a do_turn method
# the Ants.run method will parse and update bot input
# it will also run the do_turn method for us
class MyBot:
    def __init__(self):
        # define class level variables, will be remembered between turns
        pass
    
    def bfs(self, ants, visited, paths, target, depth=12):
        if ants.time_remaining() < 200:
            return None
        bf = open('bfs.txt','a')
        bf.write("\n***New round " + str(self.turn) + ": Searching for " + str(target))
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
        bf.write("\nShortest path index " + str(min_path_index) + " and length " + str(min_path_length))
        bf.flush()
        # if shortest is larger than max_depth 
        # return nothing
        if min_path_length > depth:
            return

        #bf.write("\nShortest path " + str(paths[min_path_index]))
        #bf.flush()
        # pop shortest path
        cur_path = paths.pop(min_path_index)
        bf.write("\nCurrent path " + str(cur_path))
        bf.flush()
        # search all suitable neighbor cells for last element in the path
        # that are passable, and not in visited
        
        for direction in ('n','e','s','w'):
            new_loc = ants.destination(cur_path[len(cur_path)-1], direction)
            if ants.passable(new_loc) and new_loc not in visited:
                bf.write("\nLocation " + str(new_loc) + " was OK")
                bf.flush()
                # make a new path for each passable/non-visited
                # add each independently to the search list
                visited.append(new_loc)
                p2 = copy.deepcopy(cur_path)
                p2.append(new_loc)
                paths.append(p2)
            else:
                bf.write("\nLocation " + str(new_loc) + " was NOT OK")
        bf.close()

        return self.bfs(ants, visited, paths, target, depth)

    # do_setup is run once at the start of the game
    # after the bot has received the game settings
    # the ants class is created and setup by the Ants.run method
    turn = 0
    routes = {}
    ignored_targets = []
    def do_setup(self, ants):
        # initialize data structures after learning the game settings
        self.unseen = []
        self.hills = []
        self.routes = {}
        self.turn = 0
        for row in range(ants.rows):
            for col in range(ants.cols):
                self.unseen.append((row, col))
        pass
    


    # do turn is run once per turn
    # the ants class has the game state and is updated by the Ants.run method
    # it also has several helper methods to use
    def do_turn(self, ants):
        self.turn += 1
        pf = open('mybottest.txt','a')
        pf.write("\n\n***NEW TURN: " + str(self.turn))
        pf.flush()
        # track all moves, prevent collisions
        orders = {}
        self.ignored_targets = []
        def do_move_direction(loc, direction):
            new_loc = ants.destination(loc, direction)
            if ants.unoccupied(new_loc) and new_loc not in orders and ants.passable(new_loc):
                ants.issue_order((loc, direction))
                orders[new_loc] = loc
                if new_loc in self.hills:
                    self.hills.remove(new_loc)

                return True
            else:
                return False

        targets = {}
        def do_move_location(loc, dest):
            directions = ants.direction(loc, dest)
            for direction in directions:
                if do_move_direction(loc, direction):
                    targets[dest] = loc
                    return True
            return False
        


        # prevent stepping on own hill
        for hill_loc in ants.my_hills():
            orders[hill_loc] = None
        
        """
        # avoid getting killed
        pf.write("\nDont get killed!")
        pf.flush()
        for ant_loc in ants.my_ants():
            pf.write("\nAnt: " + str(ant_loc))
            pf.flush()
            if ant_loc not in orders.values():
                closest_enemy = ants.closest_enemy_ant(ant_loc)
                pf.write("\nC Enemy: " + str(closest_enemy))
                pf.flush()
                if closest_enemy != None:
                    pf.write("\nDistance to enemy: " + str(ants.distance(ant_loc, closest_enemy)))
                    pf.flush()
                    if ants.distance(ant_loc, closest_enemy) < 5:
                        closest_ally = ants.closest_own_ant(ant_loc)
                        pf.write("\nDistance to ally: " + str(ants.distance(ant_loc, closest_ally)))
                        pf.flush()
                        if closest_ally != None:
                            if ants.distance(ant_loc, closest_ally) >= 2:
                                # move away
                                enemy_direction = ants.direction(ant_loc, closest_enemy)
                                pf.write("\nEnemy direction: " + str(enemy_direction) + " so moving to " + str(BEHIND[enemy_direction[0]]))
                                do_move_location(ant_loc, ants.destination(ant_loc, enemy_direction[0]))
        """

        # find close food
        ant_dist = []
        for food_loc in ants.food():
            for ant_loc in ants.my_ants():
                # if route to food was blocked and 
                # no route to food was found its likely behind a lot of water
                # dont try to send other ants to it
                if food_loc in self.ignored_targets:
                    pf.write("\nIgnored food at: " + str(food_loc))
                    pf.flush()
                    continue
                dist = ants.distance(ant_loc, food_loc)
                ant_dist.append((dist, ant_loc, food_loc))
        ant_dist.sort()
        for dist, ant_loc, food_loc in ant_dist:
            if food_loc not in targets and ant_loc not in targets.values():
                do_move_location(ant_loc, food_loc)
                continue
                enemy_closer = False
                """
                this checks if enemy is closer but enemy can have blocked path
                for enemy in ants.enemy_ants():
                    if ants.distance(enemy[0], food_loc) < dist:
                        enemy_closer = True
                        # enemy is closer to this food, can not reach in time
                        break
                """
                if not enemy_closer: 
                    # find a route to this food
                    
                    # check if route exists
                    # if yes, look for closest point on that route and go there
                    if food_loc in self.routes.keys():
                        route = self.routes[food_loc]
                        min_distance = 999
                        closest_route_location = None
                        for loc_on_route in route:
                            d = ants.distance(ant_loc, loc_on_route)
                            if d < min_distance:
                                closest_route_location = loc_on_route
                        if closest_route_location != None:
                            do_move_location(ant_loc, closest_route_location)
                    # find a new route
                    else:
                        route = self.bfs(ants, [[ant_loc]], [[ant_loc]], [food_loc])
                        if route != None: 
                            pf.write("\nFound route! " + str(route))
                            pf.flush()
                            do_move_location(ant_loc, route[1])
                            self.routes[food_loc] = route
                        else:
                            self.ignored_targets.append(food_loc)
                    do_move_location(ant_loc, food_loc)
        

        

        # attack hills
        for hill_loc, hill_owner in ants.enemy_hills():
            if hill_loc not in self.hills:
                self.hills.append(hill_loc)    
                #pf.write("\nSearching for route to hill depth 50")
                #pf.flush()
                #hill_route = self.bfs(ants, ants.my_hills(), [[ants.my_hills()[0]]], [hill_loc], 30)
                
        ant_dist = []
        for hill_loc in self.hills:
            for ant_loc in ants.my_ants():
                if ant_loc not in orders.values():
                    dist = ants.distance(ant_loc, hill_loc)
                    ant_dist.append((dist, ant_loc, hill_loc))
        ant_dist.sort()
        for dist, ant_loc, hill_loc in ant_dist:
            do_move_location(ant_loc, hill_loc)

        # explore unseen areas
        for loc in self.unseen[:]:
            if ants.visible(loc):
                self.unseen.remove(loc)
        for ant_loc in ants.my_ants():
            if ant_loc not in orders.values():
                unseen_dist = []
                for unseen_loc in self.unseen:
                    dist = ants.distance(ant_loc, unseen_loc)
                    unseen_dist.append((dist, unseen_loc))
                unseen_dist.sort()
                for dist, unseen_loc in unseen_dist:
                    if do_move_location(ant_loc, unseen_loc):
                        break
        # unblock own hill
        for hill_loc in ants.my_hills():
            if hill_loc in ants.my_ants() and hill_loc not in orders.values():
                for direction in ('s','e','w','n'):
                    if do_move_direction(hill_loc, direction):
                        break
            
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
