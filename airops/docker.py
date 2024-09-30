"""
This module provides classes and methods to facilitate Docker commands execution via SSH, inspired by the concept of the 'special' library.
It offers a convenient way to construct and execute `docker run` and `docker build` commands with various flags in a flexible manner.

Classes:
    - DockerRunFlag: Provides methods to generate lists of flags for the `docker run` command.
    - DockerBuildFlag: Provides methods to generate lists of flags for the `docker build` command.
    - Docker: A class to manage Docker commands execution via SSH, including login, build, and run operations.

Usage Example:
    docker = Docker(ssh_conn_id="my_ssh_connection", username="myuser", password="mypassword")
    docker.build(
        docker_flags=DockerBuildFlag.build_arg({"arg1": "value1"}) + DockerBuildFlag.pull(),
        image_name="my_image",
        project_path="."
    )
    docker.run(
        image_name="my_image",
        docker_flags=DockerRunFlag.temp_container() + DockerRunFlag.env({"ENV_VAR": "value"}) + DockerRunFlag.volume({"/host/path": "/container/path"})
    )
"""

from typing import Dict, List, Union
from airflow.providers.ssh.operators.ssh import SSHOperator
import shlex

class DockerRunFlag:
    """
    Provides static methods to generate flag options for the `docker run` command.

    Methods:
        - detach(): Returns the flag for running a container in detached mode.
        - interactive(): Returns the flag for interactive mode.
        - tty(): Returns the flag for allocating a pseudo-TTY.
        - temp_container(): Returns the flag for automatically removing the container when it exits.
        - name(name: str): Returns the flag for setting the container's name.
        - publish(ports: Dict[str, str]): Returns the flag for publishing container ports to the host.
        - env(envs: Dict[str, str]): Returns the flag for setting environment variables in the container.
        - volume(volume: Dict[str, str]): Returns the flag for binding mount volumes.
    """

    @staticmethod
    def detach() -> List[str]:
        """Returns the flag for running a container in detached mode."""
        return ["-d"]

    @staticmethod
    def interactive() -> List[str]:
        """Returns the flag for interactive mode."""
        return ["-i"]

    @staticmethod
    def tty() -> List[str]:
        """Returns the flag for allocating a pseudo-TTY."""
        return ["-t"]

    @staticmethod
    def temp_container() -> List[str]:
        """Returns the flag for automatically removing the container when it exits."""
        return ["--rm"]

    @staticmethod
    def name(name: str) -> List[str]:
        """Returns the flag for naming the container."""
        return ["--name", name]

    @staticmethod
    def publish(ports: Dict[str, str]) -> List[str]:
        """Returns flags for publishing container ports to the host."""
        arg = []
        for p1, p2 in ports.items():
            arg += ["-p", f"{p1}:{p2}"]
        return arg

    @staticmethod
    def env(envs: Dict[str, str]) -> List[str]:
        """Returns flags for setting environment variables in the container."""
        arg = []
        for name, value in envs.items():
            arg += ["-e", f"{name}={value}"]
        return arg

    @staticmethod
    def volume(volume: Dict[str, str]) -> List[str]:
        """Returns flags for binding mount volumes."""
        arg = []
        for p1, p2 in volume.items():
            arg += ["-v", f"{p1}:{p2}"]
        return arg

class DockerBuildFlag:
    """
    Provides static methods to generate flag options for the `docker build` command.

    Methods:
        - build_arg(envs: Dict[str, str]): Returns flags for setting build-time variables.
        - file(f: str): Returns the flag for specifying a Dockerfile.
        - no_cache(): Returns the flag for disabling the build cache.
        - target(t: str): Returns the flag for specifying a build target.
        - pull(): Returns the flag for always attempting to pull a newer version of the image.
        - platform(platform_name: str): Returns the flag for specifying the target platform.
    """

    @staticmethod
    def build_arg(envs: Dict[str, str]) -> List[str]:
        """Returns flags for setting build-time variables."""
        arg = []
        for name, value in envs.items():
            arg += ["--build-arg", f"{name}={value}"]
        return arg

    @staticmethod
    def file(f: str) -> List[str]:
        """Returns the flag for specifying a Dockerfile."""
        return ["-f", f]

    @staticmethod
    def no_cache() -> List[str]:
        """Returns the flag for disabling the build cache."""
        return ["--no-cache"]

    @staticmethod
    def target(t: str) -> List[str]:
        """Returns the flag for specifying a build target."""
        return ["--target", t]

    @staticmethod
    def pull() -> List[str]:
        """Returns the flag for always attempting to pull a newer version of the image."""
        return ["--pull"]

    @staticmethod
    def platform(platform_name: str) -> List[str]:
        """Returns the flag for specifying the target platform."""
        return ["--platform", platform_name]

