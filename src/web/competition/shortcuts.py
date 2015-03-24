def simulation_started(simulation):
    return simulation.started


def simulation_waiting(simulation):
    return not simulation.started


def simulation_done(simulation):
    try:
        return (simulation.log_json.url is not None) and simulation.started
    except ValueError:
        return False