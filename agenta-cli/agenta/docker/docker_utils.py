import docker
import os
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from pathlib import Path
import shutil


def create_dockerfile(out_folder: Path):
    """Creates a dockerfile based on the template in the out_folder.

    Arguments:
        out_folder -- Folder in which to create the Dockerfile.
    """
    assert Path(out_folder).exists(), f"Folder {out_folder} does not exist."
    dockerfile_template = Path(__file__).parent / "Dockerfile.template"
    dockerfile_path = out_folder / "Dockerfile"
    shutil.copy(dockerfile_template, dockerfile_path)
    return dockerfile_path


def build_image(folder: Path) -> Path:
    """Builds an image from the folder and returns the path

    Arguments:
        folder -- _description_

    Returns:
        _description_
    """
    # Initialize Docker client
    client = docker.from_env()

    with TemporaryDirectory() as temp_dir:
        # Create a Dockerfile for the project
        dockerfile_path = create_dockerfile(folder)

        # Copy the project files to a temporary directory
        shutil.copytree(folder, temp_dir, dirs_exist_ok=True)

        # Build the Docker image
        print("Building Docker image...")
        image, build_log = client.images.build(
            path=temp_dir,
            tag=f"agenta/test:latest",
            rm=True  # Remove intermediate containers after a successful build
        )

        # Print the build log
        for line in build_log:
            print(line)

        # Upload the Docker image to the Agenta registry
        print("Uploading Docker image...")
        client.images.push(repository=f"agenta/{folder}", tag="latest")
        print("Docker image uploaded successfully.")

        # Clean up the temporary Dockerfile
        dockerfile_path.unlink()
