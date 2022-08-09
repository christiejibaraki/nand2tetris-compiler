# nand2tetris-compiler
Jack Compiler: Project 10 &amp; 11

- Project 10: Syntax Analysis: Tokenization and Parsing
- Project 11: Code Generation

The main module runs the first "half" of the compiler, which tokenizes and parses a Jack program, 
assigning tags to each token, which reflect the syntactic structure of the program. 
The tokens and their tags are output to a set of XML files.

Input should be a directory containing one more `.jack` files.
The output will be written to a file with the name *`<filename>T.jack`* and extension `.xml`.

- Input: `<directory>` containing one or more files `<filename>.jack`
- Output: `<directory>/<filename>T.asm`

### To run the module:
Specify the location of `main.py` and the input directory, e.g.:

`python3 IbarakiChristieProject10/src/main.py <directory>`

### Known issues:
