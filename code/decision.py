import numpy as np

# This is where you can build a decision tree for determining throttle, brake and steer
# commands based on the output of the perception_step() function
def decision_step_old(Rover):

    # Implement conditionals to decide what to do given perception data
    # Here you're all set up with some basic functionality but you'll need to
    # improve on this decision tree to do a good job of navigating autonomously!

    # Example:
    # Check if we have vision data to make decisions with

    if Rover.nav_angles is not None:
        # Check for Rover.mode status

        if Rover.mode == 'forward':
            # Check the extent of navigable terrain
            if len(Rover.nav_angles) >= Rover.stop_forward:
                # If mode is forward, navigable terrain looks good
                # and velocity is below max, then throttle
                if Rover.vel < Rover.max_vel:
                    # Set throttle value to throttle setting
                    Rover.throttle = Rover.throttle_set
                else: # Else coast
                    Rover.throttle = 0
                Rover.brake = 0
                # Set steering to average angle clipped to the range +/- 15
                Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
            # If there's a lack of navigable terrain pixels then go to 'stop' mode
            elif len(Rover.nav_angles) < Rover.stop_forward:
                    # Set mode to "stop" and hit the brakes!
                    Rover.throttle = 0
                    # Set brake to stored brake value
                    Rover.brake = Rover.brake_set
                    Rover.steer = 0
                    Rover.mode = 'stop'

        # If we're already in "stop" mode then make different decisions
        elif Rover.mode == 'stop':
            # If we're in stop mode but still moving keep braking
            if Rover.vel > 0.2:
                Rover.throttle = 0
                Rover.brake = Rover.brake_set
                Rover.steer = 0
            # If we're not moving (vel < 0.2) then do something else
            elif Rover.vel <= 0.2:
                # Now we're stopped and we have vision data to see if there's a path forward
                if len(Rover.nav_angles) < Rover.go_forward:
                    Rover.throttle = 0
                    # Release the brake to allow turning
                    Rover.brake = 0
                    # Turn range is +/- 15 degrees, when stopped the next line will induce 4-wheel turning
                    Rover.steer = -15 # Could be more clever here about which way to turn
                # If we're stopped but see sufficient navigable terrain in front then go!
                if len(Rover.nav_angles) >= Rover.go_forward:
                    # Set throttle back to stored value
                    Rover.throttle = Rover.throttle_set
                    # Release the brake
                    Rover.brake = 0
                    # Set steer to mean angle
                    Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
                    Rover.mode = 'forward'
    # Just to make the rover do something
    # even if no modifications have been made to the code
    else:
        Rover.throttle = Rover.throttle_set
        Rover.steer = 0
        Rover.brake = 0
    if Rover.near_sample and Rover.vel == 0 and not Rover.picking_up:
        Rover.send_pickup = True

    return Rover


def decision_step(Rover):
    if Rover.nav_angles is not None:
        # Check for Rover.mode status
        if Rover.mode == 'pickup':
            # If the mode is pickup and we have angles for the rock, move slowly towards the rock, to do a pickup
            #if Rover.r_angles is not None and len(Rover.r_angles) > 0 and not np.isnan(np.mean(Rover.r_angles)):
            if Rover.rock_angles is not None and Rover.obstacles_angles is not None:
                Rover.steer = np.clip(np.mean(Rover.rock_angles * 180/np.pi), -15, 15)
                # Record the direction where the turn was made, this is so that we can resume original heading
                Rover.steer_dir = 1 if Rover.steer > 0 else -1

                if Rover.vel < 1:
                    # Set throttle value to throttle setting
                    Rover.throttle = Rover.throttle_set
                else: # Else coast
                    Rover.throttle = 0
                Rover.brake = 0

                if Rover.near_sample:
                    Rover = brake_control(Rover, True)
                    Rover.throttle = 0
                    # Set brake to stored brake value
                    if hit:
                        Rover.brake = Rover.brake_set
                    else:
                        Rover.brake = 0
                    Rover.steer = 0
                    
                    if Rover.mode == 'pickup':
                        Rover.rocks_collected = Rover.rocks_collected + 1
                    Rover.mode = 'stop'
                    Rover.send_pickup = True
            else:
                # Id we lose sight of the target, move on without getting stuck in the pickup mode
                Rover.mode = 'forward'
        if Rover.mode == 'forward':
            # For the first time the target is seen, orient towards it, stop (as I couldn't find a nicer way to slow down)
            # Set the mode to pickup
            #if Rover.r_angles is not None and len(Rover.r_angles) > 0 and not np.isnan(np.mean(Rover.r_angles)):
            if Rover.rock_angles is not None and Rover.rock_dist is not None:
                Rover.steer = np.clip(np.mean(Rover.rock_angles * 180/np.pi), -15, 15)
                Rover.throttle = 0
                # Set brake to stored brake value
                if hit:
                    Rover.brake = Rover.brake_set
                else:
                    Rover.brake = 0
                    Rover.steer = 0
                Rover.mode = 'pickup'
            elif len(Rover.nav_angles) >= Rover.stop_forward:
                if Rover.vel == 0 and Rover.throttle > 0 and Rover.brake == 0:
                    Rover.steer = -15 if Rover.steer_dir > 0 else 15
                else:
                    if Rover.vel < Rover.max_vel:
                        # Set throttle value to throttle setting
                        Rover.throttle = Rover.throttle_set
                    else: # Else coast
                        Rover.throttle = 0
                    Rover.brake = 0
                    # Set steering to average angle clipped to the range +/- 15
                    Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
                    Rover.steer_dir = 1 if Rover.steer > 0 else -1
            # If there's a lack of navigable terrain pixels then go to 'stop' mode
        elif Rover.obstacles_angles is not None and Rover.obstacles_dist is not None and np.sum(np.mean(Rover.obstacles_dist)) < 5:
                Rover = brake_control(Rover, True)

                Rover.mode = 'stop'
            elif len(Rover.nav_angles) < Rover.stop_forward:
                Rover = brake_control(Rover, True)
                Rover.mode = 'stop'
        # If we're already in "stop" mode then make different decisions
        elif Rover.mode == 'stop':
            # If we're in stop mode but still moving keep braking
            if Rover.vel > 0.2:
                Rover = brake_control(Rover, True)
                Rover = pickup(Rover)
            # If we're not moving (vel < 0.2) then do something else
            elif Rover.vel <= 0.2:
                # Now we're stopped and we have vision data to see if there's a path forward
                if len(Rover.nav_angles) < Rover.go_forward:
                    # Rover = brake_control(Rover, False)
                    # Turn range is +/- 15 degrees, when stopped the next line will induce 4-wheel turning
                    # Based on the direction of turn re-orient to continue in the same direction
                    Rover.throttle = 0
                    Rover.brake = 0
                    Rover.steer = -15 if Rover.steer_dir > 0 else 15
                    #Rover.steer_dir = 0
                # If we're stopped but see sufficient navigable terrain in front then go!
                if len(Rover.nav_angles) >= Rover.go_forward:
                    # Set throttle back to stored value
                    Rover = throttle_control(Rover, Rover.max_vel)
                    # Set steer to mean angle
                    Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
                    Rover.mode = 'forward'
    # Just to make the rover do something
    # even if no modifications have been made to the code
    else:
        Rover.throttle = Rover.throttle_set
        Rover.steer = 0
        Rover.brake = 0

    return Rover
