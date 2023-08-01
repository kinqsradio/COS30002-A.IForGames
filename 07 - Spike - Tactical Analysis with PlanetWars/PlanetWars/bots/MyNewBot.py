from random import choice
from collections import Counter

class MyNewBot(object):
    def update(self, gameinfo):
        # only send one fleet at a time
        if gameinfo.my_fleets:
            return
        
        # check if we should attack
        if gameinfo.my_planets and gameinfo.not_my_planets:
            # select strategic target and destination

            # Always send from the planet with the highest value
            src = max(gameinfo.my_planets.values(), key=lambda p: p.num_ships)

            # Filter planets with less ships than our src fleet
            # src.num_ships is multiplied by 0.75 as that is the size of the fleet that is being sent out
            less_ships = filter(lambda x: x.num_ships < round(src.num_ships * 0.75), gameinfo.not_my_planets.values())

            # Choose destination based on the highest value that represents the ratio between distance and value is calculated
            dest = max(less_ships, default=min(gameinfo.not_my_planets.values(), key=lambda p: p.distance_to(src)), key=lambda p: (p.num_ships + p.growth_rate) / p.distance_to(src))

            # launch new fleet if there's enough ships
            if src.num_ships > 10:
                gameinfo.planet_order(src, dest, int(src.num_ships * 0.75))

            print("Planet {} attacked Planet {} from a distance of {:.2f} with {} ships".format(src.id, dest.id, round(src.distance_to(dest)), round(src.num_ships * 0.75)))
