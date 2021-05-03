# Python Brainfuck-IDE

![image](https://user-images.githubusercontent.com/77941087/116938829-a1258180-ac6b-11eb-9637-a5606492887a.png)\
A dummy Brainfuck program in my editor just to f\*ck your brain

## What is Brainfuck?

### TL;DR:
Brainfuck is the best language to f\*ck your brain. It requires a lot of logic and math, and if you don't pay enough attention, it can be completely nonsense.

### From [Wikipedia](https://en.wikipedia.org/wiki/Brainfuck):

In 1992, Urban Müller, a Swiss physics student, took over a small online archive for Amiga software. The archive grew more popular, and was soon mirrored around the world. Today, it is the world's largest Amiga archive, known as Aminet.

Müller designed Brainfuck with the goal of implementing it with the smallest possible compiler, inspired by the 1024-byte compiler for the FALSE programming language. Müller's original compiler was implemented in machine language and compiled to a binary with a size of 296 bytes (yes, mine is much larger). He uploaded the first Brainfuck compiler to Aminet in 1993. The program came with a "Readme" file, which briefly described the language, and challenged the reader "Who can program anything useful with it? :)". Müller also included an interpreter and some quite elaborate examples. A second version of the compiler used only 240 bytes.

As Aminet grew, the compiler became popular among the Amiga community, and in time it was implemented for other platforms.

#### Language design

The language consists of eight commands, listed below. A brainfuck program is a sequence of these commands, possibly interspersed with other characters (which are ignored). The commands are executed sequentially, with some exceptions: an instruction pointer begins at the first command, and each command it points to is executed, after which it normally moves forward to the next command. The program terminates when the instruction pointer moves past the last command.

The brainfuck language uses a simple machine model consisting of the program and instruction pointer, as well as a one-dimensional array of at least 30,000 byte cells initialized to zero; a movable data pointer (initialized to point to the leftmost byte of the array); and two streams of bytes for input and output (most often connected to a keyboard and a monitor respectively, and using the ASCII character encoding).

Commands
The eight language commands each consist of a single character:

Character | Meaning
-|-
\> | increment the data pointer (to point to the next cell to the right).
\< | decrement the data pointer (to point to the next cell to the left).
\+ | increment (increase by one) the byte at the data pointer.
\- | decrement (decrease by one) the byte at the data pointer.
\. | output the byte at the data pointer.
\, | accept one byte of input, storing its value in the byte at the data pointer.
\[ | if the byte at the data pointer is zero, then instead of moving the instruction pointer forward to the next command, jump it forward to the command after the matching ] command.
\] | if the byte at the data pointer is nonzero, then instead of moving the instruction pointer forward to the next command, jump it back to the command after the matching \[ command.


### Bugs
I know the IDE is far from good. Current bugs:
- On-close save prompts
- Azure theme on Linux filedialog (looks awful)
- Syntax highlighting is quite slow (I don't know if it could be faster)

And I would like to add these features
- Auto-update with GitHub versions (just for fun)
- Select editor font
- Prompt on outer modification
- Tabs
- Search 😆
- Context menu for copy, paste, clear output, etc.

If you can fix these, feel free to open a PR!
