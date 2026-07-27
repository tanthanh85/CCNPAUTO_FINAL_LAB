# Final Assessment Lab: Enterprise Network Automation Delivery

## Scenario

You are part of the network automation team for **Apex Global Services**, a company that operates both legacy data-center networks and newer programmable campus infrastructure. The business has asked your team to reduce manual configuration work, improve change consistency, and provide simple operational visibility for support engineers.

The environment is mixed. Some older devices do not expose modern model-driven interfaces, so the team still needs CLI-based automation. Newer IOS XE devices support NETCONF, RESTCONF, and YANG, so the team wants model-driven automation for those platforms. The company also recently adopted a basic secrets-management policy, which means device credentials should not remain hard-coded or scattered across local files.

You have inherited two mostly completed automation projects. Your job is to complete the missing parts, run the projects, and use the self-grading scripts to confirm your result.

## Time Allowed

You have **4 hours** to complete the final lab.

## Assessment Structure

| Project | Topic | Platform | Max Points |
|---|---|---|---:|
| Project 1 | CLI automation for legacy devices | Cisco Nexus NX-OS sandbox switch | 50 |
| Project 2 | Model-driven automation and monitoring | Cisco IOS XE reservable sandbox router | 50 |
| **Total** |  |  | **100** |

## Required Lab Access

You need access to:

- Cisco Nexus NX-OS sandbox switch
- Cisco IOS XE reservable sandbox router
- Access to local Cisco Yangsuite at `https://localhost:8443` or Cisco DevNet Sandbox Yangsuite at `http://10.10.20.50:8480`
- HashiCorp Vault from Lab 1

The assessment does not use NetBox, TIG, or GitLab Runner. Stop them to preserve workstation resources, then verify Vault and the selected Yangsuite option:

```bash
test -d "$HOME/lab-services/netbox-docker" && \
  (cd "$HOME/lab-services/netbox-docker" && docker compose stop)
test -d "$HOME/lab-services/tig" && \
  (cd "$HOME/lab-services/tig" && docker compose stop)
sudo systemctl stop gitlab-runner
vault status
```

If `vault status` fails, start the development server in a dedicated terminal and recreate the assessment secret. For local Yangsuite, start it from `~/lab-services/yangsuite/docker`; otherwise open Cisco DevNet Sandbox Yangsuite at `http://10.10.20.50:8480`.

Both projects use `python-dotenv` and load `.env` explicitly from their own
project root. Learners edit the file but do not run `source .env` or maintain
connection variables with shell `export` commands. Activating `final_lab1` or
`final_lab2` is still required to select the correct Python interpreter and
installed packages.

## Create the Two GitLab Projects

Each assessment project must have its own private GitLab.com repository. Do
not place both projects in one repository.

Create these projects:

| Assessment project | GitLab project name |
|---|---|
| Project 1 | `ccnpauto-final-project1-nxos` |
| Project 2 | `ccnpauto-final-project2-iosxe` |

For each project:

1. Sign in to GitLab.com.
2. Select **New project/repository**.
3. Select **Create blank project**.
4. Enter the project name shown in the table.
5. Set **Visibility Level** to **Private**.
6. Clear **Initialize repository with a README**. The supplied assessment
   files will provide the first commit.
7. Select **Create project**.
8. On the new project page, select **Code > Clone with SSH** and copy the SSH
   URL. Use **Clone with HTTPS** only if SSH access has not been configured.

## Clone the Two Repositories

Create the assessment workspace:

```bash
mkdir -p ~/ccnpauto-workspace/final_assessment
cd ~/ccnpauto-workspace/final_assessment
```

Clone both empty repositories, replacing `<gitlab-username>` with the
learner's GitLab.com namespace:

```bash
git clone git@gitlab.com:<gitlab-username>/ccnpauto-final-project1-nxos.git
git clone git@gitlab.com:<gitlab-username>/ccnpauto-final-project2-iosxe.git
```

If Git reports that an empty repository was cloned, that is expected.

## Copy the Starter Files with VS Code

Use VS Code rather than an Ubuntu `cp` command so the source and destination
are visually clear.

For Project 1:

1. Open a new VS Code window and open the supplied
   `CCNPAUTO_FINAL_LAB/Project1_NXOS_CLI_VLAN/` folder.
2. Open a second VS Code window and open the cloned
   `~/ccnpauto-workspace/final_assessment/ccnpauto-final-project1-nxos/`
   folder.
3. In the source Explorer, select `Project1.md`, `requirements.txt`, `data`,
   `scripts`, `src`, and `templates`.
4. Copy and paste those items into the root of the cloned repository.

For Project 2:

1. Open the supplied
   `CCNPAUTO_FINAL_LAB/Project2_IOSXE_MODEL_DRIVEN/` folder in VS Code.
2. Open the cloned
   `~/ccnpauto-workspace/final_assessment/ccnpauto-final-project2-iosxe/`
   folder in another VS Code window.
3. Select and copy all supplied Project 2 files and folders, including the
   hidden `.env.example`.
4. Paste them into the root of the cloned repository.

Copy only the contents of the two supplied project folders. Do not copy the
top-level `CCNPAUTO_FINAL_LAB/.git` folder into either learner repository.

