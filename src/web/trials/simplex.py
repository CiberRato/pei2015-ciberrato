from competition.models import LogTrialAgent


class AgentX():
    def __init__(self, log_trial_agent, trial_id):
        if log_trial_agent.competition_agent.agent.is_remote:
            self.agent_type = "virtual"
        else:
            self.agent_type = "local"

        self.agent_name = log_trial_agent.competition_agent.agent.agent_name
        self.team_name = log_trial_agent.competition_agent.agent.team.name
        self.pos = log_trial_agent.pos
        self.language = log_trial_agent.competition_agent.agent.language

        if not log_trial_agent.competition_agent.agent.is_remote:
            # o agent tem de estar na simulacao
            # autenticacao para receber estes dados
            self.files = "/api/v1/agents/agent_file/" + log_trial_agent.competition_agent.agent.team.name + "/" + log_trial_agent.competition_agent.agent.agent_name + "/"


class TrialX():
    def __init__(self, trial):
        self.trial_id = trial.identifier

        # a competicao nao pode estar em register
        self.grid = "/api/v1/competitions/round_file/" + trial.round.name + "/?file=grid"
        self.param_list = "/api/v1/competitions/round_file/" + trial.round.name + "/?file=param_list"
        self.lab = "/api/v1/competitions/round_file/" + trial.round.name + "/?file=lab"

        # send type of competition information
        self.type_of_competition = trial.round.parent_competition.type_of_competition

        # get the agents
        log_trial_agents = LogTrialAgent.objects.filter(trial=trial)
        self.agents = []
        for log_trial_agent in log_trial_agents:
            self.agents += [AgentX(log_trial_agent, self.trial_id)]