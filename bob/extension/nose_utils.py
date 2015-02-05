import functools
import resource

def memory_check(test_function):
  """Generic decorator fucntion for detecting if there are memory leaks inside the wrapped function.

  If you are in doubt that some function tested with nose tests might generate memory leaks, you can simply decorate the function with this decorator:

  .. code-block:: py

     from bob.extension.nose import memory_check

     @memory_check
     def test_my_code():
       ...

  .. warning::
     This function might have false positives, e.g., when global variables are set inside the tested function.

  .. warning::
     This function might also have false negatives, i.e., when the memory loss is too small.
     To assure that memory leaks are detected, use objects of sufficient size.
  """

  @functools.wraps(test_function)
  def wrapper(*args, **kwargs):
    before = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    result = test_function(*args, **kwargs)
    after = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

    assert before == after, "The memory inside the function '%s' was changed from %d to %d (a change of %d bytes); do you have a memory leak there?" % (test_function.__name__, before, after, after-before)
    return result
  return wrapper
