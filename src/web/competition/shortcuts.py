def simulation_started(simulation):
    return simulation.started


def simulation_waiting(simulation):
    return not simulation.started


def simulation_done(simulation):
    return (simulation.log_json is not None) and simulation.started