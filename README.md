# Secret Message Project
*This was a project developed with the help of GitHub Copilot, it is a small script that searches for table content in a Google Docs file and prints it out in a specific way.*  

## Message Encoding
The messages are stored in a somewhat unusual way. The script expects to find a table with x-values, y-values, and Unicode characters. These characters are printed out according to their grid value (with 0,0 being bottom left, positive x being right, and positive y being up).  This allows characters to be printed to essentially draw ASCII art (but using Unicode characters) that can communicate a message.

Examples can be found in the two `.txt` files in this repository.
