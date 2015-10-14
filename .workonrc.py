import os
import dshell

shell = dshell.create()
shell.prepend('PYTHONPATH', os.getcwd())
