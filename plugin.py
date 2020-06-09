###
# Copyright (c) 2020, Nelluk
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

from supybot import utils, plugins, ircutils, callbacks
from supybot.commands import *
import supybot.log as log
# from rcp import get_poll_data
from bs4 import BeautifulSoup

try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('RCP')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x


class RCP(callbacks.Plugin):
    """Display results of RealClearPolitics polling summaries"""
    threaded = True

    # TODO: poll url at end
    # TODO: check for correct URL domain

    def get_poll_data(self, url):
        # Parsing code modified from Anthony Bloomer https://github.com/AnthonyBloomer/rcp

        response = utils.web.getUrlFd(url)
        # response = urlopen(url)
        soup = BeautifulSoup(response, 'html.parser')
        fp = soup.find("div", {"id": 'polling-data-full'})
        title = soup.find("title").contents[0]

        if not fp:
            return

        rows = fp.find('table', {"class": 'data'})

        p = []
        poll_summary = {'title': title}

        # first row is headers, second row should be RCP Average
        for row in rows:
            cols = row.find_all(['th', 'td'])
            p.append([ele.text.strip() for ele in cols])
            if len(p) >= 2:
                # I only want the first two rows, but slicing as in rows[:2] fails. Quick hack way to limit the loop
                break

        keys = p[0]  # extract header rows ie Date/Spread

        for i, n in enumerate(keys):
            poll_summary[n] = p[1][i]

        return poll_summary

    def rcp(self, irc, msg, args, rcp_url):
        """Load a RealClearPolitics polling URL and display the top-line average"""
        log.debug('avg called')
        poll_data = self.get_poll_data(rcp_url)

        response = []
        for k, v in poll_data.items():
            if k in ['title', 'Poll', 'MoE', 'Sample', 'Date']:
                continue  # skip unwanted fields
            k_formatted = k.replace('(D)', ircutils.mircColor('(D)', fg='blue', bg='dark gray')).replace(
                '(R)', ircutils.mircColor('(R)', fg='red', bg='dark gray')
            )
            response.append(f'{ircutils.underline(k_formatted)}: {v}')

        response_str = ' | '.join(response)

        irc.reply(f'{ircutils.bold(poll_data["title"])} {poll_data["Date"]} | {response_str}')

    rcp = wrap(rcp, ['url'])


Class = RCP


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
