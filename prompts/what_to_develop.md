# Miniature

Github-based folder-packaging system.


## Overview

github-based generalized package or folder publication system.

We don't need to develop something complex again.

We will use `npm degit` or `git` or `gh` commands.

We just need to make the abstractions using them for our purpose. For the abstraction, we will use the module `runsh`.

[https://github.com/crimson206/runsh](https://github.com/crimson206/runsh)

We will define our scriptized functions in the `scripts` folder.


## Architucture

rough abstractions of the runsh module.

### Publish

db-repo is the target repo. The folder will be pushed to the repository as a package.
Publish means, we generate a tag with '{root-dir}/v{version}' with push.


`runsh publish example_pkg`

Arguments:
    pkg-root                Required. The root path of a pkg folder.

Options:
    -f --force      If the tag already exists, publish causes an error. If it is on, the version is override.


### Load

It is similar to clone. The difference is, it load the folder only.

npx degit을 사용하여 구현할 것.