class Docker:
    """
    Manages Docker commands execution via SSH, allowing you to login, build, and run Docker containers remotely.

    Attributes:
        - ssh_conn_id (str): SSH connection ID used to connect to the remote machine.
        - _username (str): Docker Hub username for login.
        - _password (str): Docker Hub password for login.

    Methods:
        - __init__(ssh_conn_id, username=None, password=None): Initializes the Docker object with SSH connection details.
        - _login_command(): Constructs the `docker login` command based on the provided credentials.
        - _ssh(command, **kwargs): Executes the given command on the remote machine via SSH.
        - run(docker_flags, image_name, app_args=None, **kwargs): Executes a `docker run` command with specified flags and image.
        - build(image_name, docker_flags, project_path=".", **kwargs): Executes a `docker build` command with specified flags and image.
    """

    def __init__(self, ssh_conn_id: str, username: str = None, password: str = None) -> None:
        """
        Initializes the Docker object with SSH connection details and optional Docker Hub credentials.

        Args:
            ssh_conn_id (str): SSH connection ID used to connect to the remote machine.
            username (str, optional): Docker Hub username for login.
            password (str, optional): Docker Hub password for login.
        """
        self.ssh_conn_id = ssh_conn_id
        self._username = username
        self._password = password
    
    def _login_command(self) -> Union[str, None]:
        """
        Constructs the `docker login` command based on the provided credentials.

        Returns:
            Union[str, None]: The login command string if credentials are provided, otherwise None.
        """
        if self._username and self._password:
            args = ["docker", "login", "-u", self._username, "-p", self._password]
            safe_args = [shlex.quote(arg) for arg in args]
            command = " ".join(safe_args)
        else:
            command = None
        return command
    
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

    def run(self, docker_flags: List[str], image_name: str, app_args: List[str] = None, return_command: bool = False, **kwargs):
        """
        Executes a `docker run` command with specified flags and image.

        Args:
            docker_flags (List[str]): List of flags to pass to the `docker run` command.
            image_name (str): The name of the Docker image to run.
            app_args (List[str], optional): Additional arguments to pass to the container.
            return_command (bool, optional): Whether to return the command instead of executing it. Defaults to False.
            **kwargs: Additional arguments for SSH execution.
        """
        app_args = app_args or list()
        args = ["docker", "run", *docker_flags, image_name, *app_args]
        safe_args = [shlex.quote(arg) for arg in args]
        command = " ".join(safe_args)
        login_command = self._login_command()
        if login_command:
            command = login_command + " && " + command
        if return_command:
            return command
        else:
            return self._ssh(command=command, **kwargs)
    
    def build(self, image_name: str, docker_flags: List[str], project_path: str = ".", return_command: bool = False, **kwargs):
        """
        Executes a `docker build` command with specified flags and image.

        Args:
            image_name (str): The name of the Docker image to build.
            docker_flags (List[str]): List of flags to pass to the `docker build` command.
            project_path (str, optional): The path to the project directory. Defaults to ".".
            return_command (bool, optional): Whether to return the command instead of executing it. Defaults to False.
            **kwargs: Additional arguments for SSH execution.
        """
        args = ["docker", "build", *docker_flags, "-t", image_name, project_path]
        safe_args = [shlex.quote(arg) for arg in args]
        command = " ".join(safe_args)
        login_command = self._login_command()
        if login_command:
            command = login_command + " && " + command
        if return_command:
            return command
        else:
            return self._ssh(command=command, **kwargs)
