# cmpsc-202-Team-B
Kallan Fuchs, 
Isaac Michalek, 
Issei Hasegawa

## Project 3: Navigating the Sea
You are charting a newly discovered, biologically dense ocean trench represented by an nm grid of vertical depth zones and horizontal coordinates. Each coordinate (i,j) has a surveyed "biomass density" score B(i,j), which can be positive (rich coral) or negative (hazardous hydrothermal vents that damage sensors). An autonomous submersible drops from the surface (row 1) and must navigate to the ocean floor (row n). To conserve battery, the submersible can only move downward. From zone (i,j), it can only move to (i+1,j-1) (down-left), (i+1,j) (straight down), or (i+1,j+1) (down-right). The submersible can start at any horizontal coordinate on the surface and end at any horizontal coordinate on the floor. Determine the path that maximizes the total accumulated biomass density score.