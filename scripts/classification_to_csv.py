import json
import csv

def extract_hierarchy(json_path, csv_path):
    # load JSON
    with open(json_path, 'r') as f:
        data = json.load(f)

    # flatten top-level lists into one groups list
    groups = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, list):
                groups.extend(item)
            elif isinstance(item, dict):
                groups.append(item)
    else:
        raise ValueError("Expected top-level list in JSON")

    # open CSV and write header
    with open(csv_path, 'w', newline='') as outf:
        writer = csv.writer(outf)
        writer.writerow(['index', 'group', 'family', 'subfamily', 'protein', 'uniprot'])

        idx = 1
        for grp in groups:
            gname = grp.get('value', '')

            for fam in grp.get('nodes', []):
                fname = fam.get('value', '')
                # group + family
                writer.writerow([idx, gname, fname, '', '', ''])
                idx += 1

                for node in fam.get('nodes', []):
                    ntype = node.get('type', '')
                    if ntype == 'subfamily':
                        sf = node.get('value', '')
                        writer.writerow([idx, gname, fname, sf, '', ''])
                        idx += 1
                        for prot in node.get('nodes', []):
                            pname = prot.get('value', '')
                            uid   = prot.get('uniprot', '')
                            writer.writerow([idx, gname, fname, sf, pname, uid])
                            idx += 1

                    elif ntype == 'protein':
                        pname = node.get('value', '')
                        uid   = node.get('uniprot', '')
                        writer.writerow([idx, gname, fname, '', pname, uid])
                        idx += 1

if __name__ == '__main__':
    extract_hierarchy('./data/classification.json', './data/classification.csv')
    print("Wrote classification.csv")