# Titan Campus Algorithmic Assistant (TCAA)

**Course:** CPSC 335
**Project:** Comprehensive Algorithmic Assistant GUI

## Overview
The Titan Campus Algorithmic Assistant is a fully interactive Python application designed to demonstrate the practical application of advanced algorithms and data structures. Built with a custom Tkinter UI, the application strictly adheres to zero-dependency algorithm implementations (no NetworkX or Pandas) and features four core modules: Campus Navigator, Study Planner, Notes Search Engine, and Algorithm Info.

## Core Features

### 1. Interactive Campus Navigator
* **Visual Map Interface:** Users can view a high-contrast Cal State Fullerton map with selectable building nodes. Edge weights represent estimated walking times for algorithm demonstration.
* **Breadth-First Search (BFS):** Finds the destination by exploring all neighbor nodes at the present depth before moving further (calculates fewest hops).
* **Depth-First Search (DFS):** Explores as far as possible along each branch before backtracking (demonstrates graph connectivity; not guaranteed to find the shortest route).
* **Dijkstra's Algorithm:** Computes the guaranteed shortest path based on weighted distances, implemented strictly using a Python `heapq` priority queue.
* **Prim's MST:** Calculates the Minimum Spanning Tree to connect all campus buildings with the lowest total weight.

### 2. Study Planner Optimization
* **Greedy Task Scheduling:** Rapidly schedules study tasks based on a highest-value-first greedy heuristic.
* **Dynamic Programming (0/1 Knapsack):** Calculates the mathematically optimal study schedule to maximize value within a strict time constraint.

### 3. Notes Search Engine
* **Multi-Format Parsing:** Extracts text from uploaded `.txt`, `.pdf`, and `.docx` files.
* **Advanced String Matching:** Allows users to search for keywords using Naive, Rabin-Karp, and Knuth-Morris-Pratt (KMP) algorithms, complete with execution time comparisons.

### 4. Data Processing & Validation
* **Pure Python Architecture:** All data structures (graphs, adjacency lists, heaps) are built from scratch using standard Python.
* **Validation Checks:** Robust error handling prevents application crashes from invalid inputs or missing files.

## Project Architecture
The project strictly separates frontend UI components from backend algorithmic logic:
* `/algorithms/`: Pure Python implementations of BFS, DFS, Dijkstra, Prim's, DP, and String Matching.
* `/ui/`: Modular Tkinter frames handling layout, state, and canvas drawing.
* `/assets/`: Static resources including the CSUF campus map and test documents.

## Installation & Setup
This project requires Python 3.x. 

1. **Clone or extract the repository.**
2. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt