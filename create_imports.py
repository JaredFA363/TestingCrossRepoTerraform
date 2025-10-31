import re
import json
import sys

def parse_terraform_plan(plan_text):
    # Regex to find each resource block starting with a line like:
    #   # atlassian-operations_email_integration.email_v2["default"] will be imported
    block_pattern = re.compile(
        r'#\s+(?P<header>[^\n]+)\n(.*?)(?=\n\s*#|\Z)',
        re.DOTALL
    )

    results = []

    for match in block_pattern.finditer(plan_text):
        header = match.group('header').strip()
        block = match.group(0)

        # Extract team_id and id
        team_id_match = re.search(r'team_id\s*=\s*"([^"]+)"', block)
        id_match = re.search(r'\bid\s*=\s*"([^"]+)"', block)

        team_id = team_id_match.group(1) if team_id_match else ""
        resource_id = id_match.group(1) if id_match else ""

        results.append({
            "resource": header.split(" will ")[0].strip(),
            "team_id": team_id,
            "id": resource_id
        })

    return results

def create_terraform_imports(json_resource_data):
    imports = []
    for resource in json_resource_data:
        import_command = "import {\n  for_each = local.squad == \"" + "cc" + "\" ? toset([\"a\"]) : toset([])\n  to = " + resource["resource"] + "\n  id = \"" + resource["id"] + "," + resource["team_id"] + "\"\n}\n\n"
        imports.append(import_command)
    return imports

def create_terraform_imports_file(imports):
    with open("terraform_imports.tf", "w") as f:
        f.writelines(imports)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python parse_tf_plan.py <terraform_plan.txt>")
        sys.exit(1)

    filename = sys.argv[1]
    with open(filename, "r") as f:
        plan_text = f.read()

    parsed = parse_terraform_plan(plan_text)
    print(json.dumps(parsed, indent=2))

    imports = create_terraform_imports(parsed)
    create_terraform_imports_file(imports)
