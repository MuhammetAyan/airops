import pytest
from airops.docker import Docker, DockerBuildFlag, DockerRunFlag

@pytest.fixture
def docker_obj():
    return Docker(ssh_conn_id="my_ssh_connection", username="myuser", password="mypassword")


@pytest.mark.parametrize(
    "docker_build_flag_obj, image_name, project_path, expected",
    [
        (DockerBuildFlag.build_arg({"arg1": "value1"}), "my_image", ".", "docker build --build-arg arg1=value1 -t my_image ."),
    ],
)
def test_docker_build(docker_obj, docker_build_flag_obj, image_name, project_path, expected):
    result = Docker.build(docker_obj, docker_build_flag_obj, image_name=image_name, project_path=project_path, return_command=True)
    assert result == expected

@pytest.fixture
def docker_run_obj(docker_obj, docker_run_flag_obj):
    return Docker.run(docker_obj, docker_run_flag_obj, image_name="my_image")

@pytest.fixture
def docker_obj_with_args(docker_obj, docker_run_flag_obj, docker_build_flag_obj):
    return Docker(docker_obj, docker_run_flag_obj, docker_build_flag_obj, image_name="my_image")
