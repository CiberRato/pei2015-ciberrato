def simulation_started(simulation):
    return simulation.started


def simulation_waiting(simulation):
    return simulation.waiting


def simulation_done(simulation):
    try:
        return (simulation.log_json.url is not None) and simulation.started
    except ValueError:
        return False


def simulation_error(simulation):
    return len(simulation.errors) != 0


def simulation_not_started(simulation):
    return not simulation_waiting(simulation) and not simulation_done(simulation) and not simulation_started(simulation)