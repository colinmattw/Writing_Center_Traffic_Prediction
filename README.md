# Writing_Center_Traffic_Prediction
Program made for the Marian University writing center which uses frequency and importance of homework assignments to predict use of writing center resources.
---------------------------------------------------
Created by Colim M Wareham
---------------------------------------------------
The python program first interfaces with Marian University's Canvas API, where it accesses assignment, quiz, and exam data from the participating professors.
It then models the impact that a single assignment has on the utilization of the writing center's resources. This increases exponentially as the due date of the assignment approaches, and is 0 after the due date has passed.
It does this for every assignment, quiz, and exam, and stacks all the distributions based on the due dates to get the aggregate function that approximates the foottraffic of the writing center in advance.
It is more accurate than predictions from historical data alone because it takes into consideration real-time changes in course material and movement of due dates.
This program was used to great success in the Marian University Writing center and would have been developed further if the management had not changed as well as myself moving on to other projects.

The python program has a side effect of exporting all the assignment, quiz, and exam information to a CSV file, where our Writing Center staff can easily see the assignments for the whole semester, along with who the professor is, how much the assignment is worth, the assignment description, and its due date.

Participation in this program was done on a professor-by-professor basis, as some professors preferred to not have their data aggregated in such a way. However, we only had one professor opt out of this program.
