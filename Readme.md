# version_bridge


This package provides a simple method to call python functions written in a different python version.

Right now it can only handle basic python types and no custom classes instances.
In this case you would have to write a translator script in the old python version and call this alternative function.

If there is demand for such functionality feel free to create an issue.

## Why?

Sometimes upgrading an old codebase to python 3 is infeasable due to a lot of dependencies that can not be updated. If in this case only a simple function output is needed, which does not carry class instances, this package can be used to directly call this function.

## Usage

For globally installed packages use it as follows.

Suppose you want to call 
```python
def old_function(input):
    print "I only work with python 2.7"
    return {'result': 'Your parameter was ' + str(input)}
```
located in package `old_python`.

```python
import version_bridge

# create a connection to your package 
# Also specify the python version you want to use
old_module = version_bridge.Bridge(version="2.7",module="old_python")

# call your function as usual
print(old_module.old_function(19))

# Result:
#
# I only work with python 2.7
# {'result': 'Your parameter was 19'}
```
Also `stderr` and `stdout` will be redirected to the current process.

If the code you want to use lies in a relative path to your current script, use the following:

```python
import version_bridge as vb

old_module = vb.Bridge(version="2.7",module="old_python", path="../path/relative/to/script")

print(old_module.old_function(19))

# Result:
#
# I only work with python 2.7
# {'result': 'Your parameter was 19'}
```