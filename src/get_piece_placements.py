import json
import requests
import lxml.html as lh
import pandas as pd
from collections import defaultdict
import numpy as np
from tqdm import tqdm

from constants import SQSIZE


def run(path, side_length, diameters):
    results = defaultdict(defaultdict)
    for diameter in tqdm(diameters):
        page = requests.get(path.format(side_length, diameter))
        doc = lh.fromstring(page.content)
        tr_elements = doc.xpath("//tr")
        col = []
        for t in tr_elements[0]:
            name = t.text_content().replace("\xa0", "").replace("\n", "")
            col.append((name, []))
        for tr in tr_elements[1:]:
            if len(tr) > 1:
                for i, t in enumerate(tr.iterchildren()):
                    data = t.text_content().replace("\xa0", "").replace("\n", "")
                    col[i][1].append(data)
        Dict = {title: column for (title, column) in col}
        df = (
            pd.DataFrame(Dict).drop(
                columns=["# circle"]
            ).apply(
                pd.to_numeric
                ).to_numpy() + SQSIZE // 2
        ).tolist()
        results[len(df)] = df
        return results


def main():
    path = "http://hydra.nat.uni-magdeburg.de/cgi-bin/csq1.pl?size={}&diameter={}&name=&addr="
    diameters = np.arange(1, 0.2, -0.001)
    results = run(path, SQSIZE, diameters)
    final_diameter_list = []
    for key in results.keys():
        final_diameter_list.append(max(results[key].keys()))
    results = run(path, final_diameter_list)
    return results

if __name__ == "__main__":
    results = main()
    with open("piece_placements.json", "w") as f:
        json.dump(results)
    