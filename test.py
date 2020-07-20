from showdowngym import ShowdownGym
from stable_baselines.common.env_checker import check_env
from baseai import BaseAi

env = ShowdownGym(BaseAi())
check_env(env, warn=True)