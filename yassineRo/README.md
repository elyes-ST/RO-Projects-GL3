# Transport Network Optimizer

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green.svg)](https://pypi.org/project/PyQt5/)

A modern PyQt5 application for optimizing transportation network design using mathematical optimization.

## Features

- **Interactive Network Design**: Create and modify transportation networks with nodes and routes
- **Real-time Visualization**: Dynamic network visualization with matplotlib
- **Optimization Engine**: Powered by Gurobi for optimal network design
- **Modern UI**: Clean, dark-themed interface with CRUD operations
- **Data Management**: Add, edit, and delete network components

## Installation

1. Clone the repository:
```bash
git clone https://github.com/YassWorks/OR-labs.git
cd OR-labs
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python main.py
```

1. **Define Network Nodes**: Add warehouses (supply) and customers (demand)
2. **Configure Routes**: Set up possible transportation routes with costs and capacities
3. **Optimize**: Click "Optimize Network" to find the optimal network design
4. **View Results**: Analyze the optimized network and cost breakdown

## Requirements

- Python 3.8+
- PyQt5
- Gurobi
- NetworkX
- Matplotlib
- NumPy
