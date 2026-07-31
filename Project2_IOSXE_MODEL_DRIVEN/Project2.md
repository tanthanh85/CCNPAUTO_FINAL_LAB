# Project 2: Model-Driven Automation and Monitoring

## Business Scenario

Apex Global Services is modernizing its campus and WAN infrastructure. New IOS XE routers support NETCONF, RESTCONF, and YANG, so the network automation team wants to stop relying only on CLI screen scraping. The company has asked for a small model-driven automation project that can configure static routes from YAML, retrieve credentials from Vault, and expose a simple portal showing CPU, memory, and interface utilization.

Most of the project is already complete. Your job is to complete the missing model-driven parts.

## Points

Project 2 is worth **50 points**.

| Task | Requirement | Points |
|---|---|---:|
| 1 | Complete the Jinja2 loop in the Cisco IOS XE Native NETCONF template | 15 |
| 2 | Complete the Vault credential retrieval function | 20 |
| 3 | Locate and place Cisco IOS XE operational RESTCONF URIs for CPU, memory, and GigabitEthernet1 | 15 |

## Project Repository

Complete this assessment inside the cloned GitLab repository:

```text
~/ccnpauto-workspace/final_assessment/ccnpauto-final-project2-iosxe
```

Before beginning Task 1, follow the main assessment guide to create the
private `ccnpauto-final-project2-iosxe` project, clone it, and use VS Code to
copy all supplied Project 2 starter content into the clone, including
`.env.example`. Confirm that the starter commit has been pushed to GitLab.com.

## Project Files

```text
Project2_IOSXE_MODEL_DRIVEN/
├── .env.example
├── .env                 # Learner-created and not committed
├── Project2.md
├── README.md
├── app.py
├── data/
│   └── static_routes.yaml
├── requirements.txt
├── scripts/
│   ├── configure_static_routes.py
│   └── grade_project2.py
├── src/
│   ├── restconf_monitor.py
│   ├── route_source.py
│   ├── settings.py
│   └── vault_credentials.py
├── static/
│   └── portal.css
├── templates/
│   └── static_routes.xml.j2
└── templates_flask/
    └── portal.html
```

## Task 1: Complete the Jinja2 Loop

Before editing project files, create a Python virtual environment and install the required libraries:

```bash
python3 -m venv final_lab2
source final_lab2/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The dependency list includes `xmltodict`, which the project uses only to
check whether the NETCONF XML reply contains `<ok/>`. The installable package
and Python module are both named `xmltodict`.

Static-route intent is already defined in [data/static_routes.yaml](data/static_routes.yaml). The starter template contains the NETCONF `<config>` root and the complete Cisco IOS XE Native `native/ip/route` XML structure. However, the Jinja2 loop has been removed. Your task is to add the opening and closing loop statements in [templates/static_routes.xml.j2](templates/static_routes.xml.j2) so that every route in the YAML list produces one XML route entry.

In Yangsuite, choose **`Cisco-IOS-XE-native`** with its dependencies. Do not use OpenConfig or the generic IETF routing model for this task. The native static-route hierarchy accepts the destination address and subnet mask as separate values, matching the supplied YAML source.

Use Yangsuite to understand and verify the supplied XML structure:

1. In **Setup > Device profiles**, create or refresh the IOS XE reservation profile with NETCONF port `830`.
2. In **Setup > YANG files and repositories**, retrieve the schema list from that device and download `Cisco-IOS-XE-native` with its dependencies.
3. Add those files to a YANG module set.
4. In **Protocols > NETCONF**, select the device and module set, load `Cisco-IOS-XE-native`, and locate the `native/ip/route` subtree.
5. Build one sample `edit-config` request and compare its `<config>` body with the supplied template.
6. Confirm that the supplied `prefix`, `mask`, `fwd-list`, and `fwd` elements follow the hierarchy exposed by the reserved router.
7. Leave the supplied XML elements and variables in place. Only add the missing opening and closing Jinja2 loop statements.

The YAML format is:

```yaml
static_routes:
  - prefix: 203.0.113.0
    mask: 255.255.255.0
    next_hop: 10.10.20.254
    description: Example business route
