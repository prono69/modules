# -*- coding: future_fstrings -*-

#    Friendly Telegram (telegram userbot)
#    Copyright (C) 2018-2019 The Authors

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.

#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging
import inspect

from telethon.tl.functions.channels import JoinChannelRequest

from .. import loader, utils

logger = logging.getLogger(__name__)


def register(cb):
    cb(HelpMod())


class HelpMod(loader.Module):
    """Provides this help message"""
    def __init__(self):
        super().__init__()
        self.name = _("Help")
        self.allmodules = None
        self.client = None

    async def helpcmd(self, message):
        """.help [module]"""
        args = utils.get_args_raw(message)
        if args:
            module = None
            for mod in self.allmodules.modules:
                if mod.name.lower() == args.lower():
                    module = mod
            if module is None:
                await message.edit("<code>" + _("Invalid module name specified") + "</code>")
                return
            # Translate the format specification and the module seperately
            reply = "<b>" + _("Help for</b> <code>{}</code>:").format(utils.escape_html(_(module.name))) + "\n  "
            if module.__doc__:
                reply += utils.escape_html(inspect.cleandoc(module.__doc__))
            else:
                logger.warning("Module %s is missing docstring!", module)
            for name, fun in module.commands.items():
                reply += f"\n  <code>{name}</code>\n"
                if fun.__doc__:
                    reply += utils.escape_html("\n".join(["    " + x for x in
                                                          _(inspect.cleandoc(fun.__doc__)).splitlines()]))
                else:
                    reply += _("There is no documentation for this command")
        else:
            reply = _('<b>Available modules:</b>\n')
            for mod in self.allmodules.modules:
                if len(mod.commands) != 0:
                    if len(mod.commands) is 1:
                        cmds_count = _('1 cmd')
                    else:
                        cmds_count = _('{} cmds').format(len(mod.commands))
                    reply += _("<code><b>{name}</b></code> <code>({cmds})</code>:\n").format(name=mod.name, cmds=cmds_count)
                    count = 0
                    for cmd in mod.commands:
                        if count < (len(mod.commands) - 1):
                            reply += f' {cmd} <b>|</b>'
                        else:
                            reply += f' {cmd}\n'
                            count = 0  # works without, but better reset to 0.
                        count += 1
        await utils.answer(message, reply)

    async def supportcmd(self, message):
        """Joins the support chat"""
        await self.client(JoinChannelRequest("https://t.me/ftgextended"))
        await message.edit('<code>' + _('Joined to '
                                        '</code><a href="https://t.me/ftgextended">' + 'support chat' + '</a>'))

    async def client_ready(self, client, db):
        self.client = client
