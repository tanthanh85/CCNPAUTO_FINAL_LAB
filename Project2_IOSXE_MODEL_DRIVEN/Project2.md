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
4. Open **Explore**, select the IOS XE YANG set, load `Cisco-IOS-XE-native`, and expand the tree to `native/ip/route`. Select the route nodes and use the XPath shown by Yangsuite to confirm their location in the model.
5. In **Protocols > NETCONF**, build one sample `edit-config` request and compare its `<config>` body with the supplied template.
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
nano .env
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

Update `.env`:

```text
USE_VAULT=true
VAULT_ADDR=http://127.0.0.1:8200
VAULT_TOKEN=root
VAULT_SECRET_PATH=ccnpauto/final/iosxe
```

The inline variables above apply only to the single Vault CLI command. The
Python application reads the same Vault settings automatically from the
project-root `.env` file.

Open [src/vault_credentials.py](src/vault_credentials.py) and complete `get_iosxe_credentials_from_vault()`.

The function should:

- create an `hvac.Client`,
- authenticate with `VAULT_ADDR` and `VAULT_TOKEN`,
- read the KV version 2 secret from `VAULT_SECRET_PATH`,
- and return a dictionary with `username` and `password`.

After adding the working code, comment out the original placeholder at the end
of the function:

```python
# raise NotImplementedError("Complete Vault credential retrieval for the final lab")
```

Do not leave the `raise NotImplementedError(...)` statement active, even when
it appears after your `return` statement. The grader checks that the starter
placeholder has been deliberately disabled.

After completing the function, add one more static route to [data/static_routes.yaml](data/static_routes.yaml), rerun the script, and verify the new route.

## Task 3: Complete Cisco IOS XE RESTCONF Monitoring URIs

The project includes a small Flask management portal that refreshes every 5 seconds. Most of the code is complete, but the Cisco IOS XE operational RESTCONF URIs are missing.

Use local Cisco Yangsuite or Cisco DevNet Sandbox Yangsuite at `http://10.10.20.50:8480` to locate operational paths for:

- five-second CPU utilization under `Cisco-IOS-XE-process-cpu-oper`,
- used processor memory under `Cisco-IOS-XE-memory-oper`,
- and input octets for `GigabitEthernet1` under `Cisco-IOS-XE-interfaces-oper`.

For CPU, inspect `cpu-usage/cpu-utilization/five-seconds`. For memory, inspect `memory-statistics/memory-statistic`, select the processor-memory list entry exposed by the device, and locate `used-memory`. For the interface, inspect `interfaces/interface/statistics` and select `in-octets`. Let Yangsuite generate the exact RESTCONF list-key syntax used by the active IOS XE image.

For each metric, first use **Explore** to identify the correct model XPath and
then use the RESTCONF tool to generate the corresponding resource URI:

1. Use the device profile and the YANG set downloaded from the active IOS XE reservation.
2. Confirm that the module set includes `Cisco-IOS-XE-process-cpu-oper`, `Cisco-IOS-XE-memory-oper`, and `Cisco-IOS-XE-interfaces-oper` with their dependencies.
3. Open **Explore** from the Yangsuite menu and select the IOS XE YANG set.
4. Select the relevant operational module. Use the tree search to locate the required leaf, then expand its parent containers and lists so that the complete hierarchy is visible.
5. Select the leaf and record the XPath displayed by Yangsuite. Confirm that the XPath begins in the correct module and ends at the required leaf:

   ```text
   CPU:       /process-cpu-ios-xe-oper:cpu-usage/cpu-utilization/five-seconds
   Memory:    /memory-ios-xe-oper:memory-statistics/memory-statistic/.../used-memory
   Interface: /interfaces-ios-xe-oper:interfaces/interface/.../statistics/in-octets
   ```

   The ellipses indicate list-key selections that must come from the active
   device. Do not paste the ellipses into a request.
6. For a list such as `memory-statistic` or `interface`, inspect its key leaf in **Explore**. Record the processor-memory key returned by the router and the interface key `GigabitEthernet1`. This step prevents learners from guessing the list-key order or syntax.
7. After confirming the XPath, select **Protocols > RESTCONF**, load the same module, locate the same node, and choose **Generate APIs**. Yangsuite translates the selected model path and list keys into a RESTCONF resource URI.
8. Use the generated API information to identify the `GET` resource path.
   Copy the device resource path that follows `/restconf/data/`; do not copy a
   Yangsuite proxy hostname or proxy prefix. Validate the request directly
   against IOS XE with Postman.
9. Open Postman and create a new **HTTP Request**. Set the method to `GET` and
   enter the direct IOS XE URL:

   ```text
   https://<IOSXE_HOST>:<IOSXE_RESTCONF_PORT>/restconf/data/<generated-resource-path>
   ```

10. On the **Authorization** tab, select **Basic Auth** and enter the active IOS
   XE reservation username and password.
11. On the **Headers** tab, add:

   ```text
   Accept: application/yang-data+json
   ```

12. The sandbox normally uses a self-signed HTTPS certificate. For this
   controlled assessment only, open **Postman Settings > General** and disable
   **SSL certificate verification** if certificate validation prevents the
   request.
13. Select **Send** and confirm that IOS XE returns `200 OK`. Inspect the JSON
   response and verify that it includes the field consumed by the portal.
14. When selecting a memory or interface list entry, allow Yangsuite to
    generate the RESTCONF list-key syntax. Use the processor-memory entry
    exposed by the device and the `GigabitEthernet1` interface entry; do not
    paste an XPath predicate into a RESTCONF URI.
15. Repeat the Postman request for CPU, memory, and interface data before
    placing any resource path into Python.

An XPath describes a node in the YANG data tree and normally uses the YANG
module prefix, such as `process-cpu-ios-xe-oper`. A RESTCONF URI identifies
that node as an HTTP resource and commonly begins with the module name, such
as `Cisco-IOS-XE-process-cpu-oper:cpu-usage`. Use **Explore** to prove that the
model path is correct, but place only the generated RESTCONF resource path in
`restconf_monitor.py`.

Open [src/restconf_monitor.py](src/restconf_monitor.py) and complete:

```python
CPU_URI = ""
MEMORY_URI = ""
INTERFACE_GIG1_URI = ""
```

Place the RESTCONF data paths only. Do not include the scheme, hostname, or `/restconf/data` base in these constants. The code adds the base URL automatically.

Use this format:

```python
CPU_URI = "/Cisco-IOS-XE-process-cpu-oper:..."
MEMORY_URI = "/Cisco-IOS-XE-memory-oper:..."
INTERFACE_GIG1_URI = "/Cisco-IOS-XE-interfaces-oper:..."
```

Run the portal:

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5060
```

The portal should show CPU, memory, and GigabitEthernet1 information and refresh automatically.

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
