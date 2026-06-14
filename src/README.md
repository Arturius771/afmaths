# Commands

## Format files

`clang-format -i *.cpp`

## Compile to library code

`clang++ -c file.cpp`

## Compile to an executable

`clang++ file.cpp -o file.o`
or to put in a directory
`clang++ file.cpp -o ../build/file.o`

## Execute file

`./file`

## Inspect assembly

`objdump -d file`
