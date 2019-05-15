# Contributing

If you're reading this then thanks for helping out with Kapture!

# Guidelines

We plan to accept almost any PR; we value your ideas. Including half baked ones.
If you think your idea is a little too undercooked, just throw it onto a contrib branch and draw some attention to it.

## Kapture Images

In order to work on Kubernetes, Kapture builds its own custom container.
To do this, there a workflow setup on DockerHub to automatically build an image with the appropriate tag whenever a new push occurs.
By default, the new container will be tagged with `dev-${branch_name}`; a branch called `test-changes` will result in a docker container with the tag: `dev-test-changes`.
If you do need to test changes to the Kapture container, create a new branch, update the [`kustomization.yml`](kustomization.yml) to use the new tag, and the rest should be automatic.

# Coding Conventions

Kapture's a bit of a mixed bag when it comes to languages.
There's a lot of Bash, a helping of yaml files, and a fair amount of Python.
The only real, overarching patterns are four spaces for tabs and inline curly brackets for blocks.
In general, just try to match what the code being modified looks like and it'll be fine.
