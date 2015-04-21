from competition.models import LogTrialAgent


class AgentX():
    def __init__(self, log_simulation_agent, simulation_id):
        if log_simulation_agent.competition_agent.agent.is_local:
            self.agent_type = "virtual"
        else:
            self.agent_type = "local"

        self.agent_name = log_simulation_agent.competition_agent.agent.agent_name
        self.pos = log_simulation_agent.pos
        self.language = log_simulation_agent.competition_agent.agent.language

        if not log_simulation_agent.competition_agent.agent.is_local:
            # o agent tem de estar na simulacao
            # autenticacao para receber estes dados
            self.files = "/api/v1/agents/agent_file/" + log_simulation_agent.competition_agent.agent.agent_name + "/"


class TrialX():
    def __init__(self, simulation):
        self.simulation_id = simulation.identifier

        # a competicao nao pode estar em register
        self.grid = "/api/v1/competitions/round_file/" + simulation.round.name + "/?file=grid"
        self.param_list = "/api/v1/competitions/round_file/" + simulation.round.name + "/?file=param_list"
        self.lab = "/api/v1/competitions/round_file/" + simulation.round.name + "/?file=lab"

        # get the agents
        log_simulation_agents = LogTrialAgent.objects.filter(simulation=simulation)
        self.agents = []
        for log_simulation_agent in log_simulation_agents:
            self.agents += [AgentX(log_simulation_agent, self.simulation_id)]