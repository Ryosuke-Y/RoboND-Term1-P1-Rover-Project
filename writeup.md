## Project: Search and Sample Return
### Writeup Template: You can use this file as a template for your writeup if you want to submit it as a markdown file, but feel free to use some other method and submit a pdf if you prefer.

---


**The goals / steps of this project are the following:**  

**Training / Calibration**  

* Download the simulator and take data in "Training Mode"
* Test out the functions in the Jupyter Notebook provided
* Add functions to detect obstacles and samples of interest (golden rocks)
* Fill in the `process_image()` function with the appropriate image processing steps (perspective transform, color threshold etc.) to get from raw images to a map.  The `output_image` you create in this step should demonstrate that your mapping pipeline works.
* Use `moviepy` to process the images in your saved dataset with the `process_image()` function.  Include the video you produce as part of your submission.

**Autonomous Navigation / Mapping**

* Fill in the `perception_step()` function within the `perception.py` script with the appropriate image processing functions to create a map and update `Rover()` data (similar to what you did with `process_image()` in the notebook).
* Fill in the `decision_step()` function within the `decision.py` script with conditional statements that take into consideration the outputs of the `perception_step()` in deciding how to issue throttle, brake and steering commands.
* Iterate on your perception and decision function until your rover does a reasonable (need to define metric) job of navigating and mapping.  


## [Rubric](https://review.udacity.com/#!/rubrics/916/view) Points
### Here I will consider the rubric points individually and describe how I addressed each point in my implementation.  

---
### Writeup / README

#### 1. Provide a Writeup / README that includes all the rubric points and how you addressed each one.  You can submit your writeup as markdown or pdf.  

I wrote this writeup to explain how I implemented my code in Udacity's Robotics Nanodegree first project.

### Notebook Analysis
#### 1. Run the functions provided in the notebook on test images (first with the test data provided, next on data you have recorded). Add/modify functions to allow for color selection of obstacles and rock samples.
I defined two functions, `obstacle_thresh` and `rock_thresh` to identify samples and obstacles. In rock_thresh, samples are defined as yellow objects. In obstacle_thresh, obstacles are defined as darker objects.

```  
def obstacle_thresh(img, rgb_thresh=(160, 160, 160)):  
    color_select = np.zeros_like(img[:,:,0])  
    above_thresh = (img[:,:,0] <= rgb_thresh[0]) \  
                & (img[:,:,1] <= rgb_thresh[1]) \  
                & (img[:,:,2] <= rgb_thresh[2])  
    color_select[above_thresh] = 1  
    return color_select  

def rock_thresh(img, threshold_low=(100, 100, 20), threshold_high=(210, 210, 55)):  
    color_select = np.zeros_like(img[:, :, 0])  
    above_thresh = (img[:,:,0] > threshold_low[0]) & (img[:,:,0] < threshold_high[0])  \  
                   & (img[:,:,1] > threshold_low[1]) & (img[:,:,1] < threshold_high[1]) \  
                   & (img[:,:,2] > threshold_low[2]) & (img[:,:,2] < threshold_high[2])  
    color_select[above_thresh] = 1  
    return color_select  
```

#### 2. Populate the `process_image()` function with the appropriate analysis steps to map pixels identifying navigable terrain, obstacles and rock samples into a worldmap.  Run `process_image()` on your test data using the `moviepy` functions provided to create video output of your result.

1. Use `perspect_transform()` function to transform img into image warped based on the source and destination points.  

2. Use the color selection functions mentioned above to identify navigable terrain, rock samples and obstacles.  

```  
threshed_terrain = color_thresh(warped)  
threshed_obstacle = obstacle_thresh(warped)  
threshed_rocks = rock_thresh(warped)  
```
3. Use `rover_coords` function, which consists of converting to rover-centric coordinates and then transforming to world map coordinates.  

