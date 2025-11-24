[//]: # (STANDARD README)
[//]: # (https://github.com/RichardLitt/standard-readme)
[//]: # (----------------------------------------------)
[//]: # (Uncomment optional sections as required)
[//]: # (----------------------------------------------)

[//]: # (Title)
[//]: # (Match repository name)
[//]: # (REQUIRED)

# drydock

[//]: # (Banner)
[//]: # (OPTIONAL)
[//]: # (Must not have its own title)
[//]: # (Must link to local image in current repository)


> [!IMPORTANT]
> **Work in Progress**
>
> We are working towards the initial version.

[//]: # (Badges)
[//]: # (OPTIONAL)
[//]: # (Must not have its own title)


[//]: # (Short description)
[//]: # (REQUIRED)
[//]: # (An overview of the intentions of this repo)
[//]: # (Must not have its own title)
[//]: # (Must be less than 120 characters)
[//]: # (Must match GitHub's description)

Build the Kubernetes Lab from empty metal

[//]: # (Long Description)
[//]: # (OPTIONAL)
[//]: # (Must not have its own title)
[//]: # (A detailed description of the repo)

Uses Ansible to build an MVP controller, so that Cluster API and Tinkerbell can take over.

## Table of Contents

[//]: # (REQUIRED)
[//]: # (TOCGEN_TABLE_OF_CONTENTS_START)

- [Security](#security)
- [Background](#background)
- [Install](#install)
- [Usage](#usage)
- [Documentation](#documentation)
- [Repository Configuration](#repository-configuration)
- [Contributing](#contributing)
- [License](#license)
    - [Code](#code)
    - [Non-code content](#non-code-content)

[//]: # (TOCGEN_TABLE_OF_CONTENTS_END)

## Security
[//]: # (OPTIONAL)
[//]: # (May go here if it is important to highlight security concerns.)

Ansible uses obvious passwords, but these are replaced by SSH key auth once Kubernetes takes over.

## Background
[//]: # (OPTIONAL)
[//]: # (Explain the motivation and abstract dependencies for this repo)

Running your own metal has traditionally meant herding kittens. We wanted to keep the cloud native "feel", so it should
be as easy to replace a physical node as it is to replace a virtual one.

We, therefore, needed a way to provision that metal reliably and repeatably.

## Install

[//]: # (Explain how to install the thing.)
[//]: # (OPTIONAL IF documentation repo)
[//]: # (ELSE REQUIRED)

You will need,
- to install,
  - OpenTofu
  - Python3
  - Ansible
- A spare computer

## Usage
[//]: # (REQUIRED)
[//]: # (Explain what the thing does. Use screenshots and/or videos.)

To build the cluster from nothing,
1. Install Ubuntu server on a computer, setting the credentials to
    - Username: ubuntu
    - password: bootstrap
1. Ensure SSH is enabled, as it is disabled by default.
2. Connect all hosts to the kubernetes-lab VLAN
2. `cp .env.example .env` and add your real values to it.
1. run:

```shell
python3 bootstrap_runner
```

Your spare computer will go through the following stages,
1. Ansible will make it a Kubernetes Controller
2. Ansible will install Cluster API and Tinkerbell into the (currently single node) cluster.
3. Tinkerbell will provision the rest of the metal
4. Tinkerbell will reprovision the initial computer as a worker

From this point, Tinkerbell has ownership over all metal and is configured by Cluster API. This means we end up with
zero Ansible in use in our live cluster, which, from a "traditional" perspective, is remarkable.

[//]: # (Extra sections)
[//]: # (OPTIONAL)
[//]: # (This should not be called "Extra Sections".)
[//]: # (This is a space for ≥0 sections to be included,)
[//]: # (each of which must have their own titles.)


## Documentation

Further documentation is in the [`docs`](docs/) directory.

## Repository Configuration

> [!WARNING]
> This repo is controlled by OpenTofu in the [estate-repos](https://github.com/evoteum/estate-repos) repository.
>
> Manual configuration changes will be overwritten the next time OpenTofu runs.


[//]: # (## API)
[//]: # (OPTIONAL)
[//]: # (Describe exported functions and objects)



[//]: # (## Maintainers)
[//]: # (OPTIONAL)
[//]: # (List maintainers for this repository)
[//]: # (along with one way of contacting them - GitHub link or email.)



[//]: # (## Thanks)
[//]: # (OPTIONAL)
[//]: # (State anyone or anything that significantly)
[//]: # (helped with the development of this project)



## Contributing
[//]: # (REQUIRED)
If you need any help, please log an issue and one of our team will get back to you.

PRs are welcome.


## License
[//]: # (REQUIRED)

### Code

All source code in this repository is licenced under the [GNU Affero General Public License v3.0 (AGPL-3.0)](https://www.gnu.org/licenses/agpl-3.0.en.html). A copy of this is provided in the [LICENSE](LICENSE).

### Non-code content

All non-code content in this repository, including but not limited to images, diagrams or prose documentation, is licenced under the [Creative Commons Attribution-ShareAlike 4.0 International](https://creativecommons.org/licenses/by-sa/4.0/) licence.
