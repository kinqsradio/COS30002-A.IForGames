

class BlankoEXTW5:

    def __init__(self):
        self.target_planets = set()
        self.last_seen = {}
        self.is_symetrical = None
        self.turn = 0
        
    def detect_map_symmetry(self, gameinfo):
        planet_coords = [tuple(p.position) for p in gameinfo.planets.values()]
        planet_coords_reversed = [(x[1], x[0]) for x in planet_coords]
        return set(planet_coords) == set(planet_coords_reversed)
        
        
    def get_least_recently_seen(self, gameinfo):
        if not self.last_seen:
            return None
        min_turn = min(self.last_seen.values())
        planet_id = [k for k, v in self.last_seen.items() if v == min_turn][0]
        return gameinfo.get_planet_by_id(planet_id)
        
    def get_most_recently_seen(self, gameinfo):
        if not self.last_seen:
            return None
        min_turn = max(self.last_seen.values())
        planet_id = [k for k, v in self.last_seen.items() if v == min_turn][0]
        return gameinfo.get_planet_by_id(planet_id)
        
    def attack(self, gameinfo):
        if gameinfo.my_planets and gameinfo.not_my_planets:
            # Always send from the planet with the highest value
            src = max(gameinfo.my_planets.values(), key=lambda p: p.num_ships)

            # Filter planets based on distance and ship count
            max_distance = 100
            less_ships = filter(lambda x: x.num_ships < round(src.num_ships * 0.75) 
                                and x.id not in self.target_planets 
                                and src.distance_to(x) <= max_distance, 
                                gameinfo.not_my_planets.values())

            # dest = max(less_ships, 
            #             default=min(gameinfo.not_my_planets.values(), 
            #             key=lambda p: p.distance_to(src)), 
            #             key=lambda p: (2 * p.num_ships + p.growth_rate) / p.distance_to(src))
            
            # Choose the most recently seen enemy planet as the destination
            dest = self.get_most_recently_seen(gameinfo)

            if dest is not None: 
                # Choose destination based on the highest value that represents the ratio between distance, value, and growth rate, prioritizing weaker planets
                dest = max(less_ships, 
                            default=min(gameinfo.not_my_planets.values(), 
                            key=lambda p: p.distance_to(src)), 
                            key=lambda p: (2 * p.num_ships + p.growth_rate) / p.distance_to(src))
            

            # launch new fleet if there's enough ships
            if src.num_ships > 10:
                gameinfo.planet_order(src, dest, int(src.num_ships * 0.75))
                self.target_planets.add(dest.id)

            print("Planet {} attacked Planet {} from a distance of {:.2f} with {} ships".format(src.id, dest.id, round(src.distance_to(dest)), round(src.num_ships * 0.75)))
    
    def defend(self, gameinfo):
        for planet in gameinfo.my_planets.values():
            incoming_fleets = []

            for fleets in gameinfo.enemy_fleets:
                fleet = gameinfo.get_fleet_by_id(fleets)  
                
                #print(fleet)  # Testing
                
                # if fleet.dest.id == planet.id:
                #         incoming_fleets.append(fleet)
                        
                        
                try:
                    if fleet.dest.id == planet.id:
                        incoming_fleets.append(fleet)
                except AttributeError as e:
                    print(f"AttributeError: {e}")

                # If there is, send fleets for defense or find friendly planet for reinforcement
                if incoming_fleets:
                    total_incoming_ships = sum(fleet.num_ships for fleet in incoming_fleets)
                    if planet.num_ships < total_incoming_ships:
                        # find the nearest friendly planet with enough ships for reinforcement
                        planets_with_enough_ships = [p for p in gameinfo.my_planets.values() if
                                                        p.num_ships > total_incoming_ships and p.id != planet.id]
                        nearest_planet = min(planets_with_enough_ships, default=None, key=lambda p: p.distance_to(planet))

                        if nearest_planet:
                            required_ships = total_incoming_ships - planet.num_ships + 1
                            gameinfo.planet_order(nearest_planet, planet, required_ships)  # Send reinforcement

                            print("Planet {} sent {} ships to defend Planet {}".format(nearest_planet.id, required_ships, planet.id))                        


    def send_scouts(self, gameinfo):
        for planet in gameinfo.enemy_planets.values():
            if planet.id not in self.last_seen and planet.id not in self.target_planets:  
                scout_src = min(gameinfo.my_planets.values(), key=lambda p: p.distance_to(planet))
                gameinfo.planet_order(scout_src, planet, 1)  # Send scouts (1 ship)
                self.target_planets.add(planet.id)
                #self.last_seen.add(planet.id)
                self.last_seen[planet.id] = self.turn
                print("Planet {} sent {} ships to scout enemy Planet {}".format(scout_src.id, 1, planet.id))


    def update(self, gameinfo):
        #print("Turn Numbers:", self.turn)
        self.turn += 1
        
        # Send scouts to unexplored enemy planets
        self.send_scouts(gameinfo)

        # Defend planets under attack
        self.defend(gameinfo)

        # Only send one fleet at a time
        if gameinfo.my_fleets:
            return
            
        # Attack enemy planets
        self.attack(gameinfo)

