"""This script generates the positions in a square to place the pieces that it contains.
It assumes that each piece in a square is a circle with radius r.
It then solves the circle packing problem to pack the piece circles in a square of length
SQSIZE.

Instead of solving the problem, we use the API available at:
"http://hydra.nat.uni-magdeburg.de/cgi-bin/csq1.pl?size={<enter_square_length>}&diameter={<enter_circle_diameter>}&name=&addr="

The piece positions are saved to src/piece_placements.json as a dictionary where
the keys are the number of pieces and the values are a list of positions for those pieces.
"""

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
            pd.DataFrame(Dict)
            .drop(columns=["# circle"])
            .apply(pd.to_numeric)
            .to_numpy()
            + SQSIZE // 2
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
