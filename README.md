# MLS Player Analytics & Optimization

This repository contains data analytics notebooks for Major League Soccer (MLS) player performance and salary cap optimization, powered by the **American Soccer Analysis (ASA) API** (using the `itscalledsoccer` library) and the **MLS Players Association (MLSPA)** salary guides.

---

## Workspace Notebooks

### 1. [Moneyball Salary Cap Optimizer](file:///Users/yaniss/Documents/personal/projects/football/moneyball_optimizer.ipynb)
This notebook models roster selection as an **Integer Linear Programming (ILP)** problem (a variation of the Knapsack Problem).
*   **Goal:** Construct the highest-performing starting XI that fits under a specified salary cap (default: $5,000,000) for a given formation (default: 4-3-3).
*   **Performance Metric:** Maximizes the team's combined **Goals Added (g+)**—ASA's comprehensive value-metric measuring pass, dribble, defensive, and shot-stopping actions.
*   **Visualizations:** Generates scatter plots highlighting the selected squad of "bargains" on the overall league salary vs. performance landscape.

### 2. [Young Rookies Playtime Analysis](file:///Users/yaniss/Documents/personal/projects/football/young_rookies_analysis.ipynb)
This notebook tracks the impact of young, incoming talent in MLS.
*   **Goal:** Filter and rank players who debuted in MLS in **2024 or 2025** and were **under 23 years old** at the time of their debut.
*   **Performance Metric:** Ranked by total minutes played during the **2025 season only**.
*   **Visualizations:**
    1.  **Playtime by Position:** A bar chart showcasing which positions log the most rookie minutes.
    2.  **Cohort & Age Profile:** A bar chart showing signing years and annotating debut age and current 2025 age.
    3.  **Interactive Distribution Plot:** An interactive **Plotly** scatter plot showing all rookies (Age vs. Playtime). Hovering over any data point displays the player's name, debut details, and nationality.

---

## Installation & Setup

A virtual environment (`.venv`) is already configured in the project directory.

### 1. Activate the Virtual Environment
Activate the environment in your terminal:
```bash
source .venv/bin/activate
```

### 2. Dependencies
All required libraries are pre-installed in the virtual environment. They include:
*   `pandas` (Data manipulation)
*   `itscalledsoccer` (ASA API client)
*   `pulp` (Optimization engine)
*   `matplotlib` & `seaborn` (Static plotting)
*   `plotly` (Interactive charts)
*   `notebook` (Jupyter environment)

---

## How to Run

1.  Open the project folder in your IDE (e.g., VS Code).
2.  Open either [moneyball_optimizer.ipynb](file:///Users/yaniss/Documents/personal/projects/football/moneyball_optimizer.ipynb) or [young_rookies_analysis.ipynb](file:///Users/yaniss/Documents/personal/projects/football/young_rookies_analysis.ipynb).
3.  Ensure the notebook kernel is set to the project's virtual environment (`.venv`).
4.  Click **Run All** to fetch the latest live data and execute the visual workflows.
