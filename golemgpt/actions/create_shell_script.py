from .delegate_job import delegate_job_action


def create_shell_script_action(
    name: str, description: str, in_files: list, out_files: list, **kwargs
) -> str:
    """Create a Bash script and return its content."""
    return delegate_job_action(
        goal=f"Create a Bash script {name}: {description}",
        role='coder',
        in_files=in_files,
        out_files=out_files,
    )
