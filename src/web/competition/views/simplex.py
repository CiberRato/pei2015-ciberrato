from competition.shortcuts import *
from competition.models import LogTrialAgent


class RoundSimplex:
    def __init__(self, r):
        self.name = r.name
        self.parent_competition_name = str(r.parent_competition)
        self.param_list_path = r.param_list_path
        self.grid_path = r.grid_path
        self.lab_path = r.lab_path


class TeamEnrolledSimplex:
    def __init__(self, ge):
        self.competition = ge.competition
        self.team_name = ge.team.name
        self.valid = ge.valid


class CompetitionAgentSimplex:
    def __init__(self, cas):
        self.round_name = cas.round.name
        self.agent_name = cas.agent.agent_name
        self.team_name = cas.agent.team.name
        self.created_at = cas.created_at
        self.updated_at = cas.updated_at


class TrialSimplex:
    def __init__(self, ss):
        self.round_name = ss.round.name
        self.competition_name = ss.round.parent_competition.name
        self.identifier = ss.identifier
        self.errors = ss.errors
        self.created_at = ss.created_at
        self.updated_at = ss.updated_at
        if trial_done(ss):
            self.state = "LOG"
        elif trial_error(ss):
            self.state = "ERROR"
        elif trial_started(ss):
            self.state = "STARTED"
        elif trial_waiting(ss):
            self.state = "WAITING"
        elif trial_prepare(ss):
            self.state = "PREPARE"
        else:
            self.state = "READY"


class TrialAgentSimplex:
    def __init__(self, sas):
        self.trial_identifier = sas.trial.identifier
        self.agent_name = sas.competition_agent.agent.agent_name
        self.team_name = sas.competition_agent.agent.team.name
        self.round_name = sas.trial.round.name
        self.pos = sas.pos


class GridPositionsSimplex:
    def __init__(self, ps):
        self.competition = ps.competition
        self.team_name = ps.team.name
        self.identifier = ps.identifier


class TrialGridSimplex:
    def __init__(self, sgs):
        self.grid_positions = GridPositionsSimplex(sgs.grid_positions)
        self.position = sgs.position


class AgentGridSimplex:
    def __init__(self, sgs):
        self.grid_identifier = sgs.grid_position.identifier
        self.agent_name = sgs.agent.agent_name
        self.team_name = sgs.agent.team.name
        self.position = sgs.position


class TeamScoreSimplex:
    def __init__(self, tss):
        self.trial = TrialSimplex(tss.trial)
        self.team = tss.team
        self.score = tss.score
        self.number_of_agents = tss.number_of_agents
        self.time = tss.time


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
        self.grid = "/api/v1/competitions/round_file/" + trial.round.parent_competition.name + "/" + trial.round.name + "/grid/"
        self.param_list = "/api/v1/competitions/round_file/" + trial.round.parent_competition.name + "/" + trial.round.name + "/param_list/"
        self.lab = "/api/v1/competitions/round_file/" + trial.round.parent_competition.name + "/" + trial.round.name + "/lab/"

        # allow remote agents
        self.allow_remote_agents = trial.round.parent_competition.allow_remote_agents

        # send type of competition information
        self.type_of_competition = trial.round.parent_competition.type_of_competition

        # get the agents
        log_trial_agents = LogTrialAgent.objects.filter(trial=trial)
        self.agents = []
        for log_trial_agent in log_trial_agents:
            self.agents += [AgentX(log_trial_agent, self.trial_id)]


class RFile:
    def __init__(self, p, name):
        self.path = p
        self.name = name


class FolderSimplex:
    def __init__(self, name, sub):
        self.name = name
        self.sub = sub
