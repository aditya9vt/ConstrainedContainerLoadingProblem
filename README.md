# Constrained Container Loading Problem
The objective of this project is to present a heuristic algorithm for solving a container loading problem with practical constraints based on a real industrial application. The algorithm is built in collaboration with Jonah Dwyer, Director Of Business Analytics at Frontline Carrier Systems Inc.

This problem consists of constraints such as container weight restrictions, axle weight restrictions, box weight limit, box covered surface area limit, and grouping of orders while designing the loading plan. The loading sequence is based on the rules that are designed by utilizing the dimensions and weight of the boxes in the set. In the end, the algorithm provides all the generated solutions and the pictorial representation of the solution with maximum utilization of the container. Once all the solutions are generated user can re-run the same code with a different set of inputs to obtain the graphical representation of any other generated solution. 

# Steps to run the algorithm:
1. Clone the repository to obtain the required input and python files
2. Prepare the excel file: CLPData_Parameters.xlsx
3. Open script file (in an IDE, e.g. SPYDER): _0_ScriptFile
4. Hit F5, and the algorithm will ask for a user-input
   - Enter '1' to run the algorithm.   
5. The algorithm will create a 'SolutionsGroupAgg' folder inside your main folder in which the repository is cloned.
6. The 'SolutionsGroupAgg' folders consists of:
   - Summary File: All possible solutions generated and their respective volume loaded
   - Detailed Result File: It consists of the loading sequence and position of each cargo
   - Pictorial representation of the best solution from three angles.
7. If you would like to see the pictorial representation of any other solution, hit F5 once again
   - this time enter '0' then the algorithm will ask for another input. Enter the solution number for which you want to see the loading pattern
