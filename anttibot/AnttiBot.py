#!/usr/bin/env python
from random import Random
from ants import *
import copy




class AnttiBot:
    TURN_COUNT = 0
    SOLDIER = "soldier"
    CAPTAIN = "captain"
    WARLORD = "warlord"
    PEON = "peon"
    SCOUT = "scout"
    NOROLE = "norole"

    FIRST_SCOUT = 4
    SECOND_SCOUT = 8
    PEON_COUNT = 5

    def __init__(self):
        # define class level variables, will be remembered between turns
        pass
    
    # do_setup is run once at the start of the game
    # after the bot has received the game settings
    # the ants class is created and setup by the Ants.run method
    class Antti:
        target = None
        route = None
        role = None
        newloc = None
        curloc = None
        command_given = False
        command_move = None
        id = -1

        def __init__(self, identifier, loc):
            self.curloc = loc
            self.role = AnttiBot.PEON
            self.id = identifier
            file_object = open('ants.txt', 'a')
            file_object.write("\n***inited new ant:" + str(self.curloc))
            file_object.flush()
            pass

        def get_id(self):
            return self.id

        def get_route(self):
            return self.route

        def set_route(self, newroute):
            self.route = newroute

        def reset_route(self):
            self.route = None

        def get_target(self):
            return self.target
        
        def set_target(self, newtarget):
            self.target = newtarget

        def get_command_given(self):
            return self.command_given

        def give_command(self, move):
            self.command_move = move
            self.newloc = move
            self.command_given = True

        def reset_command(self):
            self.command_move = None
            self.command_given = False
            self.newloc = None
    
        def get_role(self):
            return self.role

        def set_role(self, newrole):
            self.role = newrole

        def get_curloc(self):
            return self.curloc

        def set_curloc(self, newloc):
            self.curloc = newloc

        def set_nextloc(self):
            self.curloc = self.newloc

    my_ants = []
    def count_peons(self):
        count = 0
        for ant in self.my_ants:
            if ant.get_role() == AnttiBot.PEON:
                count += 1
    
        return count

    

    def do_setup(self, ants):
        # initialize data structures after learning the game settings
        self.hills = []
        self.unseen = []           
        for row in range(ants.rows):
            for col in range(ants.cols):
                self.unseen.append((row, col))
                
        pass

    def do_turn(self, ants):
        
        # returns a list of neighboring squares (n,s,w,e) that are passable and are visible
        def get_neighbors(loc, visited):
            neighbors = []
            for a in AIM:
                newloc = ants.destination(loc, a)
                if ants.passable(newloc) and newloc not in visited and ants.visible(newloc):
                    neighbors.append(newloc)
            random.shuffle(neighbors)
            
            return neighbors

        # returns the whole path between two points
        def shortest_path(start, end):
            for key in self.best_paths:
                if key == (str(start) + "," + str(end)):
                    return self.best_paths[key][0]

            visited = list()
            visited.append(start)

            paths = list()

            startNeighbors = get_neighbors(start, visited)
            for n in startNeighbors:
                p = list()
                p.append(n)
                paths.append(p)
               
                visited.append(n)
            iterate = True
            
            while iterate:  
                if ants.time_remaining() < 150:
                    return None
                
                newpaths = list()
                for i in range(0, len(paths)): 
                    p = paths.pop(0)
                    # max depth
                    if len(p) > 25: 
                        iterate = False
                        break

                    pn = get_neighbors(p[len(p)-1], visited)                   
                    
                    for n in pn:
                        p3 = copy.deepcopy(p)
                        visited.append(n)
                        p3.append(n)
                        
                        # if we found the end return the first step of this path
                        if n == end:
                            self.best_paths[str(start) + "," + str(end)] = p3
                            return p3
                        
                        newpaths.append(p3)
                
                paths = newpaths

            return None

        # returns the whole path between two points where target is a list of points
        def shortest_path_to_multiple(start, end):
            for key in self.best_paths:
                if key == (str(start) + "," + str(end)):
                    return self.best_paths[key][0]

            visited = list()
            visited.append(start)

            paths = list()

            startNeighbors = get_neighbors(start, visited)
            for n in startNeighbors:
                p = list()
                p.append(n)
                paths.append(p)
               
                visited.append(n)
            iterate = True
            
            while iterate:  
                if ants.time_remaining() < 150:
                    return None
                
                newpaths = list()
                for i in range(0, len(paths)): 
                    p = paths.pop(0)
                    # max depth
                    if len(p) > 25: 
                        iterate = False
                        break

                    pn = get_neighbors(p[len(p)-1], visited)                   
                    
                    for n in pn:
                        p3 = copy.deepcopy(p)
                        visited.append(n)
                        p3.append(n)
                        
                        # if we found the end return the first step of this path
                        if n in end:
                            self.best_paths[str(start) + "," + str(end)] = p3
                            return p3
                        
                        newpaths.append(p3)
                
                paths = newpaths

            return None

        # route without pathfinding
        # returns the route
        # unless the direct route is not passable, in which case returns None
        def get_passable_route(start, end):
            pf = open ('proute.txt', 'a')
            pf.write("\nSearching from " + str(start) + " to " + str(end))
            pf.flush()
            if ants.distance(start, end) > 15:
                directions = ants.direction(start, end)
                random.shuffle(directions)
                pf.write("\ntoo far")
                pf.flush()
                for d in directions:
                    c = ants.destination(start, d)
                    if c in orders or c in ants.my_hills():
                        next
                    path = []
                    path.append(c)
                    return path
                
                # no direction works, just stay still
                return None
               
            path = []
            i = 1
            pf.write("\nMy hills: " + str(ants.my_hills()))
            pf.flush()
            while True:
                pf.write("\niter " + str(i))
                pf.flush()
                directions = ants.direction(start, end)
                random.shuffle(directions)
                i += 1
                # if target was not in first 30 iters
                if i > 30:
                    return None

                found_passable = False
                for d in directions:
                    c = ants.destination(start, d)
                    pf.write("\nchecking: " + str(c) + " is hill: " + str(c in ants.my_hills()))
                    
                    if c in orders or c in ants.my_hills():
                        next

                    elif c == end:
                        pf.write("\nfound " + str(path))
                        pf.flush()
                        return path
                    elif ants.passable(c):
                        found_passable = True
                        path.append(c)
                        start = c
                        break
                    # if a direct route is not passable return None
                if not found_passable:
                    pf.write("\nNo route! " + str(path))
                    pf.flush()
                    return None

        # turn start!

        board_ants = ants.my_ants()
        orders = {}
        file_object = open('ants.txt', 'a')
        self.TURN_COUNT = self.TURN_COUNT + 1
        file_object.write("\n----- NEW TURN: " + str(self.TURN_COUNT))
        file_object.flush()

        # check status of all ants on board

        for antti_loc in board_ants:
            file_object.write("\nsearching ant in " + str(antti_loc))
            file_object.flush()
            found = False
            for antti_in_list in self.my_ants:
                file_object.write("\nsearching FOR ant :" + str(antti_in_list.get_curloc()))
                file_object.flush()
            
                if antti_in_list.get_curloc() == antti_loc:
                    antti_in_list.reset_command()
                    found = True
                    file_object.write("\n***found ant:" + str(antti_in_list.curloc))
                    file_object.flush()

            # set role of new ant
            if found == False:
                a = self.Antti(len(self.my_ants), antti_loc)
                if len(self.my_ants) == AnttiBot.FIRST_SCOUT:
                    a.set_role(AnttiBot.SCOUT)
                elif self.count_peons() < AnttiBot.PEON_COUNT:
                    a.set_role(AnttiBot.PEON)
                else:
                    a.set_role(AnttiBot.SOLDIER)
                # if just spawned move from hill
                if antti_loc in ants.my_hills():
                    for direction in ('s','e','w','n'):
                        new_loc = ants.destination(antti_loc, direction)
                        if (ants.unoccupied(new_loc) and new_loc not in orders and ants.passable(new_loc)):
                            orders[new_loc] = antti_loc
                            ants.issue_order((antti_loc, direction))
                            a.give_command(new_loc)
                            break

                self.my_ants.append(a)
        
        # continue old routes
        for antti in self.my_ants:
            r = antti.get_route()
            if r != None:
                file_object.write("\nContinue route for:" + str(antti.get_curloc()) + " on route " + str(r))
                file_object.flush()
                new_order = r.pop(0)
                file_object.write("\nNext step: " + str(new_order))
                file_object.write("\nRoute left: " + str(r))
                file_object.flush()
                
                orders[new_order] = antti.get_curloc()
                # direction is ants.direction(loc, dest) 
                # loc = start, dest = end
                directions = ants.direction(antti.get_curloc(), new_order)
                ants.issue_order((antti.get_curloc(), directions[0]))
                antti.give_command(new_order)
                if len(r) > 0:
                    antti.set_route(r)
                else:
                    antti.reset_route()


        # find food for peons
        file_object.write("\n***find food:")
        file_object.flush()
        food_targets = []
        peons = []
        peon_locs = []
        # get all available PEONs
        for antti in self.my_ants:
            if antti.get_role() == self.PEON and not antti.get_command_given():
                peon_locs.append(antti.get_curloc())
                peons.append(antti)
        # find closest peon for each food 
        file_object.write("\n***found available peons:" + str(peon_locs))
        file_object.flush()

        for food_loc in ants.food():
            file_object.write("\nSearching route to food at : " + str(food_loc))
            file_object.flush()
            if len(peons) == 0:
                file_object.write("\nNo peons left!")
                file_object.flush()
                break
            closest_distance = 999
            closest_peon = None
            for i in range(0,len(peons)):
                file_object.write("\iterating " + str(i) + "/" + str(len(peons)))
                file_object.flush()
                peon = peons[i]
                file_object.write("\nChecking peon at : " + str(peon_locs[i]))
                file_object.flush()
                d = ants.distance(food_loc, peon_locs[i])
                file_object.write("\ndistance: " + str(d))
                file_object.flush()
                
                if d < closest_distance:
                    file_object.write("\closest: " + str(i))
                    file_object.flush()
                    closest_distance = d
                    closest_peon = i

            #cur_peon = peons[closest_peon]
            file_object.write("\nClosest peon at: " + str(peon_locs[closest_peon]))
            file_object.write("\nClosest peon object : " + str(peons[closest_peon]))

            file_object.flush()
            #newroute = get_passable_route(peon_locs[closest_peon], food_loc)
            newroute = get_shortest_path(peon_locs[closest_peon], food_loc)
            
            cur_peon = peons[closest_peon]
            if newroute != None:
                file_object.write("\nFound route: " + str(newroute))
                file_object.flush()
                new_loc = newroute[0]
                orders[new_loc] = peon_locs[closest_peon]
                directions = ants.direction(peon_locs[closest_peon], new_loc)
                ants.issue_order((peon_locs[closest_peon], directions[0]))
                
                cur_peon.give_command(new_loc)
                
                newroute.pop(0)
                cur_peon.set_route(newroute)
                
                file_object.write("\nGave order to peon " + str(peons[closest_peon].get_id()) + " at " + str(peon_locs[closest_peon]) + "to move to food at:" + str(food_loc))
                file_object.write("\nStep is : " + str(new_loc) + " on route: " + str(newroute))
                file_object.flush()
                
                peons.pop(closest_peon)
                peon_locs.pop(closest_peon)

            if newroute == None:
                file_object.write("\nNo route!")
                file_object.flush()

        file_object.write("\n---- TURN END ----")
        for antti in self.my_ants:
            file_object.write("\nUpdate loc from " + str(antti.get_curloc()) + " to:")
            antti.set_nextloc()
            file_object.write(str(antti.get_curloc()))
            file_object.flush()


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
        Ants.run(AnttiBot())
    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
