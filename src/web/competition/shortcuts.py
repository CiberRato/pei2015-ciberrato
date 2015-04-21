def trial_started(trial):
    return trial.started


def trial_waiting(trial):
    return trial.waiting


def trial_done(trial):
    try:
        return (trial.log_json.url is not None) and trial.started
    except ValueError:
        return False


def trial_error(trial):
    return len(trial.errors) != 0


def trial_not_started(trial):
    return not trial_waiting(trial) and not trial_done(trial) and not trial_started(trial)