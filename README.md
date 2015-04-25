FILE:    mine
PURPOSE: Any-dimensional minesweeper
AUTHOR:  Geoffrey Card
DATE:    2015-03-23 - 2015-04-25
VERSION: 1.0.1
TODO:    split matrices before solving
        combine checkVictory and checkFailure
        clean up and comment
NOTES:   graphics are poor

Game becomes dramatically more difficult per dimension, for both humans and machines.
Assuming a field with n dimensions.
Assuming each dimension has length m greater than or equal to 5:
Assuming player's first click is a non-edge:

Total number of cells = m^n
Total number of adjacent cells to any non-edge: 3^n-1
 
To solve the simplest possible opening (after first click), an automatic solver must solve a matrix of 3^n-1 equations and 5^n-3^n unknowns.

As a matrix, it would be a sparse matrix with 3^n-1 rows and 5^n-3^n columns.
For each row, there would be fewer than 3^n-1 elements.
That means fewer than (3^n-1)^2 elements out of (3^n-1)*(5^n-3^n) elements total.
Since each unknown can only be a mine or not, for the number of unknowns k, there are 2^k potential solutions.

 n | m^n (m=5) | 3^n-1 | 5^n-3^n | (3^n-1)^2 | (3^n-1)x(5^n-3^n) | 2^(5^n-3^n) |
---+-----------+-------+---------+-----------+-------------------+-------------+
 1 |         5 |     2 |       2 |         4 |                 4 |           4 |
 2 |        25 |     8 |      16 |        64 |               128 |       65536 |
 3 |       125 |    26 |      98 |       676 |              2548 |     3x10^29 |
 4 |       625 |    80 |     544 |      6400 |             43520 |    6x10^163 |
 5 |      3125 |   242 |    2882 |     58564 |            697444 |    4x10^867 |
 6 |     15625 |   728 |   14896 |    529984 |          10844288 |   1x10^4484 |
 7 |     78125 |  2186 |   75938 |   4778596 |         166000468 |  4x10^22859 |

Solving as a matrix:
Using brute force, the number of solutions would be proportional to at least the number of solutions, > O(2^(5^n)).
Using optimized algorithms should take time proportional to the number of non-zero elements, > O(9^n).
Using unoptimized algorithms sould take time proportional to the total number of elements, > O(15^n).
I don't know the complexity of my algorithm, I use a trick with the binary nature of the solutions and sparsity of the matrix, even that is slow.

There are tricks and certain simpified and trivial cases (e.g. all mines), but that's the simplest opening possible for a non-edge.
