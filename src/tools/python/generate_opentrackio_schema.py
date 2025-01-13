import sys
import json
import camdkit.model

if __name__ == "__main__":
  json_as_text = json.dumps(camdkit.model.Clip.make_json_schema(),
                            sort_keys=True,
                            indent=2)
  if len(sys.argv) == 2:
    with open(sys.argv[1], "w") as fp:
      print(json_as_text, file=fp)
  else:
    print(json_as_text)
