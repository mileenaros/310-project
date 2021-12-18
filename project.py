import json
import urllib.error
import urllib.parse
import urllib.request
from flask import Flask, render_template, request
from random import randint, shuffle

app = Flask(__name__)


# from previous homeworks
def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)


# urls
met_url = "https://collectionapi.metmuseum.org/public/collection/v1/"


# my methods
def safe_get(request_url):
    try:
        f = urllib.request.urlopen(request_url)
        request = f.read().decode("utf-8")
        temp_data = json.loads(request)
        # print json data
        # print(pretty(data))
        # print("\npass: json retrieved")
        return temp_data
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print("Error:", e.code)
        if hasattr(e, "reason"):
            print("Reason:", e.reason)
        return None


paintings = {}
paintings_by_women = {}
image_rows = {}


@app.route('/')
def start():
    return render_template("template.html", form=True)

@app.route('/by-women')
def filter_paintings():
    # step 1: get list of paintings of women
    # step 2: get data for each painting and filter out non women artists
    params = {"medium": "Paintings", "q": "women"}
    param_str = urllib.parse.urlencode(params)
    url = met_url + "search" + "?" + param_str
    unfiltered = safe_get(url)


    # print(unfiltered["objectIDs"])
    # print(objectIDs_random)
    # print(pretty(unfiltered))
    # print("\npass: retrieved list of paintings of women\n")
    # print(pretty(image_rows))
    # print(pretty(paintings_by_women))
    # print(pretty(paintings))
    random_order = unfiltered["objectIDs"].copy()
    shuffle(random_order)

    size = int(request.args.get('size'))
    row_fill = 4
    row_num = 1
    range_end = randint(size, unfiltered["total"])
    range_start = range_end - size
    print(random_order)
    # print(size)
    # print(unfiltered["total"])
    print(range_end)
    print(range_start)

    for objectID in random_order[range_start:range_end]:
        req_url = met_url + "objects/" + str(objectID)
        # print(url)
        temp_data = safe_get(req_url)
        if temp_data["artistGender"] != "":
            paintings_by_women[objectID] = {}
            paintings_by_women[objectID]["title"] = paintings_by_women[objectID].get("title", temp_data["title"])
            paintings_by_women[objectID]["artist"] = paintings_by_women[objectID].get("artist",
                                                                                      temp_data["artistDisplayName"])
            paintings_by_women[objectID]["image"] = paintings_by_women[objectID].get("image", temp_data["primaryImage"])
            paintings_by_women[objectID]["link"] = paintings_by_women[objectID].get("link", temp_data["objectURL"])

        paintings[objectID] = {}
        paintings[objectID]["title"] = paintings[objectID].get("title", temp_data["title"])
        paintings[objectID]["artist"] = paintings[objectID].get("artist", temp_data["artistDisplayName"])
        paintings[objectID]["image"] = paintings[objectID].get("image", temp_data["primaryImage"])
        paintings[objectID]["link"] = paintings[objectID].get("link", temp_data["objectURL"])
        if row_fill == 4:
            image_rows[row_num] = image_rows.get(row_num, [paintings[objectID]])
            row_fill -= 1
        else:
            image_rows[row_num].append(paintings[objectID])
            row_fill -= 1
            if row_fill == 0:
                row_fill = 4
                row_num += 1
    return render_template("template.html", paintings=paintings, paintings_by_women=paintings_by_women,
                           image_rows=image_rows, num_by_women=len(paintings_by_women), form=False,
                           size=size, all_paintings=False)


@app.route('/all')
def all_paintings():
    size = request.args.get('size')
    return render_template("template.html", paintings=paintings, paintings_by_women=paintings_by_women,
                           image_rows=image_rows, num_by_women=len(paintings_by_women), form=False,
                           size=size, all_paintings=True)


if __name__ == "__main__":
    # Used when running locally only.
    # When deploying to Google AppEngine, a webserver process
    # will serve your app.
    app.run(host="localhost", port=8080, debug=True)
