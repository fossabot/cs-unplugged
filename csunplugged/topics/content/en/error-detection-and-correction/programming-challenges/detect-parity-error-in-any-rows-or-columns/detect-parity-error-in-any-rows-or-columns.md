# Detect parity error in rows and columns (any length)

## Requirement:

Write a program that asks the user to enter the number of rows for a parity
trick followed by the rows (one row at a time) as the input and says
which row and column has a parity error as the output.
We are assuming that only one card has been flipped over (i.e. there is only
one row and one column with error).
You will need to use a list to store the rows for this challenge.

## Testing examples:

Your program should display the outputs shown in these panels for the given
inputs provided:

| Input   | Output |
| ------- | ------ |
| How many rows would you like to enter? **6**<br>Enter 6 cards for row 1: **WBBWWW**<br>Enter 6 cards for row 2: **BBWBWB**<br>Enter 6 cards for row 3: **BWWWBW**<br>Enter 6 cards for row 4: **BBBBBB**<br>Enter 6 cards for row 5: **WBBWWB**<br>Enter 6 cards for row 6: **BBBWBB** | There is a parity error in row 5 and column 2. |
| How many rows would you like to enter? **4**<br>Enter 4 cards for row 1: **BWWB**<br>Enter 4 cards for row 2: **BBBB**<br>Enter 4 cards for row 3: **WBBB**<br>Enter 4 cards for row 4: **WBWB** | There is a parity error in row 3 and column 2. |