```

### Jinja2 Syntax Used in This Task

Jinja2 uses two different delimiter styles in this template:

- `{{ variable }}` prints a value into the rendered XML. The supplied XML already uses `{{ route.prefix }}`, `{{ route.mask }}`, and `{{ route.next_hop }}`.
- `{% statement %}` controls template logic. A `for` statement repeats a block, while `endfor` marks the end of that repeated block.

Keep one space after the opening delimiter and one space before the closing delimiter. For example, write `{{ route.prefix }}` rather than `{{route.prefix}}`, and write `{% for route in static_routes %}` rather than `{%for route in static_routes%}`. Jinja2 may accept compressed forms, but consistent spacing makes templates much easier to read and troubleshoot.

Open [templates/static_routes.xml.j2](templates/static_routes.xml.j2). Add the opening loop immediately before `<ip-route-interface-forwarding-list>` and add the closing statement immediately after that element:

```jinja2
{% for route in static_routes %}
  <!-- The supplied Cisco Native static-route XML is repeated here. -->
{% endfor %}
```

Do not add another `<config>`, `<native>`, `<ip>`, or `<route>` element inside the loop. Those parent elements already exist and must appear only once in the payload.

When the YAML file contains two or more routes, the rendered XML should contain two or more `ip-route-interface-forwarding-list` entries. This confirms that the loop operates on the entire `static_routes` list rather than rendering only one hard-coded route.

After completing the template, first create `.env` if it does not exist. Open `.env.example` in VS Code, create `.env` in the project root, and copy and paste the example content into it. Enter the active reservation values, then render the template:

The project loads this file automatically with `python-dotenv`. Do not run
`source .env` and do not export the IOS XE or Vault variables manually.

```bash
source final_lab2/bin/activate
python scripts/configure_static_routes.py --dry-run
```

Then add a second route to [data/static_routes.yaml](data/static_routes.yaml) and run the dry run again. If the rendered XML now contains both static routes, configure the routes:

```bash
python scripts/configure_static_routes.py
```

After `ncclient` sends the `<edit-config>` request, the router returns an XML
`<rpc-reply>`. The supplied code parses the reply and checks for `<ok/>`:

```python
reply = xmltodict.parse(response.xml)
rpc_reply = reply.get("rpc-reply", {})

if isinstance(rpc_reply, dict) and "ok" in rpc_reply:
    print("NETCONF result: configuration accepted")
else:
    print("NETCONF result: <ok/> was not returned")
```

No additional response interpretation is required for this assessment.

Verify on the router:

```text
show ip route static
```

## Task 2: Move IOS XE Credentials to Vault

The project can initially read credentials from environment variables. Your task is to complete the Vault integration so the script can retrieve IOS XE credentials from Vault.

Start Vault if it is not running:

```bash
vault server -dev -dev-root-token-id=root
```

In another terminal:

```bash
VAULT_ADDR=http://127.0.0.1:8200 VAULT_TOKEN=root \
  vault kv put secret/ccnpauto/final/iosxe \
  username='<iosxe-username>' \
  password='<iosxe-password>'
```

Open the project-root `.env` file. Change the existing setting from
`USE_VAULT=false` to `USE_VAULT=true`, and confirm that the remaining Vault
settings match the service you started:

```text
USE_VAULT=true
VAULT_ADDR=http://127.0.0.1:8200
VAULT_TOKEN=root
VAULT_SECRET_PATH=ccnpauto/final/iosxe
```

The inline variables above apply only to the single Vault CLI command. The
Python application reads the same Vault settings automatically from the
project-root `.env` file. If `USE_VAULT` remains `false`, the application will
continue reading `IOSXE_USERNAME` and `IOSXE_PASSWORD` instead of calling your
Vault function.

Open [src/vault_credentials.py](src/vault_credentials.py) and complete `get_iosxe_credentials_from_vault()`.

The function should:

- create an `hvac.Client`,
- authenticate with `VAULT_ADDR` and `VAULT_TOKEN`,
- read the KV version 2 secret from `VAULT_SECRET_PATH`,
- and return a dictionary with `username` and `password`.

Do not use `print(data)` or print the returned username, password, Vault token,
or complete Vault response. The Flask dashboard refreshes every five seconds,
so a debugging print inside this function would repeatedly expose the router
credentials in the terminal. While troubleshooting, inspect only
non-sensitive status information, such as whether the Vault client is
authenticated.

After adding the working code, comment out the original placeholder at the end
of the function:

```python
# raise NotImplementedError("Complete Vault credential retrieval for the final lab")
```

Do not leave the `raise NotImplementedError(...)` statement active, even when
it appears after your `return` statement. The grader checks that the starter
placeholder has been deliberately disabled.

Before testing, check `.env` once more and confirm that it contains
`USE_VAULT=true`. Stop and restart the Python script or Flask portal after
changing this setting so the new process loads the updated environment.

After completing the function, add one more static route to [data/static_routes.yaml](data/static_routes.yaml), rerun the script, and verify the new route.

## Task 3: Complete Cisco IOS XE RESTCONF Monitoring URIs

The project includes a responsive Flask operations dashboard that refreshes every 5 seconds and maintains a rolling history of 60 samples. It presents line charts for CPU utilization, used memory, GigabitEthernet1 input packet rate, and GigabitEthernet1 output packet rate. Most of the code is complete, but the Cisco IOS XE operational RESTCONF URIs are missing.

Use local Cisco Yangsuite or Cisco DevNet Sandbox Yangsuite at `http://10.10.20.50:8480` to locate operational paths for:

- five-second CPU utilization under `Cisco-IOS-XE-process-cpu-oper`,
- the memory-pool list under `Cisco-IOS-XE-memory-oper`,
- and the `GigabitEthernet1` statistics container under `Cisco-IOS-XE-interfaces-oper`, including `rx-pps` and `tx-pps`.

