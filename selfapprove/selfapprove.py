import re

from errbot import BotPlugin, botcmd, arg_botcmd, webhook
from github3 import GitHub
from github3.exceptions import GitHubError


class Selfapprove(BotPlugin):
    """
    Self approve your github PR via a bot
    """

    def activate(self):
        """
        Triggers on plugin activation
        """
        token = self.config["GITHUB_TOKEN"]
        self.gh = GitHub(token=token)

        self.gh.is_starred(
            "github", "gitignore"
        )  # test connection, will raise if connection fails

        super(Selfapprove, self).activate()

    def get_configuration_template(self):
        """
        Defines the configuration structure this plugin supports
        """
        return {"GITHUB_TOKEN": "tokenvalue"}

    @arg_botcmd(
        "pr",
        help="The URL of the Pull Request you would like to self approve",
        type=str,
    )
    @arg_botcmd(
        "--reason",
        help="The reason you are self approving this PR instead of having a teammate approve",
        type=str,
        required=True,
    )
    @arg_botcmd(
        "--test-only-changes", help="Are these test only changes?", action="store_true"
    )
    def selfapprove(self, message, pr, reason, test_only_changes):
        if not message.to.name == 'self_approve':
            return "!selfapprove command must be run from #self_approve channel"
        if not test_only_changes:
            return "Changes that touch more than just tests must be approved by another engineer."

        match = re.search(r"https://github.com/(.+)/(.+)/pull/([0-9]+)", pr)
        if not match:
            return f"PR URL {pr} did not match regex r'https://github.com/(.+)/(.+)/pull/([0-9]+)'"

        org = match.group(1)
        repo_name = match.group(2)
        if not repo_name == 'apm_bundle':
            return f"selfapprove currently only works with apm_bundle"
        pr_num = match.group(3)
        repo = self.gh.repository(org, repo_name)
        pr = repo.pull_request(int(pr_num))
        pr.create_review(
            f"This PR was self-approved by {message.frm.fullname}. The stated reason for self-appoval was: {reason}",
            event="APPROVE",
        )
        return f"{pr} was succesfully self-approved."
