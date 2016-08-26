import numpy as np

def set_tick_arrangement(grid):

    if grid.grx[0] < 0:
        tick_range = grid.grx[0] - grid.grx[-1]
    elif grid >= 0:
        tick_range = grid.grx[-1] - grid.grx[0]

    nticks = 4
    tick_step = np.round(tick_range / nticks)

    if grid.grx[0] < 0:
        if 4*tick_step < grid.grx[0]:
            tick_arrangement = tick_step*np.arange(nticks)
        else:
            tick_arrangement = tick_step*np.arange(nticks+1)

    if grid.grx[0] >= 0:
        if 4*tick_step > grid.grx[-1]:
            tick_arrangement = tick_step*np.arange(nticks)
        else:
            tick_arrangement = tick_step*np.arange(nticks+1)

    return tick_arrangement