```  
terrain_x_pix, terrain_y_pix = rover_coords(threshed_terrain)  
obstacles_x_pix, obstacles_y_pix = rover_coords(threshed_obstacle)  
rocks_x_pix, rocks_y_pix = rover_coords(threshed_rocks)  
```

4. Use `pix_to_world` function to convert rover-centric pixel values to world coords.  

```  
terrain_x_world, terrain_y_world = pix_to_world(terrain_x_pix, terrain_y_pix, rover_x_pos, rover_y_pos, data.yaw, data.worldmap.shape[0], scale)  
obstacles_x_world, obstacles_y_world = pix_to_world(obstacles_x_pix, obstacles_y_pix, rover_x_pos, rover_y_pos, data.yaw, data.worldmap.shape[0], scale)  
rock_x_world, rock_y_world = pix_to_world(rocks_x_pix, rocks_y_pix, rover_x_pos, rover_y_pos, data.yaw, data.worldmap.shape[0], scale)  
```

5. Color the position in the world map with different colors for navigable terrain, obstacles and rock samples  

```  
data.worldmap[obstacles_y_world, obstacles_x_world, 0] += 1  
data.worldmap[rock_y_world, rock_x_world, 1] += 1  
data.worldmap[terrain_y_world, terrain_x_world, 2] += 1  
```


### Autonomous Navigation and Mapping

#### 1. Fill in the `perception_step()` (at the bottom of the `perception.py` script) and `decision_step()` (in `decision.py`) functions in the autonomous mapping scripts and an explanation is provided in the writeup of how and why these functions were modified as they were.  

**`perception_step()`**

perception_step() function is almost same as the process_image() function above. Just change all entries to be class Rover related. For example,

```  
Rover.vision_image[:,:,0] = threshed_obstacle * 255
Rover.vision_image[:,:,1] = threshed_rocks * 255
Rover.vision_image[:,:,2] = threshed_terrain * 255
```  

**`decision_step()`**  

I modified the Udacity prepared `decision_step()`. In autonomous mode, I was wondering about the "stuck" and "looping". So I added the `stuck` and `looping` mode in my code as following.  

```  
elif Rover.mode == 'stuck':  
        print('STUCK')  
        Rover.brake = 0  
        Rover.throttle = 0  
        Rover.steer = -15  
        Rover.mode = 'forward'  

elif Rover.mode == 'looping':  
        print('LOOPING')  
        Rover.count = 0  
        Rover.throttle = 0  
        Rover.steer = -15  
        Rover.brake = 0  
        Rover.count += 1  
        if Rover.count > 50:  
            Rover.mode = 'forward'  
            Rover.count = 0  
```  

Finally, I added the picking-up part in my code to improve the sample picking process.  

```  
if Rover.picking_up:
      Rover.throttle = 0

  elif Rover.near_sample and not Rover.picking_up:
      if Rover.vel == 0:
          Rover.brake = 0
          Rover.send_pickup = True
      else:
          Rover.throttle = 0
          Rover.brake = Rover.brake_set

  elif Rover.rock_angles is not None and len(Rover.rock_angles) > 1:
      Rover.throttle = 0.05
      Rover.steer = np.clip(np.mean(Rover.rock_angles * 180 / np.pi), -15, 15)
```  

I repeated the implementation and checking process and finally got the better results.  

#### 2. Launching in autonomous mode your rover can navigate and map autonomously.  Explain your results and how you might improve them in your writeup.  

**Note: running the simulator with different choices of resolution and graphics quality may produce different results, particularly on different machines!  Make a note of your simulator settings (resolution and graphics quality set on launch) and frames per second (FPS output to terminal by `drive_rover.py`) in your writeup when you submit the project so your reviewer can reproduce your results.**

In autonomous mode, my Rover actually works pretty well and succeeded to be able to find and pick up the rocks smoothly. But I still have two problems in my Rover.  

1. Rover couldn't avoid small obstacles  
2. Rover couldn't prioritize the route which haven't been yet.  

To solve these problems, I need to use the map information more and obstacle information in my `decision.py`.
