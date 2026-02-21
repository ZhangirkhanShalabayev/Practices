import json

with open('sample-data.json') as f:
    data = json.load(f)

print("Interface Status")
print("=" * 80)
print(f"{'DN':<50} {'Description':<20} {'Speed':<7} {'MTU':<6}")
print("-" * 50 + " " + "-" * 20 + "  " + "-" * 6 + "  " + "-" * 6)

interfaces = data.get("imdata", [])

for item in interfaces:
    attributes = item.get("l1PhysIf", {}).get("attributes", {})
    
    dn = attributes.get("dn", "")
    descr = attributes.get("descr", "")
    speed = attributes.get("speed", "inherit")
    mtu = attributes.get("mtu", "")
    
    print(f"{dn:<50} {descr:<20} {speed:<7} {mtu:<6}")