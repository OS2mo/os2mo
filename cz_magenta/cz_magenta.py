from commitizen.cz.conventional_commits import ConventionalCommitsCz
from commitizen.defaults import Questions
from commitizen.cz.exceptions import CzException


class DoNotIncludeBrackets(CzException):
    ...


class TicketNumberShouldBeInteger(CzException):
    ...


def parse_ticketnumber(text: str) -> str:
    # TODO: Extract from branch name?
    if not text:
        return "xxxxx"

    if "[" in text or "]" in text:
        raise DoNotIncludeBrackets("Do not include '[]' in ticket number")

    try:
        ticket_number = int(text)
    except ValueError:
        raise TicketNumberShouldBeInteger("Ticket number should be an integer")
    return ticket_number


class MagentaCz(ConventionalCommitsCz):
    commit_parser = r"^(?P<change_type>fix|feat|docs|style|refactor|perf|test|build|ci)(?:\((?P<scope>[^()\r\n]*)\)|\()?(?P<breaking>!)?:\s?(?P<ticket>\[#.*\])?\s(?P<message>.*)?"
    change_type_map = {
        "fix": "Bug Fixes",
        "feat": "Features",
        "docs": "Documentation",
        "style": "Style",
        "refactor": "Code Refactor",
        "perf": "Performance improvements",
        "test": "Test improvements",
        "build": "Build improvements",
        "ci": "CI improvements",
    }

    def changelog_message_builder_hook(self, parsed_message: dict, commit) -> dict:
        output = ""
        if parsed_message["breaking"] is not None:
            output = u"\u26A0\uFE0F" + " "
        output += parsed_message["ticket"] + " " + parsed_message["message"]
        output += ("\n\n" + commit.body + "\n" if commit.body else "")
        parsed_message["message"] = output
        return parsed_message

    # Questions = Iterable[MutableMapping[str, Any]]
    # It expects a list with dictionaries.
    def questions(self) -> Questions:
        """Questions regarding the commit message."""
        questions = [{
            "type": "input",
            "name": "ticket",
            "message": (
                "What is the relevant ticket number? (press [enter] to skip)\n"
            ),
            "filter": parse_ticketnumber
        }]
        questions.extend(super().questions())
        return questions

    def message(self, answers: dict) -> str:
        prefix = answers["prefix"]
        scope = answers["scope"]
        ticket = answers["ticket"]
        subject = answers["subject"]
        body = answers["body"]
        footer = answers["footer"]
        is_breaking_change = answers["is_breaking_change"]

        if scope:
            scope = f"({scope})"
        if body:
            body = f"\n\n{body}"
        if is_breaking_change:
            footer = f"BREAKING CHANGE: {footer}"
        if footer:
            footer = f"\n\n{footer}"

        message = f"{prefix}{scope}: [#{ticket}] {subject}{body}{footer}"

        return message

    def example(self) -> str:
        return (
            "fix: [#12345] correct minor typos in code\n"
            "\n"
            "see the issue for details on the typos fixed\n"
            "\n"
            "closes issue #12"
        )

    def schema(self) -> str:
        return (
            "<type>(<scope>): [<ticket>] <subject>\n"
            "<BLANK LINE>\n"
            "<body>\n"
            "<BLANK LINE>\n"
            "(BREAKING CHANGE: )<footer>"
        )

    def schema_pattern(self) -> str:
        PATTERN = (
            r"(?s)"  # To explictly make . match new line
            r"(build|ci|docs|feat|fix|perf|refactor|style|test|chore|revert|bump)"  # type
            r"(\(\S+\))?!?:"  # scope
            r"( \[#\S+\])"  # ticket
            r"( [^\n\r]+)"  # subject
            r"((\n\n.*)|(\s*))?$"
        )
        return PATTERN

discover_this = MagentaCz
