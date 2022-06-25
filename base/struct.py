from __future__ import annotations

class Config:
    def __init__(self, cfg: dict) -> None:
        self.bot_token = cfg['bot_token']
        self.bot_prefix = cfg['bot_prefix']
        self.guild = cfg['guild']
        self.chat_cmds = cfg['chat_cmds']
        self.chat_loop = cfg['chat_loop']
        self.chat_release = cfg['chat_release']
        self.setup = cfg['setup']
        self.eqp_role  = cfg['eqp_role']
        self.mark_role  = cfg['mark_role']
        self.aut_role  = cfg['aut_role']
        self.creat_role  = cfg['creat_role']
