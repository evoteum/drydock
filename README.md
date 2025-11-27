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
> **Pre-pre-alpha**
>
> Drydock is currently in active design and initial prototyping. Some sections of this README describe intended
> behaviour before implementation.
> 
> Drydock is not production ready yet!

[//]: # (Badges)
[//]: # (OPTIONAL)
[//]: # (Must not have its own title)


[//]: # (Short description)
[//]: # (REQUIRED)
[//]: # (An overview of the intentions of this repo)
[//]: # (Must not have its own title)
[//]: # (Must be less than 120 characters)
[//]: # (Must match GitHub's description)

A harbour workshop where bare metal becomes a ready Kubernetes vessel.

[//]: # (Long Description)
[//]: # (OPTIONAL)
[//]: # (Must not have its own title)
[//]: # (A detailed description of the repo)

Drydock will provide a fully automated, Kubernetes-native bootstrap system that turns bare-metal hosts into a highly
available Kubernetes cluster with minimal manual intervention and a clean GitOps handover.

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

Drydock provides,
- default Kubernetes
- A CNI, default is Cilium
- Tinkerbell
- ClusterAPI
- ArgoCD

Drydock makes your nodes available to your cluster, it is up to you to secure your cluster. Follow the official
[Kubernetes Security documentation](https://Kubernetes.io/docs/concepts/security/) to harden your cluster
appropriately.

Drydock will, however, suggest hardened operating system base images for you to use.

## Background
[//]: # (OPTIONAL)
[//]: # (Explain the motivation and abstract dependencies for this repo)
### Metal 🤘
Running your own metal has traditionally meant herding cats. By this we mean,
- "cats vs cattle" an analogy in infrastructure management, which suggests that we should ideally treat our
servers like replaceable cattle, not like precious pet cats.
- "herding cats" is an idiom for something that is said to be impossible.

As such, in this case, running your own hardware has traditionally entailed treating each one like a special pet cat who
must be cared for individually. The fact that you may have a herd of these cats (technically a "clowder" but stick with
it), you must look after *many* special little cats individually, which leaves you *heading cats*. 

When you use a cloud provider, however, it is trivial to create and destroy servers at a moments notice. You can 
literally have 0 servers one minute, then create 1000 servers within the next minute, then destroy them all again the
next minute. The delivery guy might get a bit miffed if you tried to do that with your own hardware!

We wanted to keep the cloud native "feel", but with the control and predicability that comes with running your own
hardware. It should, therefore, be as easy to replace a physical node as it is to replace a virtual one.

We, therefore, needed a way to provision that metal,
- quickly.
- reliably.
- repeatably.

### Cloud ☁️

While cloud providers can be incredibly convenient and flexible, their bills can unpredictable. There is growing
interest in "de-clouding", either partially or completely, so that businesses can realise the cost savings that come
with owning, rather than renting, your hardware. Further details [below](#de-clouding).

### Why We are Building Drydock

- We like the elasticity and flexibility of cloud services.
- We believe in automation first.
- We choose to go to the Moon, not because it is easy, but because it is hard.

## Install

[//]: # (Explain how to install the thing.)
[//]: # (OPTIONAL IF documentation repo)
[//]: # (ELSE REQUIRED)

Installation will be available from all good package managers.

For a minimal, highly available Kubernetes cluster, you will need,
- 3 computers to use as controllers.
- 3 computers to use as workers.

This is the generally recommended Kubernetes structure, so is the one we are targeting first. Single controller clusters
will be supported later.

You will also need a router that allows you to create subnets, ideally one that can do so via API.

## Usage
[//]: # (REQUIRED)
[//]: # (Explain what the thing does. Use screenshots and/or videos.)
### Build
#### Manual Steps
We are aiming for the following workflow:

To build your cluster from bare metal,
1. Ensure network boot is enabled on all hosts (often enabled by default, but double check)
2. Set a new dedicated VLAN, and the physical ethernet ports you want to be associated with it, in the config.yaml
3. run:

```shell
drydock apply -f config.yaml
```

4. Drydock will make that VLAN
5. Drydock will ask you to connect all hosts to the ports you specified.

#### Drydock Automation
From there, Drydock will automatically,
1. Own DHCP on the specified VLAN
1. Spin up its PXE server
1. Boot your machines into SunshineOS
1. Discover hardware information
1. Emit [Tinkerbell hardware manifests](https://tinkerbell.org/docs/concepts/hardware/)
1. Build the cluster to the specification you declared in the config
1. Metal is then provisioned to Tinkerbell.
1. Provision the Drydock operator to continuously,
   - monitor the VLAN for new machines.
   - add and remove nodes from the cluster automatically, by updating the Tinkerbell inventory.

Job done. Now,
- you have a working, highly available, GitOps driven Kubernetes cluster.
- any new empty machines you add to the Kubernetes VLAN will automatically join the cluster.
- any machines that are removed from the VLAN for the time you specified will be removed from the cluster.

What a powerful single click that turned out to be!


### Destroy
When it comes time to rebuild or decommission the cluster, Drydock will be able to do that too.

```shell
drydock delete -f config.yaml
```

Drydock will then send [HerculesOS](https://github.com/evoteum/herculesos/) to wipe the disks of all, or specified,
nodes. Make sure nothing important is running first!

[//]: # (Extra sections)
[//]: # (OPTIONAL)
[//]: # (This should not be called "Extra Sections".)
[//]: # (This is a space for ≥0 sections to be included,)
[//]: # (each of which must have their own titles.)

## FAQ
### What do you mean by "metal"?
A physical computer that you own, and can ~~kick~~ caress when it misbehaves.

### Why is it named "Drydock"?
A Drydock is where ships are built before they are then launched to sea. Similarly, your empty server needs to be built
before it can be launched into the Kubernetes sea, so the Kubernetes Drydock does that for you.

We also like furthering the maritime theming of Kubernetes, as it makes for good analogies.

### Why does Drydock need to own DHCP on the Kubernetes VLAN?
Drydock owns DHCP on the Kubernetes VLAN so it can discover new hardware. Once Kubernetes is running, the Drydock
operator takes over DHCP management seamlessly. This prevents clashing with an pre-existing DHCP server, such as one
provided by the router.

### Why is this model safer and more reliable than traditional tooling?
Immutability.

Nodes will not be configured, they will be imaged. The exact same image will be deployed to all nodes in that node
group. This prevents any possibility of variation at deploy time, guaranteeing zero variance, and reducing debug hell. 

### How do rebuild and destroy flows maintain consistency?
Ensuring that everything was recently rebuilt ensures that nothing has a significant opportunity for drift.

### Why does API-driven provisioning beat playbooks?
Reconciliation.

Many traditional configuration management tools only correct drift when they run, which might be during CI or, if you
have set it up, on cron, such as hourly or daily. This gives machines a huge opportunity for drift.

The Drydock Kubernetes operator runs continuously. Any drift is detected within minutes and the node is immutably
reprovisioned.

### What language is Drydock written in?
Go.

The design of Drydock has evolved through,
- Bash (we underestimated how complex the challenge was!)
- Python, OpenTofu and Ansible 
- Python with Fabric

We then arrived at migrating the entire codebase to Go to improve,
- alignment with the Kubernetes ecosystem.
- ease of distribution.
- Kubernetes operator speed.

### Why not use an existing provisioning tool?
Sure, you could, as the BBC says, "Other providers are available." Existing tools solve part of the problem, however,
none offer all of the following end-to-end;
- a GitOps driven, Kubernetes native handoff. This is huge if you are running everything on Kubernetes.
- compatibility with lower powered devices. Not everyone wants to spend £10,000 per server.
- provisioning from nothing, also known as "day zero" provisioning. Many solutions assume you already have PXE infrastructure in place.
- hardware agnostic. Many solutions only work for that vendors hardware.
- the low low price of just £0 now, and £0 in 65 monthly installments. (Though we do appreciate any support you offer!)

Drydock will include all of these in one place.

Our target is to make Drydock the go solution for those who want,
- high quality, low cost
- Kubernetes
- their own hardware

### What is the usecase?
#### De-clouding
There is a growing need to optimise costs, and the ever-increasing and unpredictable cloud bill is frequently a key target. By running
your known, or "Business As Usual", workloads on machines that you own, you could make dramatic savings over renting
that compute from a cloud provider, then allowing you to make the most of the elasticity that cloud providers offer
through [Cloud Bursting](https://aws.amazon.com/what-is/cloud-bursting/).

In an SME context, we expect that Drydock will be most useful in getting a small, highly available Kubernetes management cluster running
in minutes, not days. This can then, in turn, be used to run almost anything else, including but not limited to,
- other Kubernetes clusters, in any provider, via [ClusterAPI](https://cluster-api.sigs.k8s.io/)
- your other servers, making them into immutable metal, via [Tinkerbell](https://tinkerbell.org/)
- other cloud infrastructure, via [Crossplane](https://www.crossplane.io/)

Many other Kubernetes plugins exist!

Equally, however, we also expect that Drydock could be used to directly set up massive Kubernetes clusters on metal.
Lots of options available to you.


> [!NOTE]  
> **Why?**
> 
> Give organisations the predictability of cloud provisioning while running cost-efficient hardware they
control.

#### Homelab
Over the last few years, interest has surged in,
- privacy
- home automation
- data sovereignty & independence

This has led to an increase in the number of people who want to run Kubernetes at home, so that they can self-host tools
such as,
- email
- Home Assistant
- photo hosting

Simultaneously, Kubernetes remains a hungry beast with a somewhat significant learning curve just to install, reducing
its accessibility. Drydock will improve that accessibility by making Kubernetes "just work™".

> [!NOTE]  
> **Why?**
> 
> Make Kubernetes easy for home users to get running so that they can self-host whatever they like.

## Documentation

Further documentation is in the [`docs`](docs/) directory.

## Repository Configuration

> [!WARNING]
> This repo is controlled by OpenTofu in the [estate-repos](https://github.com/evoteum/estate-repos) repository.
>
> Manual configuration changes will be overwritten the next time OpenTofu runs.


## API
[//]: # (OPTIONAL)
[//]: # (Describe exported functions and objects)

Like all things Kubernetes, Drydock will be API driven and configured by YAML.

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
