# PyPI Publishing Setup Instructions

This repository is configured to automatically publish to PyPI when you push a version tag. The workflow uses PyPI's **Trusted Publishing** feature, which is more secure than using API tokens.

## Setting up PyPI Trusted Publishing

1. **Create a PyPI account** if you don't have one at https://pypi.org

2. **Navigate to PyPI's trusted publishing setup**:
   - Go to https://pypi.org/manage/account/publishing/
   - You need to be logged into your PyPI account

3. **Add a new trusted publisher** with these details:
   - **PyPI project name**: `fmi-bd2cmake`
   - **Owner**: `jgillis` (your GitHub username)
   - **Repository name**: `fmi-bd2cmake`
   - **Workflow filename**: `publish-to-pypi.yml`
   - **Environment name**: Leave blank (optional)

4. **Click "Add"** to save the trusted publisher configuration

## Publishing a New Version

To publish a new version to PyPI:

1. **Update the version** in two places:
   - `pyproject.toml`: Update the `version = "x.y.z"` field
   - `fmi_bd2cmake/__init__.py`: Update the `__version__ = "x.y.z"` line

2. **Commit and push your changes**:
   ```bash
   git add .
   git commit -m "Bump version to x.y.z"
   git push
   ```

3. **Create and push a version tag**:
   ```bash
   git tag -a vx.y.z -m "Release version x.y.z"
   git push origin vx.y.z
   ```

   Or create the tag directly on GitHub in the Releases section.

4. **Monitor the workflow**:
   - Go to the "Actions" tab in your GitHub repository
   - Watch the "Publish to PyPI" workflow run
   - If successful, your package will be available on PyPI at https://pypi.org/project/fmi-bd2cmake/

## Important Notes

- The workflow includes version consistency checks to ensure the tag matches the versions in `pyproject.toml` and `__init__.py`
- Only tags starting with 'v' will trigger the publishing workflow (e.g., `v1.0.0`, `v0.2.1`)
- The first time you push a tag, PyPI might require you to manually create the project if it doesn't exist yet
- Make sure your repository is public or you have proper permissions set up for the workflow to run

## Troubleshooting

- **"Project does not exist" error**: You may need to first upload a version manually or create the project on PyPI
- **"Version already exists" error**: Make sure you've incremented the version number and that all three places (tag, pyproject.toml, __init__.py) match
- **"Permission denied" error**: Verify that the trusted publishing configuration in PyPI matches exactly with your repository details

## Security Benefits of Trusted Publishing

- No need to store API tokens as GitHub secrets
- Automatic credential rotation
- Enhanced security through OpenID Connect (OIDC)
- Full audit trail of publishing events