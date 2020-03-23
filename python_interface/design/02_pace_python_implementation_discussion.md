# Matlab and Python: Implementation details
**2020-03-23**


# Scope

This document describes the implementation of topics summarised by the [high level Python interface document](01_pace_python_high_level_discussion.md).

# <a name="compiled_matlab"></a> The Matlab Compiler Toolbox

To distribute Matlab code to users without a Matlab license, the **Matlab Compiler** toolbox has to be used.
There are two main Matlab functions to compile code to a library or executable; a low level compiler, `mcc` and a higher level `deploytool`.
`deploytool` is primarily a GUI application which also allows us to package an installer and bundle the (1GB) **MCR** with the Python version of Horace.
`mcc` is a command-line application and does the actual "compilation" (encrypts and packs specified `m`-files into a `ctf` archive).
This may be invoked within a Matlab session, or as a separate executable, making it suitable to be used in build systems.
[An example CMake](https://github.com/mducle/hugo/blob/master/src/CMakeLists.txt#L49) file shows how this could be implemented.
`mcc` only parses `m` and `mex` files, so, because the `Horace` and `Herbert` distributions contains many non-such files the build process copies the `m`/`mex` files to a new folder structure.
`mcc` gives an error on zero-length files and on the markup tags used by `docify` so these are removed from the temporary folder using a shell script.
A single `m`- or `mex`-file has to be specified as the target of the compilation, which is `pyhorace_init.m` in our case.
The `-a` switch then adds an `m`- or `mex`-file or a folder to the `ctf`, and may be specified repeatedly. 
Each `m`- or `mex`-file specified by an `-a` switch is available to be called directly by Python.
`m`- or `mex`-files contained within a folder specified by `-a` are included in the `ctf` archive but cannot be called directly by Python.
For `pyHorace`, two `m`-files which internally uses `feval` are specified by the `-a` switch (`call.m` and `call2.m`) to call the actual Horace/Herbert routines which are included only as folders.
`call.m` is to call functions directly, whilst `call2.m` calls methods of objects.
There is also a `thinwrapper` class to wrap old-style objects so that they are not converted to Python `dict`s.
The compilation time is approximately 10 minutes.

## Example syntax

The default Python syntax to interact with the compiled Matlab library is quite convoluted.
[For example](https://github.com/mducle/hugo/blob/master/example.py), to make some cuts and plot them:

```python
from pyHorace import horace
from matlab import double as md
m = horace.initialize()
m.call('pyhorace_init', nargout=0)

proj = m.call('projaxes', [md([-0.5, 1, 0]), md([0, 0, 1]), 'type', 'rrr'])
w1 = m.call('cut_sqw', ['ei30_10K.sqw', proj, md([0.1, 0.02, 0.5]), md([1.5, 2.5]), md([0.4, 0.5]), md([3, 0.5, 20])])
w2 = m.call2('cut', w1, [md([0.1, 0.5]), md([3, 0.5, 20])])
hf = m.call2('plot', w1, []) 
m.call('uiwait', [hf])
```


# <a name="user_interface"></a> User Interface

To make the syntax more "Pythonic", we use code developed for [`pySpinW`](https://github.com/SpinW/pySpinW) to wrap `call` and `call2` in a Python class which also handles the automatic data type conversions.
We overload the [`__getattr__()`](https://github.com/mducle/hugo/blob/master/pyHorace/Matlab.py#L40) method of this class to allow the dot (`.`) member notation to call arbitrary Matlab functions or methods.
This allows syntax such as:

```python
from pyHorace import Matlab
m = Matlab()
proj = m.projaxes([ -0.5, 1, 0], [0, 0, 1], 'type', 'rrr')
w1 = m.cut_sqw('ei30_10K.sqw', proj, [0.1, 0.02, 0.5], [1.5, 2.5], [0.4, 0.5], [3, 0.5, 20])
w2 = w1.cut([0.1, 0.5], [3, 0.5, 20])  #  or w2 = m.cut(w1, [0.1, 0.5], [3, 0.5, 20])
hf = w1.plot()                         #  or hf = m.plot(w1)
m.uiwait(hf)
```

In addition, the [class wrappers](https://github.com/mducle/hugo/blob/master/pyHorace/MatlabProxyObject.py#L51) also use the Matlab-side `properties`, `subsref` and `substruct` methods to allow Python-side views of properties of Matlab objects.
This means that it is possible inspect the header of the `sqw` object with `w1.main_header`, or extract the data with `w1.data.s` etc. (as `numpy` arrays) from Python.
The wrappers [encode](https://github.com/mducle/hugo/blob/master/pyHorace/DataTypes.py#L20) input arguments to function or method calls from Python to Matlab and [vice versa](https://github.com/mducle/hugo/blob/master/pyHorace/DataTypes.py#L62).


# <a name="type_conversions"></a> Type Conversions

These encodings and decodings try to minimize data copying between Matlab and Python.
However, some data copying is unavoidable because internally, Matlab *always* creates a data copy when converting from a Matlab (`mxArray` type) array to a Python (`buffer`) array.
That is, Matlab exports data to Python as a (Python) `array.array` object (wrapped in a `matlab.<type>` class) which supports the Python `buffer` protocol.
The `buffer` protocol is Python's way of allowing its object to directly access (in a controlled manner) a raw memory location.
However, the memory location pointed to by the Matlab created `buffer` in Python is *not* the memory pointed to by the original `mxArray` in Matlab.
(See the [appendix](#app_memcopy) for code to verify this.)

There is no official (documented) way of circumventing this data copy.
This is probably for memory safety reasons: both Matlab and Python rely on reference counting to determine when to delete objects and free their associated memory.
However, it is difficult to mesh the two systems, so Matlab seems to have opted to keep the two reference counts separate by *not* sharing data between Matlab and Python.

It *may* be possible to circumvent the data copying by writing `mex` files using the Matlab C++ API.
However, to do so safely would probably involve setting up our own reference-counting system to ensure that neither Matlab nor Python deletes memory pointed by each others variables.
This system would then have to mesh with both Python's and Matlab's systems.
The details are discussed below in the section on [using `mex` files for type conversion](#mex_wrapping).

## Wrapper implementation

In any case, the actual documented code example for handling Matlab data in Python is even more inefficient.
Matlab functions called from Python accept only wrapped `matlab.<type>` objects as input, and the default constructors for numeric arrays of these types only take Python `list`s as input.
This default constructors then *copies* the contents of the list to an `array.array` and wraps this in a `matlab.<type>` class with addition information such as type, dimensions and strides.
If we were to pass a `numpy` array (which is already a type which follows the `buffer` protocol and so is convertible to `array.array` without copying) we need to convert it to a `list` which involves an additional data copy.
Thus the default method to pass data from Python to Matlab requires *three* data copies.
The [prototype implementation](https://github.com/mducle/hugo/blob/master/pyHorace/TypeWrappers.py#L25) avoids the two unecessary copies by constructing a `matlab.<type>` object directly wrapping the `numpy` array.
It can only do this for `numpy` arrays which are stored in memory in a column-major (Fortran-style) layout, however, because Matlab only supports such a layout.
(Or at least its Python interface only supports - there are indications in the code that the `mxArray` *can* support a row-major layout).
For row-major (C-style) `numpy` arrays, the prototype implementation is forced to perform a data copy.

## Complex-valued arrays

Likewise, for complex-valued arrays, a data copy is required because the Matlab-Python API requires complex arrays to be stored as separate real and imaginery parts, in different memory locations.
This contrasts with the behaviour of `numpy` which stores complex arrays in an interleaved memory format where each element contains both real and imaginery components.
This also, ironically, contrasts with the internal behaviour of Matlab, which since R2018a has *also* used an interleaved data format for complex arrays.
(The Matlab-Python API thus forces two completely unecessary data copies, probably for backwards compatibility reasons with older versions of Matlab which stored the real and imaginery parts separately).

## Other considerations

In the reverse direction, data exported from Matlab to Python in the `matlab.<type>` classes already support the Python `buffer` protocol so can be directly wrapped in a `numpy` array without additional copying.
(One data copy has already been made by the Matlab-Python library internally).
This wrapping is done in the [`TypeWrappers` class](https://github.com/mducle/hugo/blob/master/pyHorace/TypeWrappers.py#L56) of the prototype implementation.

Finally most Matlab functions expect their input to be floating point numbers, whereas the Matlab-Python library automatically converts Python `int` into `int` etc. (and the default numeric format in Python is an `int`).
The `pyHorace` wrapper thus [explicitly converts all numerical values to `double`](https://github.com/mducle/hugo/blob/master/pyHorace/DataTypes.py#L30). 
This consciously breaks the few Matlab (mostly Java) functions that expect `int` in favour of the many which expect `float`.
Of course, this also means making an additional copy of the array in most cases, since it is not possible to convert from `int` to `float` without changing the array memory.
It may be possible to perform this conversion *in-place* using a compiled C module if the data types are the same widths (e.g. `int` and single-precision floats, or `long` and double-precision).
Plain Python code, however, does not allow such an in-place conversion, hence the prototype implementation requires a data copy.

## <a name="mex_wrapping"></a> Type Conversions in a `mex` file

A `mex` file compiled using the `matlab::data` C++ API can access the raw Matlab array in memory (including interleaved complex arrays).
It can read the memory location of a Matlab array using [`TypedArray` iterators](https://uk.mathworks.com/help/matlab/apiref/matlab.data.typedarray.html#bvo9gta-1).
It can also create a Matlab `mxArray` which wraps around a memory pointer using the [`createArrayFromBuffer` method](https://uk.mathworks.com/help/matlab/apiref/matlab.data.arrayfactory.html#bvmdq7t-1).
(Details are given in [this Matlab Central answer](https://uk.mathworks.com/matlabcentral/answers/436916-how-to-access-raw-data-via-the-mex-c-api).)
On the Python side, there are documented methods for [getting](https://docs.scipy.org/doc/numpy/reference/c-api.types-and-structures.html#c.PyArrayObject.data) and [setting](https://docs.scipy.org/doc/numpy/reference/c-api.array.html#c.PyArray_NewFromDescr) the raw data from/to a `numpy` array without copying.

The complication is that Matlab forbids `mex` files from returning non-Matlab data types, hence this cannot be used to directly export data without copying from Matlab to Python.
Exporting data without copying from Python to Matlab is also complicated by the Matlab-Python library which as noted above always creates a copy.
Hence to do copy-less exports we need some wrappers, and also a way to ensure that the shared (linked) data is not inadvertently deleted.

For this, we may use the following strategy:

1. We create a wrapper class which contains a reference to the child-array in the exported language and a *shared-copy* of the original array (no actual memory copy is needed to create a shared copy).
2. In both Matlab and Python, as long as one array has a link to an underlying memory location, and that array is in scope, the memory location will not be freed.
3. Thus the shared-copy of the original array ensures that the memory remains valid even if the original array is deleted, as long as the wrapper object itself is not deleted.
4. The wrapper object has a destructor method which ensures that the reference to the child-array in the exported language is invalidated when it is deleted (which potentially frees the underlying memory).

As a concrete example, take the case of exporting a Matlab array to `numpy`.
We first use a `mex` file to create a `numpy` object which wraps the data-in-memory of the Matlab array, and exports this `numpy` object to a Python-side module-global `dict`.
It also creates a shared-copy of the original input array using the method described [here](https://uk.mathworks.com/matlabcentral/answers/396103-mxcreateshareddatacopy-no-longer-supported-in-r2018a).
The `mex` file then returns both the key to the `numpy` object, its address in memory, and the shared-copy which is stored in a *Matlab* wrapper (handle) object.
It is this Matlab wrapper object which is passed to Python as a `matlab.object`.
We then have additional Python wrappers which can extract the key from the Matlab wrapper object and use that to access the exported `numpy` array.
As long as the Matlab wrapper stays in scopy in *Python* (as a `matlab.object`) the underlying memory is valid and we can use the linked `numpy` array.
If manipulation in Matlab changes the `numpy` object in the dictionary such that its address (the address of the wrapper and not the data-in-memory) is different from that in the Matlab wrapper object, we delete the Matlab object.
This thus breaks the link between the Matlab and Python arrays (because an implicit copy has already happened on the Python side - e.g. through `a = a + b` or some such operation).

Exporting in the reverse direction (from Python to Matlab) is (perhaps) a bit more straightforward.
In this case, we cannot use a Python class as the wrapper because this cannot be exported to Matlab.
Rather we use a Python C API module with `mex` bindings to construct a `mxArray` using `createArrayFromBuffer` from the `numpy` object's memory.
`createArrayFromBuffer` as the option to use a (C-style) row-major memory layout, but no investigation has been done to check if this results in an implicit data copy or not.
Once this `mxArray` which wraps a `numpy` memory has been created, we export it to the `base` Matlab namespace with a random variable name using an `assignin` call.
The Python C API module also creates a shared (`memoryview`) copy of the original `numpy` array, to keep it in memory, and keeps this in a module-global `dict` with a random key.
We then have Python wrapper code which creates a Matlab handle object to store the name of the exported `base` namespace Matlab array and the key to the shared-copy.
Additional Matlab wrapper codes ensure that when they are passed the Matlab handle object wrapper from Python that this resolves to the array in the `base` namespace.
When the Matlab handle object wrapper goes out of scope or deleted it removes the share-copy's key from the module-global `dict` and deletes the `base` namespace Matlab array.

No prototype implementation of the above schemes exist at present, due to time reasons. 
Instead, a the Python function call described in the [next section](#pymatpy) implements a `mex` file which creates `numpy` array that wraps memory from a Matlab array but which only exists whilst the `mex` file executes.
The [wrapped `numpy` array](https://github.com/mducle/hugo/blob/master/src/call_python.cpp#L14) is passed to the user defined function directly, and should be only used in the called function so there should not be issues with garbage collection.


# Calling user defined functions

## <a name="pymatpy"></a> Loaded Matlab within Python calling functions on Python host.

The design for this is that whenever the `pyHorace` wrapper encounters a callable Python object (usually a function), it:

1. Stores a reference to this function in a module-global `dict` in the [`pyHorace.FunctionWrapper`](https://github.com/mducle/hugo/blob/master/pyHorace/FunctionWrapper.py) module, with a random unique key.
2. Creates a Matlab-side [`pythonFunctionWrapper`](https://github.com/mducle/hugo/blob/master/src/pythonFunctionWrapper.m) object which as its destructor will call a [`mex` function](https://github.com/mducle/hugo/blob/master/src/pythonRemoveFuncKey.cpp) to remove the function reference from the `FunctionWrapper` `dict`.
3. The `pythonFunctionWrapper` is passed to the Matlab [`call.m`](https://github.com/mducle/hugo/blob/master/src/call.m) and [`call2.m`](https://github.com/mducle/hugo/blob/master/src/call2.m) functions.
4. `call.m` / `call2.m` detects this object and replaces it with a (Matlab) anonymous function which calls [`call_python.mex`](https://github.com/mducle/hugo/blob/master/src/call_python.cpp).
5. The first argument to `call_python.mex` is the Python function key and subsequent arguments are to passed to this Python function (after being wrapped in a `numpy` class as described above).
5. The anonymous function which calls `call_python.mex` created by `call.m` / `call2.m` is then passed to the desired Matlab function (e.g. `sqw_eval`) which treats it as a normal Matlab function.
6. When it is called, `call_python.mex` then checks the `dict` in `pyHorace.FunctionWrapper` to see if the key is valid and if it is, calls the function referenced by it.
7. `call_python.mex` wraps `float`/`double` and `complex<float>`/`complex<double>` Matlab arrays in a `numpy` array wrapper before passing these to the Python function (other wrappers are possible but have not been implemented).
8. On return, `call_python.mex` copies the data in the `numpy` array (the prototype implementation assumes only a single array is returned) into a Matlab array and returns this to Matlab.

The reason to wrap the function key in a `pythonFunctionWrapper` object is to ensure that the function reference does not persist eternally in the `FunctionWrapper` `dict`, causing a memory leak.
When the `pythonFunctionWrapper` object goes out of scope, it should be deleted by Matlab, and this calls its destructor `mex` function to remove the reference from the global `dict`.

As noted previously, the `thinwrapper` used by the prototype implementation does not handle nested old-style classes, such as the `multifit_sqw` class which has a nested `sqw` object within it.
Thus the `multifit.fit()` function does not work in the prototype implementation.
However, `sqw_eval` does work, and an example is given [here](https://github.com/mducle/hugo/blob/master/sqw_eval_example.py).

## <a name="matpymat"></a> Loaded Python within Matlab calling functions on Matlab host.

Very little prototyping was done with respects to this use-case, apart from verifying that it is possible.
The [prototype code](https://github.com/mducle/hugo/blob/master/src/call_matlab.cpp) uses the mex *C* API (not C++) because the C++ API needs a reference to the Matlab engine which called the `mex` function.
Since we are compiling a *Python* module which is linked to Matlab rather than a `mex` function, we cannot easily get the reference to the Matlab engine.
The C API, on the other hand, does not need such a reference and can be used to evaluate any Matlab function.
The reason for this discrepancy is unclear (it may be that the C++ wrapper only uses a reference to the engine for syntactic convenience and does not need it, so the C API dispenses with it).
The only advantage of the C++ API compared to the C API is that the C++ API allows a `mex` file to get/set the properties of a Matlab object which the C API does not.

There may thus be a case for using a C API `mex` file to get the reference to an engine and then use a C++ API in the actual Python module.
However, how this is best done is left as work for the future.


# <a name="app_memcopy"></a> Appendix: Code demonstrating the memory copies in converting data from Matlab to Python.

First we need a mex file which will print the address of the actual memory location of the *data* (not the `mxArray` wrapper) of a particular Matlab array.
This is provided by the [`get_address.mex`](https://github.com/mducle/hugo/blob/master/src/get_address.cpp) file in the Hugo repository.
Then we can use the following Python script to get the addresses in memory of the data associated with a single array as it is created in Python, exported to Matlab and re-exported back to Python:

```python
import struct
import ctypes

from pyHorace import Matlab
m = Matlab()

# We cannot directly create a variable in the Matlab base namespace
# So we first create it in Python using the default matlab.double ctor and get its memory address
import matlab
mm = matlab.double([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
addr_py = mm._data.buffer_info()[0]
print('Original Matlab array in Python memory address is {}'.format(addr_py))

# Check that it contains the correct data (in column-major, so: [1, 4, 7, 2, 5, 8, 3, 6, 9])
data_orig = [struct.unpack('<d', ctypes.string_at(addr_py+i*8, 8))[0] for i in range(9)]
print(data_orig)

# Now we use the get_address mex file to find the address of the matrix in Matlab
addr_mat = int(m.interface.call('get_address', [mm]))
print('Matlab array memory address is {}'.format(addr_mat))

# Luckily if we assign this variable to the Matlab base workspace, it _doesn't_ make another copy
m.interface.call('assignin', ['base', 'mm_mat', mm])
m.interface.call('evalin', ['base', 'whos'], nargout=0)
addr_base = int(m.interface.call('evalin', ['base', 'get_address(mm_mat)']))
print('Matlab base workspace array memory address is {}'.format(addr_base))

# Unfortunately, if we re-export this back to Python it creates another data copy.
# We use evalin (because we cannot use assignin to export to Python) 
mm_py = m.interface.call('evalin', ['base', 'mm_mat'])
print(type(mm_py))
print(mm_py)

# The data is stored in the _data attribute as a buffer object
print(type(mm_py._data))
print(mm_py._data)
# The address of the buffer can be obtained from the buffer_info property
# The first element is the address, the second is the length
buf_info = mm_py._data.buffer_info()
print(buf_info)
print('Exported Python array memory address is {}'.format(buf_info[0]))

# Check that the memory pointed to by the buffer info stores the right data
# Assumming the data is stored as IEEE double, 64-bit (8 byte) floating point number
data_py = [struct.unpack('<d', ctypes.string_at(buf_info[0]+i*8, 8))[0] for i in range(buf_info[1])]
print(data_py)

# And the corresponding Matlab data
data_mat = [struct.unpack('<d', ctypes.string_at(addr_mat+i*8, 8))[0] for i in range(buf_info[1])]
print(data_mat)

# Recap
print('Original Matlab array in Python memory address is {}'.format(addr_py))
print('Matlab array memory address is                    {}'.format(addr_mat))
print('Matlab base workspace array memory address is     {}'.format(addr_base))
print('Exported Python array memory address is           {}'.format(buf_info[0]))

# We can do some additional exploration:
#   1. We can change an element in Python and see if it propagates to Matlab (partly)
#   2. We can change an element in Matlab and see if it propagates to Python (no)

# First Python-to-Matlab
print('\nChange first element in Python matrix')
mm[0][0] = 10
print(mm._data.buffer_info()[0])
print([struct.unpack('<d', ctypes.string_at(addr_py+i*8, 8))[0] for i in range(9)])
print('Matlab Matrix in Python')
print(int(m.interface.call('get_address', [mm])))
m.interface.call('disp', [mm])
print('Matlab Matrix in Matlab') 
print(int(m.interface.call('evalin', ['base', 'get_address(mm_mat)'])))
m.interface.call('evalin', ['base', 'disp(mm_mat)'], nargout=0)

# Now Matlab-to-Python
print('Change second element in Matlab base workspace')
m.interface.call('evalin', ['base', 'mm_mat(2) = 12'], nargout=0)
print('Matlab Matrix in Python')
print(int(m.interface.call('get_address', [mm])))
m.interface.call('disp', [mm])
print('Python Matrix')
print(mm_py._data.buffer_info()[0])
print(mm_py)
```

The produced output is:

```
Original Matlab array in Python memory address is 1933042883584
[1.0, 4.0, 7.0, 2.0, 5.0, 8.0, 3.0, 6.0, 9.0]
Matlab array memory address is 1933000170400
  Name        Size            Bytes  Class     Attributes
  
  mm_mat      3x3                72  double

Matlab base workspace array memory address is 1933000170400
<class 'mlarray.double'>
[[1.0,2.0,3.0],[4.0,5.0,6.0],[7.0,8.0,9.0]]
<class 'array.array'>
array('d', [1.0, 4.0, 7.0, 2.0, 5.0, 8.0, 3.0, 6.0, 9.0])
(1933042883656, 9)
Exported Python array memory address is 1933042883656
[1.0, 4.0, 7.0, 2.0, 5.0, 8.0, 3.0, 6.0, 9.0]
[1.0, 4.0, 7.0, 2.0, 5.0, 8.0, 3.0, 6.0, 9.0]
Original Matlab array in Python memory address is 1933042883584
Matlab array memory address is                    1933000170400
Matlab base workspace array memory address is     1933000170400
Exported Python array memory address is           1933042883656

Change first element in Python matrix
1933042883584
[10.0, 4.0, 7.0, 2.0, 5.0, 8.0, 3.0, 6.0, 9.0]
Matlab Matrix in Python
1933000171264
    10     2     3
     4     5     6
     7     8     9

Matlab Matrix in Matlab
1933000170400
     1     2     3
     4     5     6
     7     8     9
     
Change second element in Matlab base workspace
mm_mat =
     1     2     3
    12     5     6
     7     8     9

Matlab Matrix in Python
1933000171264
    10     2     3
     4     5     6
     7     8     9
     
Python Matrix
1933042883656 
[[1.0,2.0,3.0],[4.0,5.0,6.0],[7.0,8.0,9.0]]
```

So an element change in Python causes another copy of the whole matrix when exported to Matlab, but changes in the Matlab side version does not propagate to Python (since the arrays do not share memory).
