
# About
This repository contains the source code of Blender. Blender is a practical simulation framework for Bluetooth Low Energy (BLE) neighbor discovery. A demo application of Blender-as-a-service can be find at [AlgoSpace](https://algospace.top/algorithm/blender_as_a_service/v1.0/).

Please cite the papers as follows (or use this [bibtex record](./bibtex.txt)).

- Yukuan Ding, Tong Li, Jiaxin Liang, Dan Wang. [Blender: Toward Practical Simulation Framework for BLE Neighbor Discovery](./paper/blender_mswim22.pdf). ACM International Conference on Mobile, Analysis and Simulation of Wireless and Mobile Systems (MSWiM), pp. 103-110, 2022. 
- Tong Li, Jiaxin Liang, Yukuan Ding, Kai Zheng, Xu Zhang, Ke Xu. [On Design and Performance of Offline Finding Network](./paper/elasticast_infocom23.pdf). IEEE International Conference on Computer Communications (INFOCOM), pp. 1-10, 2023.


## Directory Structure

### `algo`
This contains the algorithm(s) utilized for accelerating Blender's simulation process.

### `simulator`
The implementation of different simulation workflows are listed here, where the specific characteristics of each are embeded in the comments. 

### `utils`
This contains some debugging and analyzing tools.

## Setup

### Python-Based Simulator
The python implementation is written under python3.8 with numpy 1.20.1. 

## Workflow
A sample usage of the simulator is presented in playground.py.

The input parameters are explained as follows:

- adv_interval: The broadcaster's broadcast interval, an integer ranges from 20 to 10240 ms.
- scan_interval: The scanner's scan interval, an integer ranges from 20 to 10240 ms.
- scan_window: The scanner's scan window, an integer ranges from 20 to 10240 ms. scan_window must not exceed scan_interval.
- end_time: The upper bound of running time for each simulation case, an integer ranges from 1000 to 60000 ms. This speeds up the simulation when an extra large discovery latency occurs.
- loss_rate: The loss ratio of a beacon message, an integer ranges from 0 to 99. For example, 20 refers to loss_rate=20%.
