#========================================
# Utility functions for batching lists
#========================================

def batch_list(items, batch_size):
    """
    Split a list into batches.

    Example:

    Input:
        [1,2,3,4,5]

    batch_size=2

    Output
    [1,2]
    [3,4]
    [5]
    """

    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]