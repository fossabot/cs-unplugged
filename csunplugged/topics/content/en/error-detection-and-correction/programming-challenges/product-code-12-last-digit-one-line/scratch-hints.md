-   For the 11 digits entered, you need to add up 1st, 3rd, 5th and so on
    digits and store the result in a variable called total 1.
    Then add up 2nd, 4th, 6th and so on digits and store the result in
    variable called total 2.
    The last digit (check digit) is then calculated by subtracting the sum
    of total 1 multiplied by 3 and total 2 from 0 mod 10.

-   You can access a letter (or a digit) at a specified position in a string
    (or number) by using the `scratch:letter () of []` block under “Operators”.
    For example: `scratch:letter (4) of [18392819202910] //9`
