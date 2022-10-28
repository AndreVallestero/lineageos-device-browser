# pip install pyyaml
# pip install editdistance

from os import listdir, mkdir
from datetime import date
import yaml
import editdistance

DEVICES_DIR = "_data/devices/"
OUT_DIR = "_site/"

# Vendor, Name, Codename, Release Date, SOC, Latest LOS
DEVICE_TEMPLATE = """<tr>
<td>{}</td>
<td>{}</td>
<td><a href="https://wiki.lineageos.org/devices/{}/">{}</a></td>
<td>{}</td>
<td>{}</td>
<td>{}</td>
</tr>"""

def clean_release(release):
    if isinstance(release, date):
        return release.strftime('%Y-%m-%d')
    if isinstance(release, int):
        return str(release)
    return release

# Parse yaml
devices = []
for f in listdir(DEVICES_DIR):
    device = list(yaml.safe_load_all(open(DEVICES_DIR + f)))[0]
    if "/" in device["name"]: # multiple devices, need to split
        names = device["name"].split(" / ")
        for i, name in enumerate(names):

            # Create subdevice
            subdevice = {
                "name": name,
                "vendor": device["vendor"],
                "codename": device["codename"],
                "versions": device["versions"]}

            # Parse release date
            release = device["release"]
            if not isinstance(release, list):
                subdevice["release"] = clean_release(release)
            else:
                if len(names) == len(release):
                    subdevice["release"] = clean_release(list(release[i].values())[0])
                else:
                    # Check substring and also check edit distance incase no substring
                    clean_name = name.lower().replace(" ", "")
                    closest = 99
                    closest_release = None
                
                    for pair in release:
                        for key_name, value in pair.items():
                            clean_key = key_name.lower().replace(" ", "")
                            if clean_key in clean_name:
                                subdevice["release"] = clean_release(value)
                                break
                            dist = editdistance.eval(clean_name, clean_key)
                            if dist < closest:
                                closest = dist
                            closest_release = value
                        if "release" in subdevice: break
                    else:
                        subdevice["release"] = clean_release(closest_release)
                    
            
            soc = device["soc"]
            if isinstance(soc, str):
                subdevice["soc"] = soc
            elif isinstance(soc[i], str):
                subdevice["soc"] = soc[i]
            else:
                subdevice["soc"] = list(soc[i].values())[0]
            
            devices.append(subdevice)
    else:
        device["release"] = clean_release(device["release"])
        device["soc"] = device["soc"] if isinstance(device["soc"], str) else device["soc"][0]
        devices.append(device)

# Secondary sort by LOS version
devices.sort(key=lambda device: device["versions"][-1], reverse=True)
# Primary sort by release
devices.sort(key=lambda device: device["release"], reverse=True)

html_rows = "".join(DEVICE_TEMPLATE.format(
    device["vendor"],
    device["name"],
    device["codename"],
    device["codename"],
    device["release"],
    device["soc"],
    device["versions"][-1]) for device in devices)

template = open("index.html.template").read()
generated = template.format(html_rows)
mkdir(OUT_DIR)
open(OUT_DIR + "index.html", "w").write(generated)
    
          

