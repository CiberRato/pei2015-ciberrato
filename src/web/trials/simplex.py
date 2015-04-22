from competition.models import LogTrialAgent


class AgentX():
    def __init__(self, log_trial_agent, trial_id):
        if log_trial_agent.competition_agent.agent.is_local:
            self.agent_type = "virtual"
        else:
            self.agent_type = "local"

        self.agent_name = log_trial_agent.competition_agent.agent.agent_name
        self.pos = log_trial_agent.pos
        self.language = log_trial_agent.competition_agent.agent.language

        if not log_trial_agent.competition_agent.agent.is_local:
            # o agent tem de estar na simulacao
            # autenticacao para receber estes dados
            self.files = "/api/v1/agents/agent_file/" + log_trial_agent.competition_agent.agent.agent_name + "/"


class TrialX():
    def __init__(self, trial):
        self.trial_id = trial.identifier

        # a competicao nao pode estar em register
        self.grid = "/api/v1/competitions/round_file/" + trial.round.name + "/?file=grid"
        self.param_list = "/api/v1/competitions/round_file/" + trial.round.name + "/?file=param_list"
        self.lab = "/api/v1/competitions/round_file/" + trial.round.name + "/?file=lab"

        # get the agents
        log_trial_agents = LogTrialAgent.objects.filter(trial=trial)
        self.agents = []
        for log_trial_agent in log_trial_agents:
            self.agents += [AgentX(log_trial_agent, self.trial_id)]