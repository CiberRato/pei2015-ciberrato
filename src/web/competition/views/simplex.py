from competition.models import LogSimulationAgent


class RoundSimplex:
    def __init__(self, r):
        self.name = r.name
        self.parent_competition_name = str(r.parent_competition)
        self.param_list_path = r.param_list_path
        self.grid_path = r.grid_path
        self.lab_path = r.lab_path
        self.agents_list = r.agents_list


class GroupEnrolledSimplex:
    def __init__(self, ge):
        self.competition_name = ge.competition.name
        self.group_name = ge.group.name
        self.valid = ge.valid


class AgentSimplex:
    def __init__(self, ag):
        self.agent_name = ag.agent_name
        self.user = ag.user
        self.is_virtual = ag.is_virtual
        self.language = ag.language
        self.competitions = ag.competitions

        self.rounds = []
        for r in ag.rounds.all():
            self.rounds += [RoundSimplex(r)]

        self.group_name = ag.group.name
        self.created_at = ag.created_at
        self.updated_at = ag.updated_at


class CompetitionAgentSimplex:
    def __init__(self, cas):
        self.round_name = cas.round.name
        self.agent_name = cas.agent.agent_name
        self.created_at = cas.created_at
        self.updated_at = cas.updated_at


class SimulationSimplex:
    def __init__(self, ss):
        self.round_name = ss.round.name
        self.identifier = ss.identifier
        self.created_at = ss.created_at
        self.updated_at = ss.updated_at


class SimulationAgentSimplex:
    def __init__(self, sas):
        self.simulation_identifier = sas.simulation.identifier
        self.agent_name = sas.competition_agent.agent.agent_name
        self.round_name = sas.simulation.round.name
        self.pos = sas.pos


class AgentX():
    def __init__(self, log_simulation_agent, simulation_id):
        if log_simulation_agent.competition_agent.agent.is_virtual:
            self.agent_type = "virtual"
        else:
            self.agent_type = "local"

        self.agent_name = log_simulation_agent.competition_agent.agent.agent_name
        self.pos = log_simulation_agent.pos
        self.language = log_simulation_agent.competition_agent.agent.language

        if not log_simulation_agent.competition_agent.agent.is_virtual:
            # o agent tem de estar na simulacao
            # autenticacao para receber estes dados
            self.files = "/api/v1/competitions/agent_file/" + simulation_id + "/" + log_simulation_agent.competition_agent.agent.agent_name + "/"


class SimulationX():
    def __init__(self, simulation):
        self.simulation_id = simulation.identifier

        # a competicao nao pode estar em register
        self.grid = "/api/v1/competitions/round_file/" + simulation.round.name + "/?file=grid"
        self.param_list = "/api/v1/competitions/round_file/" + simulation.round.name + "/?file=param_list"
        self.lab = "/api/v1/competitions/round_file/" + simulation.round.name + "/?file=lab"

        # get the agents
        log_simulation_agents = LogSimulationAgent.objects.filter(simulation=simulation)
        self.agents = []
        for log_simulation_agent in log_simulation_agents:
            self.agents += [AgentX(log_simulation_agent, self.simulation_id)]