The monitoring code expects the complete memory-pool list. It then selects the pool whose `name` is `Processor` and reads its `used-memory` value. In contrast, the CPU request addresses one value directly, while the interface request addresses a statistics node that returns both `rx-pps` and `tx-pps`.

### Locate the paths in Yangsuite

1. Open Yangsuite and select **Setup > Device profiles**. Select the profile for the active IOS XE reservation and confirm that its NETCONF connection is available.
2. Select **Setup > YANG files and repositories**, then confirm that the device YANG set contains `Cisco-IOS-XE-process-cpu-oper`, `Cisco-IOS-XE-memory-oper`, and `Cisco-IOS-XE-interfaces-oper` together with their dependencies.
3. Open **Protocols > RESTCONF**. Select the IOS XE device profile and its YANG set.
4. For CPU, load `Cisco-IOS-XE-process-cpu-oper`. Search the model for the `five-seconds` leaf, select it, and generate its RESTCONF `GET` API.
5. For memory, load `Cisco-IOS-XE-memory-oper`. Search for the `memory-statistic` node and select the complete list rather than one keyed list entry or only the `used-memory` child. Generate its RESTCONF `GET` API. Yangsuite identifies a list with its key, so confirm that `name` is shown as the key before continuing.
6. For interface packet rates, load `Cisco-IOS-XE-interfaces-oper`. Search for the `statistics` node beneath an interface. Select the statistics container rather than an individual counter. When Yangsuite requests the interface list key, enter `GigabitEthernet1`, and then generate the RESTCONF `GET` API.
7. Study each generated URL and determine the resource path required by the Python program. Keep only the portion that follows `/restconf/data`. Do not copy a Yangsuite proxy hostname, the router hostname, or `/restconf/data` into the Python constants.

### Validate the paths with Postman

For each of the three resource paths:

1. Validate the request directly against IOS XE with Postman.
2. Open Postman and create a new **HTTP Request**. Set the method to `GET` and
   enter the direct IOS XE URL:

   ```text
   https://<IOSXE_HOST>:<IOSXE_RESTCONF_PORT>/restconf/data/<generated-resource-path>
   ```

3. On the **Authorization** tab, select **Basic Auth** and enter the active IOS
   XE reservation username and password.
4. On the **Headers** tab, add:

   ```text
   Accept: application/yang-data+json
   ```

5. The sandbox normally uses a self-signed HTTPS certificate. For this
   controlled assessment only, open **Postman Settings > General** and disable
   **SSL certificate verification** if certificate validation prevents the
   request.
6. Select **Send** and confirm that IOS XE returns `200 OK`. Inspect the JSON
    response and verify that the CPU request contains `five-seconds`, the
    memory request contains `used-memory`, and the interface statistics
    request contains both `rx-pps` and `tx-pps`.
7. For memory, locate the object whose `name` is `Processor` and confirm that it contains `used-memory`. The Python code selects this record from the returned list.
8. Repeat the Postman request for CPU, memory, and interface data before
    placing any resource path into Python.

Open [src/restconf_monitor.py](src/restconf_monitor.py) and complete:

```python
CPU_URI = ""
MEMORY_URI = ""
INTERFACE_GIG1_URI = ""
```

Place the RESTCONF data paths only. Do not include the scheme, hostname, or `/restconf/data` base in these constants. The code adds the base URL automatically.

Do not guess the paths or copy them from another IOS XE model. Generate each path in Yangsuite, validate it with Postman, and then enter it into the corresponding constant. The self-grader awards five points for each correct path.

Run the portal:

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5060
```

The dashboard should display four current values and four line charts. CPU is shown as a percentage, memory is converted to an appropriate binary unit, and the two GigabitEthernet1 charts show packets per second. Leave the page open for at least 30 seconds and confirm that each chart receives multiple samples.

## Self-Grading

Run:

```bash
python scripts/grade_project2.py
```

The grader reports your score out of 50. For every incomplete task, it
identifies the missing points and states what is required for full credit.
Correct the reported requirement and rerun the grader. The local checks
validate structure and completion; they do not replace NETCONF deployment,
Vault retrieval, RESTCONF `200 OK`, or portal verification against the
reserved router.

## Notes

If a RESTCONF or NETCONF path does not work on your IOS XE sandbox release, verify the model with local or Cisco DevNet Sandbox Yangsuite. The model exposed by the device is authoritative.

## Submit Project 2

After the grader reports the expected result and the router and portal have
been verified, review `git status`. Stage only the solution files; do not
stage `.env`, credentials, Vault tokens, or `final_lab2`.

```bash
git add data/static_routes.yaml templates/static_routes.xml.j2
git add src/vault_credentials.py src/restconf_monitor.py
git commit -m "Complete IOS XE model-driven automation assessment"
git push origin main
git status
```

Open the GitLab.com project and confirm that the latest commit and completed
source files are visible.