Create a starter commit in each clone before solving the tasks:

```bash
cd ~/ccnpauto-workspace/final_assessment/ccnpauto-final-project1-nxos
git add .
git commit -m "Add Project 1 starter files"
git branch -M main
git push -u origin main

cd ~/ccnpauto-workspace/final_assessment/ccnpauto-final-project2-iosxe
git add .
git commit -m "Add Project 2 starter files"
git branch -M main
git push -u origin main
```

## Python Environment and Required Libraries

Each project includes its own `requirements.txt` file. Use a separate virtual
environment inside each project folder so one project's dependencies do not
hide a dependency fault in the other project. Name the Project 1 environment
`final_lab1` and the Project 2 environment `final_lab2`.

Prepare Project 1 first:

```bash
cd ~/ccnpauto-workspace/final_assessment/ccnpauto-final-project1-nxos
python3 -m venv final_lab1
source final_lab1/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

After finishing Project 1, deactivate its environment and prepare Project 2:

```bash
deactivate
cd ~/ccnpauto-workspace/final_assessment/ccnpauto-final-project2-iosxe
python3 -m venv final_lab2
source final_lab2/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Project 1 deliberately omits a runtime-configuration example. Learners must
trace the Python imports and settings code to determine the configuration
mechanism, local filename, and variable names expected by the NX-OS
application. Project 2 supplies `.env.example` because its assessment focus is
Vault, NETCONF, RESTCONF, and monitoring rather than environment discovery.
Never commit a local secret file or place real credentials in an example
file.

## Project 1 Overview: CLI automation for legacy devices

Project 1 represents a legacy data-center automation task. The Nexus switch does not use NETCONF or RESTCONF in this project. Your automation must use SSH CLI through Netmiko and create VLANs from YAML intent.

You need to complete five tasks:

1. Diagnose the missing template-rendering Python dependency and install the
   package that supplies the imported module.
2. Trace the Python settings flow, identify the missing runtime configuration,
   and supply the Nexus reservation values without hard-coding secrets.
3. Construct the Jinja2 template that renders VLAN configuration from YAML.
4. Troubleshoot the incomplete Netmiko `device` dictionary and select the
   correct Nexus NX-OS platform identifier for `ConnectHandler(**device)`.
5. Handle `NetmikoAuthenticationException` and `NetmikoTimeoutException` with clear, failure-specific messages.

Each Project 1 task is worth 10 points, for a total of 50.

Run the self-grader from the project folder:

```bash
cd ~/ccnpauto-workspace/final_assessment/ccnpauto-final-project1-nxos
python -m pip install -r requirements.txt
python scripts/grade_project1.py
```

Project 1 is worth **50 points**.

After completing and verifying Project 1, stage only the solution source files.
Do not stage the learner-created secret file or the `final_lab1` virtual
environment:

```bash
git status
git add requirements.txt templates/vlans.j2 src/device.py scripts/apply_vlans.py
git commit -m "Complete NX-OS VLAN automation assessment"
git push origin main
git status
```

## Project 2 Overview: Model-Driven Automation and Monitoring

Project 2 represents a newer programmable network platform. The IOS XE router supports NETCONF and RESTCONF. The project includes static-route automation, Vault credential retrieval, and a small management portal that monitors CPU, memory, and GigabitEthernet1 utilization.

You need to complete three tasks:

1. Use local Cisco Yangsuite or Cisco DevNet Sandbox Yangsuite at `http://10.10.20.50:8480` to construct the XML structure for static routes with `Cisco-IOS-XE-native`, then convert it into a Jinja2 template with a loop over the YAML route list.
2. Complete the Vault credential retrieval function.
3. Use local or Cisco DevNet Sandbox Yangsuite to locate Cisco IOS XE operational RESTCONF URIs for CPU, memory, and GigabitEthernet1 monitoring, then place those URIs into the code.

Run the self-grader from the project folder:

```bash
cd ~/ccnpauto-workspace/final_assessment/ccnpauto-final-project2-iosxe
python -m pip install -r requirements.txt
python scripts/grade_project2.py
```

Project 2 is worth **50 points**.

After completing and verifying Project 2, stage only the files changed by the
solution. Do not stage `.env`, Vault tokens, passwords, or the `final_lab2`
virtual environment:

```bash
git status
git add data/static_routes.yaml templates/static_routes.xml.j2
git add src/vault_credentials.py src/restconf_monitor.py
git commit -m "Complete IOS XE model-driven automation assessment"
git push origin main
git status
```

## Submission Evidence

Your instructor may ask for:

- completed project files,
- self-grader output,
- screenshots showing successful VLAN/static-route deployment,
- screenshot of the monitoring portal,
- and Git commit history.

Do not submit real passwords, Vault tokens, or private keys.

## Final Reminder

The assessment is designed to test practical judgment, not memorization. Use
the tools you practised earlier: environment-based runtime configuration,
Vault for secrets, Jinja2 for rendering, YAML for intent, local or Cisco
DevNet Sandbox Yangsuite for model discovery, Netmiko for CLI devices,
NETCONF for model-driven configuration, RESTCONF for operational data, and
Flask for a simple operational portal.
