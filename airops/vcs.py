from typing import List
from airflow.providers.ssh.operators.ssh import SSHOperator
import shlex

from typing import List

class GitCloneFlag:
    """
    A utility class that provides common flags for the `git clone` command.
    Each method returns a list of arguments representing specific `git clone` options.
    """

    @staticmethod
    def verbose() -> List[str]:
        """
        Provides the verbose flag for `git clone`, which outputs detailed information about the cloning process.

        Returns:
            List[str]: A list containing the `--verbose` flag.
        """
        return ["--verbose"]

    @staticmethod
    def branch(name: str) -> List[str]:
        """
        Provides the branch flag for `git clone`, allowing you to clone a specific branch.

        Args:
            name (str): The name of the branch to be cloned.

        Returns:
            List[str]: A list containing the `--branch` flag followed by the branch name.
        """
        return ["--branch", name]


class Git:

    def __init__(self) -> None:
        pass

    def _ssh(self, command, **kwargs):
        """
        Executes the given command on the remote machine via SSH.

        Args:
            command (str): The command to execute.
            **kwargs: Additional arguments for SSH execution.
        """
        return SSHOperator(**{
            "ssh_conn_id": self.ssh_conn_id,
            "command": command,
            **kwargs})
    
    def clone(self, repository_url: str, directory: str=".", flags: List[GitCloneFlag] = None, return_command: bool = False, **kwargs) -> None:
        args = ["git", "clone", *flags, repository_url, directory]
        safe_args = [shlex.quote(arg) for arg in args]
        command = " ".join(safe_args)
        if return_command:
            return command
        else:
            return self._ssh(command=command, **kwargs)
