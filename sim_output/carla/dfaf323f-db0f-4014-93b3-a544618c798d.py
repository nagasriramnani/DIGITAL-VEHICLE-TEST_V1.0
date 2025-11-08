#!/usr/bin/env python3
"""
CARLA Simulation Script: Leaf_Thermal_Performance_Under_Load_Battery
Generated from VTA Test Scenario: dfaf323f-db0f-4014-93b3-a544618c798d

Description: Validate Battery performance characteristics for Leaf under specified conditions
"""

import carla
import random
import time
import math

def main():
    """Main simulation function."""
    # Connect to CARLA server
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    
    try:
        # Get world
        world = client.get_world()
        
        # Configure weather
        weather = carla.WeatherParameters(
            cloudiness=10.0,
            precipitation=0.0,
            precipitation_deposits=0.0,
            wind_intensity=5.0,
            sun_azimuth_angle=180.0,
            sun_altitude_angle=45.0,
            fog_density=0.0,
            fog_distance=0.0,
            wetness=0.0
        )
        world.set_weather(weather)
        
        # Get blueprint library
        blueprint_library = world.get_blueprint_library()
        
        # Spawn ego vehicle
        ego_bp = blueprint_library.filter('vehicle.tesla.model3')[0]
        spawn_points = world.get_map().get_spawn_points()
        
        if len(spawn_points) > 0:
            ego_vehicle = world.spawn_actor(ego_bp, spawn_points[0])
            print(f"Spawned ego vehicle: {ego_vehicle.type_id}")
            
            # Configure physics (if EV platform)
            if "EV" == "EV":
                physics_control = ego_vehicle.get_physics_control()
                physics_control.mass = 1800.0
                ego_vehicle.apply_physics_control(physics_control)
            
            # Spawn traffic vehicles
            traffic_vehicles = []
            vehicle_bps = blueprint_library.filter('vehicle.*')
            
            for i in range(0):
                if i + 1 < len(spawn_points):
                    bp = random.choice(vehicle_bps)
                    vehicle = world.try_spawn_actor(bp, spawn_points[i + 1])
                    if vehicle:
                        traffic_vehicles.append(vehicle)
                        vehicle.set_autopilot(True)
            
            print(f"Spawned {len(traffic_vehicles)} traffic vehicles")
            
            # Enable autopilot for ego vehicle
            ego_vehicle.set_autopilot(True)
            
            # Run simulation
            duration = 28980.34918689129
            start_time = time.time()
            
            print(f"Running simulation for {duration} seconds...")
            
            while time.time() - start_time < duration:
                # Get ego vehicle state
                transform = ego_vehicle.get_transform()
                velocity = ego_vehicle.get_velocity()
                speed_kmh = 3.6 * math.sqrt(velocity.x**2 + velocity.y**2 + velocity.z**2)
                
                print(f"Time: {time.time() - start_time:.1f}s | "
                      f"Position: ({transform.location.x:.1f}, {transform.location.y:.1f}) | "
                      f"Speed: {speed_kmh:.1f} km/h")
                
                time.sleep(1.0)
            
            print("Simulation completed")
            
            # Cleanup
            ego_vehicle.destroy()
            for vehicle in traffic_vehicles:
                vehicle.destroy()
            
            print("Actors cleaned up")
        
        else:
            print("Error: No spawn points available")
    
    except Exception as e:
        print(f"Error during simulation: {e}")
    
    finally:
        print("Simulation finished")


if __name__ == '__main__':
    main()
