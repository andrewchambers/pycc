set -e
cat ./backend/x86/x86.md |  python ./mdcompiler/mdcompiler.py > ./backend/x86/x86md.py
